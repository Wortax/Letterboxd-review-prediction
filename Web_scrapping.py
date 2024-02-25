import urllib.request
import time
from bs4 import BeautifulSoup
import requests
from os.path  import basename
import sys
import json
import csv
import pandas as pd
import numpy as np
import seaborn as sns
import os

import PySimpleGUI as sg
from datetime import datetime

requests_session = requests.Session()


def Get_avgrate(jsonobj) :
    return jsonobj["aggregateRating"]["ratingValue"]

def Get_actors(jsonobj, n_act) :
    actors_list= []
    for i in jsonobj["actors"][0:n_act] :
        actors_list.append(i["name"])
    return actors_list

def Get_director(jsonobj) :
    return jsonobj["director"][0]["name"]

def Get_review_count(jsonobj) :
    return jsonobj["aggregateRating"]["reviewCount"]

def Get_realease_date(jsonobj) :
    return jsonobj["releasedEvent"][0]["startDate"]

def Get_genre(jsonobj) :
    return jsonobj["genre"]




def Get_urls_from_list(url):
    movie_url_list = []

    page = requests_session.get(url)
    soup = BeautifulSoup(page.content,features="lxml")

    page = requests_session.get(url)
    soup = BeautifulSoup(page.content,features="lxml")
    if len(soup.find_all("li", class_="poster-container"))>0:
        list_class = "poster-container"
    else :
        "poster-container numbered-list-item"


    try :
        n_pages= int(soup.find_all("li", class_="paginate-page")[-1].find("a").text)
    except :
        n_pages=1
        for a in soup.find_all("li", class_=list_class):
            movie_url_list.append("https://letterboxd.com"+a.find("div")["data-target-link"])
        return movie_url_list

    for i in range(1,n_pages+1):
        page = requests_session.get(url+"page/"+str(i)+"/")
        soup = BeautifulSoup(page.content,features="lxml")
        print(i,n_pages+1,"  ",len(soup.find_all("li", class_=list_class)))
        for a in soup.find_all("li", class_=list_class):
            movie_url_list.append("https://letterboxd.com"+a.find("div")["data-target-link"])
    return movie_url_list



def Get_allinfo(url,rate="") :
    tick = datetime.now()  
    page = requests_session.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    
    mydivs = str(soup.find('script', type='application/ld+json'))[52:-20]
    jsondiv = json.loads(mydivs)

    
    info_list = [jsondiv["name"]]
    try :
        actors = Get_actors(jsondiv, 2)
        genre = Get_genre(jsondiv)

        info_list.append(Get_avgrate(jsondiv))
        info_list.append(Get_director(jsondiv))
        info_list.append(Get_review_count(jsondiv))
        info_list.append(Get_realease_date(jsondiv))
        
        info_list.append(actors[0])
        info_list.append(actors[1])
        
        info_list.append(genre[0])
        if len(genre)>1 :
            info_list.append(genre[1])
        else :
            info_list.append("")

        if len(rate)>0:
            info_list.append(rate)
    except :
        print("Error for",jsondiv["name"])
        return []

    return info_list


def Create_dataset(rate_file,outfile_data): 
    dataset = [["Title","Average_Rating","Director","Number_reviews","Release_Date","Actor1","Actor2","Genre1","Genre2","Own_Rate"]]
    with open(rate_file, 'r') as file:
          csvreader = csv.reader(file)
          a=True
          length = len(pd.read_csv(rate_file))
          compt=0
          for i in csvreader:
              if a :
                  a=False
                  continue
              if not sg.one_line_progress_meter('Progress Meter', compt+1, length, 'Training dataset Creation :') and compt+1 != length:
                 return 0
              dataset.append(Get_allinfo(i[-2],i[-1]))
              compt+=1
          file.close()
          
        
    with open(outfile_data, 'w', newline='') as outfile:
         writer = csv.writer(outfile)
         for i in dataset :
             if len(i)==0 :
                 continue
             try :
                 writer.writerow(i)
             except :
                print("Error with:",i)
    return 1
    outfile.close()

def Create_predict_dataset(output_file,movie_list):
    dataset = [["Title","Average_Rating","Director","Number_reviews","Release_Date","Actor1","Actor2","Genre1","Genre2"]]
    for i in range(0,len(movie_list)) :
        dataset.append(Get_allinfo(movie_list[i]))
        if not sg.one_line_progress_meter('Progress Meter', i+1, len(movie_list), 'List Dataset Creation :') and i+1 != len(movie_list):
            return 0
             
    with open(output_file, 'w', newline='') as outfile:
         writer = csv.writer(outfile)
         for i in dataset :
             if len(i)==0 :
                 continue

             try :
                 writer.writerow(i)
             except :
                print("Error with:",i)
    outfile.close()
    return 1
