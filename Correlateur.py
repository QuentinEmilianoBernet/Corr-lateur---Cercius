# coding=utf-8

from flask import Flask, flash, render_template, request, redirect, url_for, send_from_directory
import os
import pandas as pd
from string import Template
import re
import numpy as np
from werkzeug.utils import secure_filename
import io
import urllib.request
import requests
import time

#dtf = pd.read_csv(r"C:\Users\quent\Documents\images_custom6.csv", dtype={"conservation_institution":"str","contributor":"str", "extent":"str", "ornamental_motif":"str", "incipit":"str"}, encoding='utf-8')
dtf = pd.read_csv(r"Data.csv", encoding='utf-8')


#dtf = dtf.loc[dtf["place_type"]!="Localisation_inconnue"]
dtf = dtf.loc[dtf["Object ID"]!="False"]
dtf = dtf.loc[dtf["Object ID"]!=False]

dtf = dtf.loc[dtf["Object ID"]!="None"]
dtf = dtf.loc[dtf["Object ID"]!=None]

#dtf = dtf[:59591]
 
donnees = []

def geoloc(lieu, i) :
    print(lieu)
    lieu = str(lieu).replace("ca.","").replace("active by ","").replace("active ","").replace("Probably ","").replace("probably ","").replace("Possibly ","").replace("possibly ","").replace("near ","").replace("|",",")
    lat = i["lat"]
    lon = i["lon"]

    for i in lieu.strip(","):
      lieu = i
      regex = re.compile(r'\w+\s{1}\d{4}-\d{4}')
      if regex.search(lieu) is not None :
          print("trouvé")
          adresse=lieu.strip(" ")[0]
          dates = lieu.strip(" ")[1]
          url = "https://geocode.maps.co/search?q={"+str(adresse)+"}"
          paramss = {
              'action': 'wbsearchentities',
              'language':'fr',
                  'uselang':'fr',
                  'format':'json',
                  'search':url,
              }
          
          data = requests.get(url,params=paramss)
          time.sleep(0.75)
          if data.status_code == 200 and data.json() != []:
              if len(data.json()) >= 1 :
                  lat = data.json()[0]["lat"]
                  lon = data.json()[0]["lon"]
                  name = list(str(data.json()[0]["display_name"]).split(","))
                  if len(name)>1:
                      région = name[1].strip()
                      i["place"]=name[0].strip()
                      i["place_type"]=région.strip()
                  
                  if len(data.json()) >= 3 :
                      if len(name)>3:
                          if data.json()[0]["type"]=="village" :
                              région = name[3]
                              i["place"]=name[0]
                              i["place_type"]=région

                          elif data.json()[2]["type"]=="village" :
                              région = name[3]
                              i["place"]=name[0]
                              i["place_type"]=région
                  else :
                      i["place_type"]=name[len(name)-1].strip()
                  
                  if i["place"]=="Paris":
                      i["place_type"]=="Île-de-France"
                  i["lat"]=lat
                  i["lon"]=lon
              
              else :
                  print(lieu, data.json())
                  lat = data.json()["lat"]
                  lon = data.json()["lon"]
                  name = list(str(data.json()["display_name"]).split(","))
                  if len(name)>1:
                      région = name[1].strip()
                      i["place"]=name[0].strip()
                      i["place_type"]=région.strip()

                  else :
                      i["place_type"]=name[len(name)-1].strip()
                  
                  if i["place"]=="Paris":
                      i["place_type"]=="Île-de-France"
                  i["lat"]=lat
                  i["lon"]=lon

          if str(lieu).replace("?","") == "France" :
              i["place"] = "France"
              i["lat"] = 46
              i["lon"] = 2

          i["date_deb"]=dates.split("-")[0]
          i["date_fin"]=dates.split("-")[1]
          donnees.append(i)
          return print(i["place"])

def imagefrom_tif(img) :
    url = img

    if not re.search("127", url) :
      return url_for('serve_images', filename=str(url).replace(".","_").replace("/","").replace(":","_").replace("_jpg","")+'.jpg')
    
    else :
      return url
    
def imagefrom_tif2(img) :
    url = img

    if not re.search("127", url) :
      return url_for('serve_images', filename=str(url).replace(".","_").replace("/","").replace(":","_").replace("_jpg","")+'.jpg')
    
    else :
      return url

print("Chargement des données...")

for i in range(len(dtf)) :
    descri=[]
    medium=[]
    
    def descripteurs(o):
        o=str(o)
        if o != "False" :
            if o is not False :
                o = o.replace("[","")
                o = o.replace("]","")
                o = o.replace("'","")
                o = o.replace('"','')
                
                o = list(o.split(','))
                for e in o :
                    pattern = r"^\s"
                    pattern2 = r"^saint\S+"
                    match = re.search(pattern,str(e))
                    if match :
                        e = e.replace(" ","")
                    match = re.search(pattern2,e)
                    if match :
                        e = e.replace("saint","saint ")
                    descri.append(e)
            
    descri = list(set(dtf["Tags"][i].split("|")))
    descri = descri.sort()

    medium = list(set(medium))
    medium = medium.sort()


    if dtf["lat"][i] != "False" :
      #if dtf.at[i, "medium"]==dtf.at[i-1, "medium"] or any(dtf.at[i, "related_dataset_id"]) is False :
        u = {
    "id":(str(dtf["Object ID"][i]).replace(" ","_")).replace(".","_"),
    "lat":float(dtf["lat"][i]),
    "lon":float(dtf["lon"][i]),
    "contributor":((dtf["Artist Display Name"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
    "title":dtf["Title"][i].replace("False","Sans titre").replace("'","ʼ"),
    "place":dtf["place"][i].strip().replace("False","provenance inconnue"),
    "région":dtf["place_type"][i],
    "date":dtf["Object Date"][i].replace("False","date inconnue"),
    "date_deb":int(dtf["Object Begin Date"][i]),
    "date_fin":int(dtf["Object End Date"][i]),
    "descripteurs":sorted(dtf["Tags"][i].split("|")),
    "medium":sorted(dtf["Medium"][i].replace("'","ʼ").split(",")),
    "label":str(dtf["Object ID"][i])+", "+str(dtf["Medium"][i])+", par "+((dtf["Artist Display Name"][i].replace("|",", "))).replace("False","créateur inconnu")+", "+dtf["place"][i]+", "+dtf["Object Date"][i].replace("False","date inconnue")+".",
    "Quotient":"",
    "index":int(i),
    "files":dtf.at[i, "image"],
    "link":str(dtf.at[i, "Link Resource"]).replace("http","https")
    }
        donnees.append(u)

    else :
      if str(dtf["place"][i]) != "False" :
        #if dtf.at[i, "medium"]==dtf.at[i-1, "medium"] or any(dtf.at[i, "related_dataset_id"]) is False :
          u = {
      "id":(str(dtf["Object ID"][i]).replace(" ","_")).replace(".","_"),
      "lat":dtf["lat"][i],
      "lon":dtf["lon"][i],
      "contributor":((dtf["Artist Display Name"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
      "title":dtf["Title"][i].replace("False","Sans titre").replace("'","ʼ"),
      "place":dtf["place"][i].strip().replace("False","provenance inconnue"),
      "région":dtf["place_type"][i],
      "date":dtf["Object Date"][i].replace("False","date inconnue"),
      "date_deb":int(dtf["Object Begin Date"][i]),
      "date_fin":int(dtf["Object End Date"][i]),
      "descripteurs":sorted(dtf["Tags"][i].split("|")),
      "medium":sorted(dtf["Medium"][i].replace("'","ʼ").split(",")),
      "label":str(dtf["Object ID"][i])+", "+str(dtf["Medium"][i])+", par "+((dtf["Artist Display Name"][i].replace("|",", "))).replace("False","créateur inconnu")+", "+dtf["place"][i]+", "+dtf["Object Date"][i].replace("False","date inconnue")+".",
      "Quotient":"",
      "index":int(i),
      "files":dtf.at[i, "image"],
      "link":str(dtf.at[i, "Link Resource"]).replace("http","https")
      }
          donnees.append(u)

      #if dtf.at[i, "medium"]==dtf.at[i-1, "medium"] or any(dtf.at[i, "related_dataset_id"]) is False :
      elif str(dtf["City"][i]) != "False" :
          u = {
      "id":(str(dtf["Object ID"][i]).replace(" ","_")).replace(".","_"),
      "lat":dtf["lat"][i],
      "lon":dtf["lon"][i],
      "contributor":((dtf["Artist Display Name"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
      "title":dtf["Title"][i].replace("False","Sans titre").replace("'","ʼ"),
      "place":dtf["City"][i].replace("False","provenance inconnue"),
      "région":dtf["place_type"][i],
      "date":dtf["Object Date"][i].replace("False","date inconnue"),
      "date_deb":int(dtf["Object Begin Date"][i]),
      "date_fin":int(dtf["Object End Date"][i]),
      "descripteurs":sorted(dtf["Tags"][i].split("|")),
      "medium":sorted(dtf["Medium"][i].replace("'","ʼ").split(",")),
      "label":str(dtf["Object ID"][i])+", "+str(dtf["Medium"][i])+", par "+((dtf["Artist Display Name"][i].replace("|",", "))).replace("False","créateur inconnu")+", "+dtf["place"][i].replace("False","origine inconnue")+", "+dtf["Object Date"][i].replace("False","date inconnue")+".",
      "Quotient":"",
      "index":int(i),
      "files":dtf.at[i, "image"],
      "Country":str(dtf.at[i, "Country"]),
      "State":str(dtf.at[i, "State"]),
      "Region":str(dtf.at[i,"Region"]),
      "link":str(dtf.at[i, "Link Resource"]).replace("http","https")
      }
          
      elif str(dtf["State"][i]) != "False" :
          u = {
      "id":(str(dtf["Object ID"][i]).replace(" ","_")).replace(".","_"),
      "lat":dtf["lat"][i],
      "lon":dtf["lon"][i],
      "contributor":((dtf["Artist Display Name"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
      "title":dtf["Title"][i].replace("False","Sans titre").replace("'","ʼ"),
      "place":dtf["State"][i].replace("False","provenance inconnue"),
      "région":dtf["place_type"][i],
      "date":dtf["Object Date"][i].replace("False","date inconnue"),
      "date_deb":int(dtf["Object Begin Date"][i]),
      "date_fin":int(dtf["Object End Date"][i]),
      "descripteurs":sorted(dtf["Tags"][i].split("|")),
      "medium":sorted(dtf["Medium"][i].replace("'","ʼ").split(",")),
      "label":str(dtf["Object ID"][i])+", "+str(dtf["Medium"][i])+", par "+((dtf["Artist Display Name"][i].replace("|",", "))).replace("False","créateur inconnu")+", "+dtf["place"][i].replace("False","origine inconnue")+", "+dtf["Object Date"][i].replace("False","date inconnue")+".",
      "Quotient":"",
      "index":int(i),
      "files":dtf.at[i, "image"],
      "Country":str(dtf.at[i, "Country"]),
      "State":str(dtf.at[i, "State"]),
      "Region":str(dtf.at[i,"Region"]),
      "link":str(dtf.at[i, "Link Resource"]).replace("http","https")
      }
          
      elif str(dtf["County"][i]) != "False" :
          u = {
      "id":(str(dtf["Object ID"][i]).replace(" ","_")).replace(".","_"),
      "lat":dtf["lat"][i],
      "lon":dtf["lon"][i],
      "contributor":((dtf["Artist Display Name"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
      "title":dtf["Title"][i].replace("False","Sans titre").replace("'","ʼ"),
      "place":dtf["County"][i].replace("False","provenance inconnue"),
      "région":dtf["place_type"][i],
      "date":dtf["Object Date"][i].replace("False","date inconnue"),
      "date_deb":int(dtf["Object Begin Date"][i]),
      "date_fin":int(dtf["Object End Date"][i]),
      "descripteurs":sorted(dtf["Tags"][i].split("|")),
      "medium":sorted(dtf["Medium"][i].replace("'","ʼ").split(",")),
      "label":str(dtf["Object ID"][i])+", "+str(dtf["Medium"][i])+", par "+((dtf["Artist Display Name"][i].replace("|",", "))).replace("False","créateur inconnu")+", "+dtf["place"][i].replace("False","origine inconnue")+", "+dtf["Object Date"][i].replace("False","date inconnue")+".",
      "Quotient":"",
      "index":int(i),
      "files":dtf.at[i, "image"],
      "Country":str(dtf.at[i, "Country"]),
      "State":str(dtf.at[i, "State"]),
      "Region":str(dtf.at[i,"Region"]),
      "link":str(dtf.at[i, "Link Resource"]).replace("http","https")
      }
          
      elif str(dtf["Country"][i]) != "False" :
          u = {
      "id":(str(dtf["Object ID"][i]).replace(" ","_")).replace(".","_"),
      "lat":dtf["lat"][i],
      "lon":dtf["lon"][i],
      "contributor":((dtf["Artist Display Name"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
      "title":dtf["Title"][i].replace("False","Sans titre").replace("'","ʼ"),
      "place":dtf["Country"][i].strip().replace("False","provenance inconnue"),
      "région":dtf["place_type"][i],
      "date":dtf["Object Date"][i].replace("False","date inconnue"),
      "date_deb":int(dtf["Object Begin Date"][i]),
      "date_fin":int(dtf["Object End Date"][i]),
      "descripteurs":sorted(dtf["Tags"][i].split("|")),
      "medium":sorted(dtf["Medium"][i].replace("'","ʼ").split(",")),
      "label":str(dtf["Object ID"][i])+", "+str(dtf["Medium"][i])+", par "+((dtf["Artist Display Name"][i].replace("|",", "))).replace("False","créateur inconnu")+", "+dtf["place"][i].replace("False","origine inconnue")+", "+dtf["Object Date"][i].replace("False","date inconnue")+".",
      "Quotient":"",
      "index":int(i),
      "files":dtf.at[i, "image"],
      "Country":str(dtf.at[i, "Country"]),
      "State":str(dtf.at[i, "State"]),
      "Region":str(dtf.at[i,"Region"]),
      "link":str(dtf.at[i, "Link Resource"]).replace("http","https")
      }
          
      elif str(dtf["Region"][i]) != "False" :
          u = {
      "id":(str(dtf["Object ID"][i]).replace(" ","_")).replace(".","_"),
      "lat":dtf["lat"][i],
      "lon":dtf["lon"][i],
      "contributor":((dtf["Artist Display Name"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
      "title":dtf["Title"][i].replace("False","Sans titre").replace("'","ʼ"),
      "place":dtf["Region"][i].replace("False","provenance inconnue"),
      "région":dtf["place_type"][i],
      "date":dtf["Object Date"][i].replace("False","date inconnue"),
      "date_deb":int(dtf["Object Begin Date"][i]),
      "date_fin":int(dtf["Object End Date"][i]),
      "descripteurs":sorted(dtf["Tags"][i].split("|")),
      "medium":sorted(dtf["Medium"][i].replace("'","ʼ").split(",")),
      "label":str(dtf["Object ID"][i])+", "+str(dtf["Medium"][i])+", par "+((dtf["Artist Display Name"][i].replace("|",", "))).replace("False","créateur inconnu")+", "+dtf["place"][i].replace("False","origine inconnue")+", "+dtf["Object Date"][i].replace("False","date inconnue")+".",
      "Quotient":"",
      "index":int(i),
      "files":dtf.at[i, "image"],
      "Country":str(dtf.at[i, "Country"]),
      "State":str(dtf.at[i, "State"]),
      "Region":str(dtf.at[i,"Region"]),
      "link":str(dtf.at[i, "Link Resource"]).replace("http","https")
      }
          
      else :
          u = {
      "id":(str(dtf["Object ID"][i]).replace(" ","_")).replace(".","_"),
      "lat":dtf["lat"][i],
      "lon":dtf["lon"][i],
      "contributor":((dtf["Artist Display Name"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
      "title":dtf["Title"][i].replace("False","Sans titre").replace("'","ʼ"),
      "place":"provenance inconnue",
      "région":dtf["place_type"][i],
      "date":dtf["Object Date"][i].replace("False","date inconnue"),
      "date_deb":int(dtf["Object Begin Date"][i]),
      "date_fin":int(dtf["Object End Date"][i]),
      "descripteurs":sorted(dtf["Tags"][i].split("|")),
      "medium":sorted(dtf["Medium"][i].replace("'","ʼ").split(",")),
      "label":str(dtf["Object ID"][i])+", "+str(dtf["Medium"][i])+", par "+((dtf["Artist Display Name"][i].replace("|",", "))).replace("False","créateur inconnu")+", "+dtf["place"][i].replace("False","origine inconnue")+", "+dtf["Object Date"][i].replace("False","date inconnue")+".",
      "Quotient":"",
      "index":int(i),
      "files":dtf.at[i, "image"],
      "Country":str(dtf.at[i, "Country"]),
      "State":str(dtf.at[i, "State"]),
      "Region":str(dtf.at[i,"Region"]),
      "link":str(dtf.at[i, "Link Resource"]).replace("http","https")
      }
          #if str(dtf["Artist Display Bio"][i]) != "False" or not re.search(" |",str(dtf["Artist Display Bio"][i])) :
              #geoloc(dtf["Artist Display Bio"][i],u)
      
      donnees.append(u)

print (len(donnees))
t = len(dtf)

def carto(correlations) :
    carto_dict = []

    for i in correlations :
        e = i["région"]
        u = i["lon"]
        if e != "Localisation inconnue" or e == "Catalunya" :
            if u != "False" and i["date_deb"]!=0:
                carto_dict.append(i)

    script='''
    $(function () {
    $("#map").tooltip({
      track: true,
    });
    $("#map").mouseover(function () {
      $("#map").tooltip("disable");
    });
  });
  
    
            
    var blur2 = L.icon({
            iconUrl: 'https://datavirgo.huma-num.fr/blur_copie.png',
            iconSize: [100, 100],
            iconAnchor: [50, 50]
            });

    var map = L.map('map', {
    zoom: 5,
    center : [43.950001, 4.81667]});

    L.tileLayer(
            "https://api.mapbox.com/styles/v1/quentinbernet/cla6lh9e1000714mt0kv7e87z/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoicXVlbnRpbmJlcm5ldCIsImEiOiJja3ltenMxb2MwN2s3MnBuOXM4cGJma3d5In0.fPSmSgvw8iuMJ7eXobdtAw",
            {"attribution": "Quentin Bernet, 2023."}
        ).addTo(map);
        
        L.control.scale().addTo(map)
        
        // Create additional Control placeholders
        function addControlPlaceholders(map) {
            var corners = map._controlCorners,
                l = 'leaflet-',
                container = map._controlContainer;

            function createCorner(vSide, hSide) {
                var className = l + vSide + ' ' + l + hSide;

                corners[vSide + hSide] = L.DomUtil.create('div', className, container);
            }

            createCorner('verticalcenter', 'right');
        }
        addControlPlaceholders(map);

        var points ='''+str(carto_dict)+'''
        var  heat_points = []

        points.sort((a, b) => {
            return a.date_deb - b.date_deb;
        });

        var date_deb = parseInt(points[0].date_deb);

        points.sort((a, b) => {
            return b.date_fin - a.date_fin;
        });

        var date_fin = parseInt(points[0].date_fin);

        for(i in points) {
        var lat = points[i].lat,	
            lon = points[i].lon,
            label = points[i].label
            descri = points[i].descripteurs
            artiste = (points[i].contributor).split("|")
            ville = (points[i].place).split(",");

        heat_points.push([lat,lon,0.20 ])};

        var heat = L.heatLayer(heat_points, {gradient:{0.2:'#363083', 0.4:'#5F6DEF', 0.45:'#9C83DE', 0.6:'lavender', 0.7:'beige', 0.9: 'blanchedalmond'}, "blur": 27, "minOpacity": 0.5, "radius": 25}).addTo(map);
       
        var slider = document.getElementById('slider');
        
        
           noUiSlider.create(slider, {
                start: [date_deb,date_fin],
                color: 'midnightblue',
                behaviour:'drag-slide',
                connect: true,
                tooltips: [wNumb({decimals:0}),wNumb({decimals:0})],
                step:5,
                range: {
                    'min': date_deb,
                    'max': date_fin,
                }
            }).on('slide', function(e) {
              console.log(e)

              heat_points = []
              
              for (i in points) {

              if(points[i].date_deb>=parseFloat(e[0])&&points[i].date_fin<=parseFloat(e[1])) {
                  heat_points.push([points[i].lat,points[i].lon,0.3]);}
              }
              heat.setLatLngs(heat_points);
            
            
            });
                
                '''

    return script

def carto_correlations(correlations, input) :

    correlations = []
    for i in donnees :
        if input == i["id"]:
            obj = i


    for y in donnees :

                a=0
                m=0
                if obj["id"]!=y["id"] :
                    quotient_list = 0

                    if str(y["contributor"]) != "Créateur inconnu" and str(obj["contributor"])!="Créateur inconnu":
                      for d in list(obj["contributor"].split(",")) :
                        for dd in list(y["contributor"].split(",")) :
                          if d==dd :
                            a-=3

                    if str(y["medium"]) != "False" and str(obj["medium"])!="False":
                      for d in obj["medium"] :
                        for dd in y["medium"] :
                          if d==dd :
                            a+=2.5
                            m+=1.1

                    if  str(obj["place"])==str(y["place"]) and obj["place"] != "provenance inconnue":
                            a+=4
                    if  str(obj["région"])==str(y["région"]) and obj["région"] != "False":
                            a+=5
  
                    

                    for d in obj["descripteurs"] :
                      for dd in y["descripteurs"] :
                        if d==dd and m>0 :
                          quotient_list+=4*m
                        elif d==dd :
                          quotient_list+=4

                    limite=(len(obj["descripteurs"])+len(y["descripteurs"]))/2

                    quotient_list=(quotient_list/limite)*50
                    
                    a+=quotient_list*0.9

                    

                    if y["id"] is not False :

                        if int(obj["date_deb"])==int(y["date_deb"]) :
                                y["Quotient"]=float(a+2)
                                correlations.append(y)


                        elif int(obj["date_deb"])<int(y["date_deb"]) :
                            if int(y["date_deb"])-int(obj["date_deb"]) <= 150 :
                                y["Quotient"]=float(a-(int(y["date_deb"])-int(obj["date_deb"]))*0.7)
                                correlations.append(y)


                        elif int(y["date_deb"])<int(obj["date_deb"]) :
                            if int(obj["date_deb"])-int(y["date_deb"]) <= 150 :
                                y["Quotient"]=float(a-(int(obj["date_deb"])-int(y["date_deb"]))*0.7)
                                correlations.append(y)

                
    a=0
    m=0
        
    correlations.sort(key=lambda x:x["Quotient"], reverse = True)

    if len(correlations) > 300 :
        correlations=correlations[:300]

    for i in donnees :
      if i["id"] == input :
        input = i

    carto_dict = []

    for i in correlations:
        if i["région"] != "Localisation inconnue" :
            if i["lon"] != "False" and i["date_deb"]!=0 and obj["date_deb"]!=0:
                carto_dict.append(i)
            elif obj["date_deb"]==0 and i["lon"] != "False" :
                carto_dict.append(i)

    script='''
    $(function () {
    $("#map").tooltip({
      track: true,
    });
    $("#map").mouseover(function () {
      $("#map").tooltip("disable");
    });
  });
  
    
            
            var blur2 = L.icon({
                iconUrl: 'https://datavirgo.huma-num.fr/blur_copie.png',
                iconSize: [100, 100],
                iconAnchor: [50, 50]
            });

    if ("'''+str(obj["lat"])+'''" == "False" || "'''+str(obj["lon"])+'''" == "False" ) {
      var center_lat = 43.950001 ; var center_lon = 4.81667;}

    else {
      var center_lat = '''+str(obj["lat"])+''' ; var center_lon = '''+str(obj["lon"])+''';}

    var map = L.map('map', {
    zoom: 6,
    center : [center_lat, center_lon]});

    L.tileLayer(
            "https://api.mapbox.com/styles/v1/quentinbernet/cla6lh9e1000714mt0kv7e87z/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoicXVlbnRpbmJlcm5ldCIsImEiOiJja3ltenMxb2MwN2s3MnBuOXM4cGJma3d5In0.fPSmSgvw8iuMJ7eXobdtAw",
            {"attribution": "Quentin Bernet, 2023."}
        ).addTo(map);
        
        L.control.scale().addTo(map)
        
        // Create additional Control placeholders
        function addControlPlaceholders(map) {
            var corners = map._controlCorners,
                l = 'leaflet-',
                container = map._controlContainer;

            function createCorner(vSide, hSide) {
                var className = l + vSide + ' ' + l + hSide;

                corners[vSide + hSide] = L.DomUtil.create('div', className, container);
            }

            createCorner('verticalcenter', 'right');
        }
        addControlPlaceholders(map);

        var points ='''+str(carto_dict)+'''
        var  heat_points = []

        if (points.length!=0) {
        points.sort((a, b) => {
            return a.date_deb - b.date_deb;
        });
        var date_deb = parseInt(points[0].date_deb);

        points.sort((a, b) => {
            return b.date_fin - a.date_fin;
        });

        var date_fin = parseInt(points[0].date_fin);}

        else {var date_deb = 0;var date_fin=1}

        for(i in points) {
        var lat = points[i].lat,	
            lon = points[i].lon,
            label = points[i].label
            descri = points[i].descripteurs
            artiste = (points[i].contributor).split("|")
            ville = (points[i].place).split(",");


        heat_points.push([lat,lon,0.30 ])};

        var heat = L.heatLayer(heat_points, {gradient:{0.2:'#363083', 0.4:'#5F6DEF', 0.45:'#9C83DE', 0.6:'lavender', 0.7:'beige', 0.9: 'blanchedalmond'}, "blur": 27, "minOpacity": 0.5, "radius": 25}).addTo(map);
       
        if ("'''+str(input["lat"])+'''"!="False"){
        var circle = new L.circleMarker (['''+str(input["lat"])+","+str(input["lon"])+'''], {label:label, icon:blur2, opacity: 0.9, weight: 1.8, radius:10, fillColor:'none', color:'blanchedalmond'});
            circle.addTo(map);}
      
        var slider = document.getElementById('slider');
        
        
           noUiSlider.create(slider, {
                start: [date_deb,date_fin],
                color: 'midnightblue',
                behaviour:'drag-slide',
                connect: true,
                tooltips: [wNumb({decimals:0}),wNumb({decimals:0})],
                step:5,
                range: {
                    'min': date_deb,
                    'max': date_fin,
                }
            }).on('slide', function(e) {
              console.log(e)

              heat_points = []
              
              for (i in points) {

              if(points[i].date_deb>=parseFloat(e[0])&&points[i].date_fin<=parseFloat(e[1])) {
                  heat_points.push([points[i].lat,points[i].lon,0.3]);}
              }
              heat.setLatLngs(heat_points);
            
            
            });
        
        '''



    return script


def correlateur(donnees,input) :

    correlations = []
    for i in donnees :
        if input == i["id"]:
            obj = i


    for y in donnees :

                a=0
                m=0
                if obj["id"]!=y["id"] :
                    quotient_list = 0
                

                    if str(y["contributor"]) != "Créateur inconnu" and str(obj["contributor"])!="Créateur inconnu":
                      for d in list(obj["contributor"].split(",")) :
                        for dd in list(y["contributor"].split(",")) :
                          if d==dd :
                            a-=3
                  

                    if str(y["medium"]) != "False" and str(obj["medium"])!="False":
                      for d in obj["medium"] :
                        for dd in y["medium"] :
                          if d==dd :
                            a+=2.5
                            m+=1.1

                    if  str(obj["place"])==str(y["place"]) and obj["place"] != "provenance inconnue":
                            a+=4
                    if  str(obj["région"])==str(y["région"]) and obj["région"] != "False":
                            a+=5
  
                    

                    for d in obj["descripteurs"] :
                      for dd in y["descripteurs"] :
                        if d==dd and m>0 :
                          quotient_list+=4*m
                        elif d==dd :
                          quotient_list+=4

                    limite=(len(obj["descripteurs"])+len(y["descripteurs"]))/2

                    quotient_list=(quotient_list/limite)*50
                    
                    a+=quotient_list*0.9


                    if y["id"] is not False :

                        if len(obj["descripteurs"])==len(y["descripteurs"]):
                            y["Quotient"]=float(a+50)
                        if len(obj["descripteurs"])>len(y["descripteurs"]) and len(obj["descripteurs"])-len(y["descripteurs"])<=2:
                            y["Quotient"]=float(a+35)
                        if len(y["descripteurs"])>len(obj["descripteurs"]) and len(y["descripteurs"])-len(obj["descripteurs"])<=2:
                            y["Quotient"]=float(a+35)


                        if int(obj["date_deb"])==int(y["date_deb"]) :
                                y["Quotient"]=float(a+2)
                                correlations.append(y)


                        elif int(obj["date_deb"])<int(y["date_deb"]) :
                            if int(y["date_deb"])-int(obj["date_deb"]) <= 150 :
                                y["Quotient"]=float(a-(int(y["date_deb"])-int(obj["date_deb"]))*0.07)
                                correlations.append(y)


                        elif int(y["date_deb"])<int(obj["date_deb"]) :
                            if int(obj["date_deb"])-int(y["date_deb"]) <= 150 :
                                y["Quotient"]=float(a-(int(obj["date_deb"])-int(y["date_deb"]))*0.07)
                                correlations.append(y)


                        #print(y["Quotient"], end=", ")

    a=0
    m=0
    correlations.sort(key=lambda x:x["Quotient"], reverse = True)

    if len(correlations) > 200 :
        correlations=correlations[:200]

    print(correlations)

    #url = str(img[x])
    
    def imprime() :
        correlations.sort(key=lambda x:x["Quotient"], reverse = True)
        liste_descripteurs = ""

        for i in obj["descripteurs"] :
          liste_descripteurs+="- "+i+"\n\n"

        if obj["id"] is not False :

            a = '<div id="resultat"><div id="map"></div><div id="resultat1"><div id="carrousel_prime"><a href="'+str(obj["link"])+'"> <img width="auto" height="300vh" src="'+imagefrom_tif(obj["files"])+'"/></a><br></div><br><br>'
            a += "Vous avez choisi "+str(obj["title"])+ " ("+str(obj["id"])+"), "+str(obj["medium"])+", "+" par "+str(obj["contributor"]).replace("|",", ")+", "+str(obj["date"])+', '+str(obj["place"]).replace("False", "origine exacte inconnue")+'.\n\n'+'descripteurs :\n\n'+str(liste_descripteurs)+'</div><div id="netgraph"><div id="loadingScreen">Chargement...</div><div id="mynetwork"></div></div></div><br><br>'
        
        else :
            a = '<div id="resultat"><div id="map"></div><div id="resultat1">'
            a += 'Vous avez choisi '+str(obj["title"])+ " ("+str(obj["id"])+"), "+str(obj["medium"])+", "+' par '+str(obj["contributor"]).replace("|",", ")+', '+str(obj["date"])+' (Pas de reproduction), '+str(obj["place"]).replace("False", "origine exacte inconnue")+'.\n\n'+'descripteurs :\n\n'+str(liste_descripteurs)+'</div><div id="netgraph"><div id="loadingScreen">Chargement...</div><div id="mynetwork"></div></div></div><br><br>'
        z = -1
        if len(correlations)<= 120 :
            longueur = len(correlations)
        else :
            longueur = 120
        a += '<div id="resultats">'
        for i in range(longueur) :
            z+=1

            if i % 4 == 0 and i!=0:
                    a+='</div><br><div id="resultats">'
            a += '<a id="compart" href="http://127.0.0.1:5000/item_'+correlations[z]["id"]+'"> <div id="carrousel"><img width="auto" height="300vh" src="'+imagefrom_tif(correlations[z]["files"])+'"/><br></div><br><div id="cartel"> Proche de '+correlations[z]["title"]+", "+correlations[z]["label"]+"</div></a><br>"+'''
    '''
            #if z == 5 or z == 10 or z == 15 or z == 20:
            #    a += '</div><br><div id="resultats">'
        a += "</div>"
        return a
    b = imprime()

    def resultat () :
        if correlations != [] :
            return b
        else :
            return "<div id='resultat'>Pas de correlations pour cette oeuvre.</div>"

    return resultat()

def clean_data(param) :
        param=str(param)
        param=param.replace("Attribué à ","")
        param=param.replace(" ?","")
        param=param.replace("?","")
        param=param.replace("-"," ")
        param=param.replace("Î","I")
        param=param.replace(" (environs)","")
        return param

def netgraph(correlations) :

    texte = str(clean_data(request.form["input"]))

    input = clean_data(texte)

    script='''

<script type="text/javascript">


const input = "'''+input+'''"
'''

    graph_dict = []

    for i in correlations:
                i["files"]=imagefrom_tif2(i["files"])
                graph_dict.append(i)

    villes=[]
    artistes=[]

    for valeur in graph_dict:
        if valeur['place'] != "False" :
            for i in valeur['place'].split(",") :
                villes.append(i.strip())

        if valeur["contributor"] != "Créateur inconnu":
            for i in valeur['contributor'].split("|") :
                artistes.append(i)


    villes_uniques = list(set(villes))
    Artistes_uniques = list(set(artistes))
    #descripteurs = set(itertools.chain.from_iterable(descripteurs))


    script+='''
    const edges = new vis.DataSet();
    const nodes = new vis.DataSet();
    var points='''+str(graph_dict)+'''

    const data = {
    nodes: nodes,
    edges: edges
    };

    False = "provenance exacte inconnue"


  var container = document.getElementById("mynetwork");
  
  const options = {
    physics:{enabled:false},
    nodes: {
      shape: "dot",
      scaling: {
        min: 7,
        max: 30,
      },
      font: {
        size: 7,
        face: "Quicksand",
        color: "beige",
      },
    },
    edges: {
      color:{highlight:'white'},
      width: 0.20,
      length:5,
      smooth: {
          enabled:true,
          roundness:0.75,
          type:"dynamic",
          },
    },
    interaction: {
    hover:true,
    tooltipDelay:0.2,
    }
  };

for (i in points) {

        var lat = points[i].lat	//position found
            lon = points[i].lon
            label = points[i].label
            title = points[i].title
            descri = points[i].descripteurs
            artiste = (points[i].contributor).split("|")
            ville = (points[i].place).split(",")
            id = points[i].id
            medium= points[i].medium
            file= points[i].files;
            link= "http://127.0.0.1:5000/item_"+points[i].id;

            vis_popup = document.createElement("div");
            vis_popup.innerHTML = "<div class='vis_popup'>"+title+", "+label+"<br><br><a href='"+link+"'> <img src='"+file+"' width='auto' height='200vh'></a></div>";

            nodes.add(
                {
                  id: id,
                  title:vis_popup,
                  label: id,
                  artiste:artiste,
                  ville:ville,
                  descri:descri,
                  medium:medium,
                  value: 1,
                  group: 1,
                  color:{highlight:'crimson', hover:'crimson', border: 'beige', background:'darkpurple'},
              
                  mass: 8,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })

            edges.add({from: input, hidden: true, length:33, to: id})

            for (i in artiste) {
            edges.add({from: artiste[i], length:15, to:id})};

            for (i in ville) {
            edges.add({from: ville[i], length:15, to:id})};

};


var analysednodes = []
var analysednodes2 = []
nodes.forEach(node => {
    nodes.forEach(node2 => {
    var quotient_list = 0
    for (const o of node2["descri"]) {
        if (node["descri"].length>=2&&node["descri"].includes(o)&&node!=node2&&node["medium"]!=node2["medium"]) {quotient_list+=1}
    }
    var limite = ((node["descri"].length+node2["descri"].length)/2)*0.75
    ////if (node["medium"]==node2["medium"]&&node["medium"]!="aucun"&&node["medium"]!="False"&&node["id"]!=node2["id"]&&analysednodes2.includes(String(node["id"]+node2["id"]))==false){edges.add({from : node["id"], to:node2["id"]});analysednodes2.push(String(node["id"]+node2["id"]))}
    if (limite>=2&&quotient_list>limite&&analysednodes.includes(String(node2["id"]+node["id"]))==false){edges.add({from : node["id"], to: node2["id"], length:30, color:'#5353CC'});analysednodes.push(String(node["id"]+node2["id"]))}
    
})
})

    function populate (dict){
    for (i in dict) {
      if (dict[i]!="provenance inconnue"&&dict[i]!="Anonymous"&&dict[i]!="Créateur inconnu"&&villes.includes(dict[i])==false){
        nodes.add(
                {
                  id: dict[i],
                  label: dict[i],
                  title: dict[i],
                  descri:dict[i],
                  ville:"aucune",
                  artiste:"aucun",
                  medium:"aucun",        
                  font:{
                  size:28,
                  },
                  value: 3,
                  group: 1,
                  color:{highlight:'grey', border: 'indigo', background:'#9B93BD'},
                  mass: 15,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })}
}
    
};

    function populate2 (dict){
    for (i in dict) {
      if (dict[i]!="provenance inconnue"&&dict[i]!="Anonymous"&&dict[i]!="Créateur inconnu"){
        nodes.add(
                {
                  id: dict[i],
                  label: dict[i],
                  title: dict[i],
                  descri:dict[i],
                  ville:"aucune",
                  artiste:"aucun",
                  medium:"aucun",        
                  font:{
                  size:40,
                  },
                  value: 4,
                  group: 1,
                  color:{highlight:'grey', border: 'indigo', background:'#9B93BD'},
                  mass: 15,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })}
}
    
};

var villes = '''+str(villes_uniques)+''';
var artistes = '''+str(Artistes_uniques)+''';

populate2(villes)
populate(artistes)


const netw = new vis.Network(container, data, options);
var scaleOption = { scale : 0.1 }; -(1) 

netw.moveTo(scaleOption); -(2)
        

        netw.once('afterDrawing', function(e) {
        netw.setOptions({ physics: true })
        });

        netw.once('stabilized', function(e){
          netw.stopSimulation()
        });


netw.once('dblclick', function(e) {

          netw.focus("'''+str(input)+'''",{
            scale:0.2,
            });

    //if (this.style.width !="200%"){
        //this.style.width ="200%"
        //}
    //else {
        //this.style.width ="100%"
        //}
    });



'''

    script+=carto(correlations)
    script+='''

</script>'''

    return script

def netgraph_correlations(correlations,input) :

    correlations = []


    for i in donnees :
        if input == i["id"]:
            obj = i


    for y in donnees :

                a=0
                m=0
                if obj["id"]!=y["id"] :
                    quotient_list = 0
                

                    if str(y["contributor"]) != "Créateur inconnu" and str(obj["contributor"])!="Créateur inconnu":
                      for d in list(obj["contributor"].split(",")) :
                        for dd in list(y["contributor"].split(",")) :
                          if d==dd :
                            a-=4
                  

                    if str(y["medium"]) != "False" and str(obj["medium"])!="False":
                      for d in obj["medium"] :
                        for dd in y["medium"] :
                          if d==dd :
                            a+=2.5
                            m+=1.1

                    if  str(obj["place"])==str(y["place"]) and obj["place"] != "provenance inconnue":
                            a+=4
                    if  str(obj["région"])==str(y["région"]) and obj["région"] != "False":
                              a+=5
                    

                    for d in obj["descripteurs"] :
                      for dd in y["descripteurs"] :
                        if d==dd and m>0 :
                          quotient_list+=4*m
                        elif d==dd :
                          quotient_list+=4

                    limite=(len(obj["descripteurs"])+len(y["descripteurs"]))/2

                    quotient_list=(quotient_list/limite)*50
                    
                    a+=quotient_list*0.9

                    

                    if y["id"] is not False :

                        if len(obj["descripteurs"])==len(y["descripteurs"]):
                            y["Quotient"]=float(a+20)
                        if len(obj["descripteurs"])>len(y["descripteurs"]) and len(obj["descripteurs"])-len(y["descripteurs"])<=2:
                            y["Quotient"]=float(a+15)
                        if len(y["descripteurs"])>len(obj["descripteurs"]) and len(y["descripteurs"])-len(obj["descripteurs"])<=2:
                            y["Quotient"]=float(a+15)

                        if int(obj["date_deb"])==int(y["date_deb"]) :
                                y["Quotient"]=float(a+2)
                                correlations.append(y)


                        elif int(obj["date_deb"])<int(y["date_deb"]) :
                            if int(y["date_deb"])-int(obj["date_deb"]) <= 150 :
                                y["Quotient"]=float(a-(int(y["date_deb"])-int(obj["date_deb"]))*0.7)
                                correlations.append(y)


                        elif int(y["date_deb"])<int(obj["date_deb"]) :
                            if int(obj["date_deb"])-int(y["date_deb"]) <= 150 :
                                y["Quotient"]=float(a-(int(obj["date_deb"])-int(y["date_deb"]))*0.7)
                                correlations.append(y)

                
    a=0
    m=0

    graph_dict = []
    


    z=0
    correlations.sort(key=lambda x:x["Quotient"], reverse = True)
    
    if len(correlations)>650:
      correlations=correlations[:650]

    correlations.sort(key=lambda x:x["index"])

    for i in correlations:
            i["files"]=imagefrom_tif2(i["files"])
            graph_dict.append(i)

    villes_uniques = []
    Artistes_uniques = []

    villes=[]
    artistes=[]

    for valeur in graph_dict:
        if valeur['place'] != "False" :
            for i in valeur['place'].split(",") :
                villes.append(i.strip())

        if valeur["contributor"] != "Créateur inconnu":
            for i in valeur['contributor'].split("|") :
                artistes.append(i)

    if obj['place'] != "False" :
            for i in obj['place'].split(",") :
                villes.append(i.strip())

    if obj["contributor"] != "Créateur inconnu":
            for i in obj['contributor'].split("|") :
                artistes.append(i)

    villes_uniques = list(set(villes))
    Artistes_uniques = list(set(artistes))
    #descripteurs = set(itertools.chain.from_iterable(descripteurs))
    
    for i in donnees :
        if input == i["id"]:
            obj = i

    script='''
<script type="text/javascript">


const input = "'''+input+'''"
'''
    script+='''const edges = new vis.DataSet();
const nodes = new vis.DataSet();


var points='''+str(graph_dict)+'''

  nodes.add({
    id: "'''+str(obj["id"])+'''",
    label: input,
    title: "'''+str(obj["id"])+", "+ str(obj["contributor"])+", "+str(obj["title"])+", "+str(obj["date"])+"."+'''",
    ville:"'''+str(obj["place"])+'''",
    artiste:"'''+str(obj["contributor"]).replace("|",", ")+'''",
    descri:'''+str(obj["descripteurs"])+''',
    medium:"'''+str(obj["medium"])+'''",
    value: 3,
    fixed:false,
    font:{
            size:30,
            color: 'blanchedalmond',
        },
    group: 1,
    color:{highlight:'grey', border: 'blanchedalmond', background:'black', edges:'blanchedalmond'},

    mass: 4,
    borderWidth: 1.8,
    x: 300,
    y: 300,
  },)

var ville = "'''+str(obj["place"])+'''".split(",")
artiste="'''+str(obj["contributor"]).replace("|",", ")+'''".split(",")


            for (i in artiste) {
            edges.add({from: artiste[i], to:input})};

            for (i in ville) {
            edges.add({from: ville[i], to:input})};

  var container = document.getElementById("mynetwork");

function calculateNodePositions(nodes, villes, artistes, edges) {
    const villeNodes = [];
    const artisteNodes = [];
    const otherNodes = [];
  
    // Séparer les noeuds en fonction de leur type
    nodes.forEach(node => {
      if (villes.includes(node.id)) {
        villeNodes.push(node);
      } else if (artistes.includes(node.id)) {
        artisteNodes.push(node);
      } else {
        otherNodes.push(node);
      }
    });
  
    var len_total = '''+str(int(len(graph_dict)))+'''
    var len_total2 = '''+str(int(len(graph_dict)*1.5))+'''

    // Placer les noeuds ville et artiste en cercle autour du centre
    let angle = 0;
    const radius = len_total;
    const radius2 = len_total2;
    for (const node of villeNodes) {
      node.x = radius * Math.cos(angle);
      node.y = radius * Math.sin(angle);
      angle += 2 * Math.PI / villeNodes.length;
    }
    for (const node of artisteNodes) {
      node.x = radius * Math.cos(angle);
      node.y = radius * Math.sin(angle);
      angle += 2 * Math.PI / artisteNodes.length;
    }
  
    // Placer les autres noeuds autour des noeuds ville et artiste
    angle = Math.floor(Math.random() * (280 - 1 + 1)) + 1;
    for (const node of otherNodes) {
      if (villes.includes(node.ville) || artistes.includes(node.artiste)) {
        node.x = radius2 * Math.cos(angle);
        node.y = radius2 * Math.sin(angle);
        angle += 2 * Math.PI / otherNodes.length;
      }
    }
  
    // Recalculer la position des noeuds liés par plus d'un lien
    for (const node of otherNodes) {
      const connectedNodes = getConnectedNodes(node, otherNodes, edges);
      if (connectedNodes.length > 1) {
        angle = Math.floor(Math.random() * (280 - 1 + 1)) + 1;
        for (const connectedNode of connectedNodes) {
          connectedNode.x = node.x + radius * Math.cos(angle);
          connectedNode.y = node.y + radius * Math.sin(angle);
          angle += 2 * Math.PI / connectedNodes.length;
        }
      }
    }
  
    // Mettre à jour les données dans les objets vis.DataSet()
    nodes.update(villeNodes.concat(artisteNodes, otherNodes));
  }
  
  function getConnectedNodes(node, otherNodes, edges) {
    const connectedNodes = [];
    edges.forEach(edge => {
      if (edge.from === node.id || edge.to === node.id) {
        const connectedNode = otherNodes.find(n => n.id === edge.from || n.id === edge.to);
        if (connectedNode) {
          connectedNodes.push(connectedNode);
        }
      }
  });
    return connectedNodes;
  }
  
  const options = {
    physics:{enabled:false},
    nodes: {
      shape: "dot",
      scaling: {
        min: 7,
        max: 30,
      },
      font: {
        size: 7,
        face: "Quicksand",
        color: "beige",
      },
    },
    edges: {
      color:{highlight:'white'},
      width: 0.20,
      length:5,
      smooth: {
          enabled:true,
          roundness:0.75,
          type:"dynamic",
          },
    },
    interaction: {
    hover:true,
    tooltipDelay:0.2,
    }
  };

for (i in points) {

        var lat = points[i].lat	//position found
            lon = points[i].lon
            label = points[i].label
            title = points[i].title
            descri = points[i].descripteurs
            artiste = (points[i].contributor).split("|")
            ville = (points[i].place).split(",")
            id = points[i].id
            medium= points[i].medium
            file= points[i].files;
            link= "http://127.0.0.1:5000/item_"+points[i].id;

            vis_popup = document.createElement("div");
            vis_popup.innerHTML = "<div class='vis_popup'>"+title+", "+label+"<br><br><a href='"+link+"'> <img src='"+file+"' width='auto' height='200vh'></a></div>";

if (id!=input){
            nodes.add(
                {
                  id: id,
                  title:vis_popup,
                  label: id,
                  artiste:artiste,
                  ville:ville,
                  descri:descri,
                  medium:medium,
                  value: 1,
                  group: 1,
                  color:{highlight:'crimson', hover:'crimson', border: 'beige', background:'darkpurple'},
              
                  mass: 8,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })
};

            for (i in artiste) {
            edges.add({from: artiste[i], length:15, to:id})};

            for (i in ville) {
            edges.add({from: ville[i], length:15, to:id})};

};



var analysednodes = []
var analysednodes2 = []
nodes.forEach(node => {
    nodes.forEach(node2 => {
    var quotient_list = 0
    for (const o of node2["descri"]) {
        if (node["descri"].length>=2&&node["descri"].includes(o)&&node!=node2&&node["medium"]!=node2["medium"]) {quotient_list+=1}
    }
    var limite = ((node["descri"].length+node2["descri"].length)/2)*0.75
    ////if (node["medium"]==node2["medium"]&&node["medium"]!="aucun"&&node["medium"]!="False"&&node["id"]!=node2["id"]&&analysednodes2.includes(String(node["id"]+node2["id"]))==false){edges.add({from : node["id"], to:node2["id"]});analysednodes2.push(String(node["id"]+node2["id"]))}
    if (limite>=2&&quotient_list>limite&&analysednodes.includes(String(node2["id"]+node["id"]))==false){edges.add({from : node["id"], to: node2["id"], length:30, color:'#5353CC'});analysednodes.push(String(node["id"]+node2["id"]))}
    
})
})

    function populate (dict){
    for (i in dict) {
      if (dict[i]!="provenance inconnue"&&dict[i]!="Anonymous"&&dict[i]!="Créateur inconnu"&&villes.includes(dict[i])==false){
        nodes.add(
                {
                  id: dict[i],
                  label: dict[i],
                  title: dict[i],
                  descri:dict[i],
                  ville:"aucune",
                  artiste:"aucun",
                  medium:"aucun",        
                  font:{
                  size:28,
                  },
                  value: 3,
                  group: 1,
                  color:{highlight:'grey', border: 'indigo', background:'#9B93BD'},
                  mass: 15,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })}

}};

    function populate2 (dict){
    for (i in dict) {
      if (dict[i]!="provenance inconnue"&&dict[i]!="Anonymous"&&dict[i]!="Créateur inconnu"){
        nodes.add(
                {
                  id: dict[i],
                  label: dict[i],
                  title: dict[i],
                  descri:dict[i],
                  ville:"aucune",
                  artiste:"aucun",
                  medium:"aucun",        
                  font:{
                  size:40,
                  },
                  value: 4,
                  group: 1,
                  color:{highlight:'grey', border: 'indigo', background:'#9B93BD'},
                  mass: 15,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })}
}
    
};

var villes = '''+str(villes_uniques)+''';
var artistes = '''+str(Artistes_uniques)+''';

populate2(villes)
populate(artistes)

const data = {
    nodes: nodes,
    edges: edges
  };


calculateNodePositions(nodes, villes, artistes, edges)

const netw = new vis.Network(container, data, options).once('beforeDrawing', function(e) {

        netw.focus("'''+str(input)+'''",{
            scale:0.4,
            });
        });

        netw.once('afterDrawing', function(e) {
        netw.setOptions({ physics: true })
        });

        netw.once('stabilized', function(e){
          netw.stopSimulation()
        });


netw.once('dblclick', function(e) {

          netw.focus("'''+str(input)+'''",{
            scale:0.2,
            });

    //if (this.style.width !="200%"){
        //this.style.width ="200%"
        //}
    //else {
        //this.style.width ="100%"
        //}
    });

'''
    script+=str(carto_correlations(correlations, input))
    script+='''



var villes = '''+str(villes_uniques)+''',
artistes = '''+str(Artistes_uniques)+'''

</script>'''
    
    return script

app = Flask(__name__)
@app.route('/')


def home():
    return render_template('base.html')

@app.route('/corrélateur', methods = ['POST', 'GET'])
def result() :
    
    b = "<div id='resultat'>Erreur de requête.</div>"
    a = render_template('result.html', contenu = b, titre = str(request.form["input"]))

    texte = request.form["input"]

    def requeter(param) :
        texte = request.form["input"]
        requete=[]
        
        if len(list(texte.split(",")))>1:
          liste = list(texte.split(","))
          if liste[len(liste)-1].replace(" ","").isdigit():
              limite = int(liste[len(liste)-1].replace(" ",""))
              texte = re.sub(", \d*$", "", texte)
              texte = re.sub(",\d*$", "", texte)
              param2=[]
              print(texte)
              for i in param :
                if i["index"]==3444:
                  print(i)
                if len(i["descripteurs"])>=limite:
                  param2.append(i)
              param=param2

        if len(list(texte.split(",")))>1:
          pattern="(et)"
          result=re.search(pattern,texte)
          pattern2="(ou)"
          result2=re.search(pattern2,texte)
          pattern3="(dates*)"
          result3=re.search(pattern3,texte)

          if result :
                print("(et)!")
                texte = texte.replace(", ",".*")
                texte = texte.replace(",",".*")
                texte = texte.replace(".*(et)","")
                texte = texte.replace(".* (et)","")
                texte = texte.replace(" (et)","")
                texte = texte.replace("(et)","")
                print(texte)
                regex = re.compile(texte.lower())
                for i in param :
                        result = regex.search(str(i).lower())
                        if result and i not in requete:
                            requete.append(i)
          elif result2 : 
                print("(ou)!")
                print(texte)
                texte = texte.replace(", ","|")
                texte = texte.replace(",","|")
                texte = texte.replace("|(ou)","")
                texte = texte.replace(" (ou)","")
                texte = texte.replace("(ou)","")
                regex = re.compile(texte.lower())
                for i in param :
                        result = regex.search(str(i).lower())
                        if result and i not in requete:
                            requete.append(i)
          elif result3 :
                print("(dates)!")
                dates=list(texte.replace("(","").split(","))[len(texte.split(","))-1]
                dates=list(dates.strip().replace(")","").split(" "))[1]
                dates=list(dates.split("-"))
                texte = list(texte.split(", (dates "))[0]
                texte = texte.replace(", ","|")
                texte = texte.replace(",","|")
                print(texte)
                print(dates)
                regex = re.compile(texte.lower())
                for i in param :
                        result = regex.search(str(i).lower())
                        if result and i not in requete and i["date_deb"]>=int(dates[0].strip()) and i["date_fin"]<=int(dates[1].strip()):
                            requete.append(i)
          elif result and result3 :
                print("(et), (dates)!")
                print(texte)
                dates=list(texte.replace("(","").split(","))[len(texte.split(","))-1]
                dates=list(dates.strip().replace(")","").split(" "))[1]
                dates=list(dates.split("-"))
                texte = list(texte.split(", (dates "))[0]
                texte = texte.replace(", ",".*")
                texte = texte.replace(",",".*")
                texte = texte.replace(".*(et)","")
                texte = texte.replace(".* (et)","")
                texte = texte.replace(" (et)","")
                texte = texte.replace("(et)","")
                texte = ".*"+texte+".*"
                print(texte)
                regex = re.compile(texte.lower())
                for i in param :
                        result = regex.search(str(i).lower())
                        if result and i not in requete and i["date_deb"]>=int(dates[0].strip()) and i["date_fin"]<=int(dates[1].strip()):
                            requete.append(i)
          else :
              print(texte)
              texte=list(texte.split(","))
              for e in texte :
                for i in param :
                    for key, value in i.items():
                        e = e.lower().strip()
                        regex = re.compile(e)
                        result = regex.search(str(value).lower())
                        if result :
                            #if key != i["title"] and value != i["title"] and key != i["label"] and value != i["label"] :
                                if i not in requete :
                                    requete.append(i)
          
        else :
          for i in param :
              for key, value in i.items():
                  pattern = texte.lower().strip()
                  regex = re.compile(pattern)
                  result = regex.search(str(value).lower())
                  if result :
                      #if key != i["title"] and value != i["title"] and key != i["label"] and value != i["label"] :
                          if i not in requete :
                              requete.append(i)

        #if len(requete) > 200 :
            #requete=requete[:200]

        return requete

    correlations = requeter(donnees)

    def is_id(param) :
        pattern = request.form["input"]
        for i in param :
                value = i["id"]
                regex = re.compile(pattern)
                result = regex.search(str(value).lower())
                if result :
                    return True

    if request.method == 'POST' and is_id(donnees) is True :
        input = (str(request.form["input"]).replace("^","")).replace("$","")
        d = correlateur(donnees, input)
        c = render_template('result2.html', script=netgraph_correlations(donnees,input), contenu = d, titre = str(request.form["input"]))
        return c

    elif request.method == 'POST' and correlations != [] :
        if len(correlations)>=1:
            d='<div id="resultat">'+'''</br><div id="map"></div><div id="netgraph"><div id="loadingScreen">Chargement...</div><div id="mynetwork"></div></div></div><br><h2>'''+ str(len(correlations))+" correspondances."'</h2><div id="resultats">'

            if len(correlations)<=360:
              for i in range(len(correlations)) :
                  #secure_filename(correlations[i]["img"].split("/")[1])
                  
                  if i % 4 == 0 and i!=0:
                      d+='</div><br><div id="resultats">'
                  d+='<a id="compart" href="'+url_for("item_", Idx=str(correlations[i]["id"]))+'"><div id="carrousel"><img id="'+str(correlations[i]["id"])+'" width="auto" height="300vh" src="'+imagefrom_tif(correlations[i]["files"])+'"/><br></div><br><br><div id="cartel">'+str(correlations[i]["title"])+', '+str(correlations[i]["contributor"])+', '+str(correlations[i]["medium"]).replace("]","").replace("[","").replace("' ","").replace("'","")+", ("+str(correlations[i]["id"])+")"+", "+str(correlations[i]["date"])+", "+str(correlations[i]["place"])+".</div></a>"+'''
          '''
              d+='</div>'

            else :
              for i in range(360) :
                  #secure_filename(correlations[i]["img"].split("/")[1])

                  if i % 4 == 0 and i!=0:
                      d+='</div><br><div id="resultats">'
                  d+='<a id="compart" href="'+url_for("item_", Idx=str(correlations[i]["id"]))+'"><div id="carrousel"><img id="'+str(correlations[i]["id"])+'" width="auto" height="300vh" src="'+imagefrom_tif(correlations[i]["files"])+'"/><br></div><br><div id="cartel">'+str(correlations[i]["title"])+', '+str(correlations[i]["contributor"])+', '+str(correlations[i]["medium"]).replace("]","").replace("[","").replace("' ","").replace("'","")+", ("+str(correlations[i]["id"])+")"+", "+str(correlations[i]["date"])+", "+str(correlations[i]["place"])+".</div></a>"+'''
          '''
              d+='</div>'

            return render_template('result.html', script=netgraph(correlations), contenu = d, titre = str(request.form["input"]))

    else :
        return a

@app.route('/résult', methods = ['POST', 'GET'])
def result2() :
    b = "<div id='resultat'>Erreur de requête.</div>"
    a = render_template('result.html', contenu = b)

    def is_id(param) :
        pattern = request.form["input"]
        for i in param :
            for key, value in i :
                search = re.search(pattern,str(value).lower())
                if search :
                    return True

    if request.method == 'POST' and is_id(donnees) is True :
        input = str(request.form["input"])
        
        d = correlateur(donnees, input)
        c = render_template('result2.html', script=netgraph_correlations(donnees,input), contenu = d, titre = str(request.form["input"]))
        return c

    else :
        return a

        

@app.route('/item_<path:Idx>', methods = ['POST', 'GET'])
def item_(Idx):
    input = Idx
    d = correlateur(donnees, input)
    c = render_template('result2.html', script=netgraph_correlations(donnees,input), contenu = d, titre = str(input))
    return c



@app.route('/<path:filename>')
def serve_images(filename):
    return send_from_directory('MET_img/', filename)

@app.route('/result.css')
def serve_css():
    return send_from_directory('templates/', "result.css")

@app.route('/tiff.js')
def serve_tiffjs():
    return send_from_directory('', "tiff.js")

@app.route('/result2.css')
def serve_css2():
    return send_from_directory('templates/', "result2.css")

@app.route('/corr_icon.png')
def serve_icon():
    return send_from_directory('', "corr.png")

@app.route('/no_img.png')
def serve_img():
    return send_from_directory('', "icons8-no-image-gallery-96.png")

if __name__ == '__main__':
   app.run(debug=True)

if Exception :
  print(Exception)