from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from urllib.request import urlopen as uReq
import logging
import pymongo
import os
import shutil
import re
import csv
import sys
import pandas as pd

BASE_DIR = os.getcwd()
logging.basicConfig(filename=os.path.join(BASE_DIR, "scrapper.log") , level=logging.INFO)


app = Flask(__name__)

print("Youtube Scrap")
@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            query = request.form['content'].replace(" ","")
            # fake user agent to avoid getting blocked by Google
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"}

            # fetch the search results page
            response = requests.get(f"{query}", headers=headers)
            res = response.text

            # Video
            videoids = re.findall('"videoRenderer":{"videoId":".*?"', res)
            # thumbnail
            thumbnails = re.findall('"thumbnail":{"thumbnails":\[{"url":".*?"', res)
            # Title
            titles = re.findall('"title":{"runs":\[{"text":".*?"', res)
            # Views
            views = re.findall('"shortViewCountText":{"accessibility":{"accessibilityData":{"label":".*?"', res)
            # Published Time
            published_time = re.findall('"publishedTimeText":{"simpleText":".*?"', res)
            
            header_list = ['S No', 'Video url', 'Thumbnail', 'Title', 'Views', 'Published Time']
            report_list = []
            for i in range(5):
                temp = []
                temp.append(i+1)
                temp.append('https://www.youtube.com/watch?v=' + videoids[i].split('"')[-2])
                temp.append(thumbnails[i].split('"')[-2])
                temp.append(titles[i].split('"')[-2])
                temp.append(views[i].split('"')[-2])
                temp.append(published_time[i].split('"')[-2])
                report_list.append(temp)
            file_name = os.path.join(BASE_DIR, 'sample_csv.csv')
            df = pd.DataFrame(report_list,columns=header_list)
            df.to_csv(file_name,index=False)
            return render_template('results.html', report_list=report_list, channel=query)
            # return "Success"
        except Exception as e:
            logging.info(e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            print(exc_type, exc_obj, exc_tb)
            return 'something is wrong'
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run(host='localhost', port=8000, debug=True)