from flask import Flask, render_template, request
import pandas as pd
from string import Template
import numpy as np
import re

dtf = pd.read_csv(r"C:\Users\uuuu\Documents\images.csv", dtype={"conservation_institution":"str","contributor":"str", "extent":"str", "ornamental_motif":"str", "incipit":"str"})

#dtf = dtf.loc[dtf["place_type"]!="Localisation_inconnue"]
dtf = dtf.loc[dtf["id"]!="False"]
dtf = dtf.loc[dtf["id"]!=False]

#dtf = dtf[:59591]
 
base_images = []

print("chargement du dictionnaire")
for i in range(len(dtf)) :
    descri=[]
    
    def descripteurs(o):
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

    if i < len(dtf)-1 :
      descripteurs(dtf["timel_nature_place"][i+1])
      descripteurs(dtf["timel_object_architecture"][i+1])
      descripteurs(dtf["timel_character"][i+1])
      descripteurs(dtf["timel_subject"][i+1])
      descripteurs(dtf["timel_subject"][i+1])
    
    else :
      descri = []

    descri = list(set(descri))

    if dtf["lat"][i] != "False" :
        i = {
    "id":(dtf["id"][i].replace(" ","_")).replace(".","_"),
    "lat":float(dtf["lat"][i]),
    "lon":float(dtf["lon"][i]),
    "contributor":((dtf["contributor"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
    "manuscrit":dtf["archival_reference"][i],
    "title":dtf["title"][i],
    "place":dtf["place"][i],
    "région":dtf["place_type"][i],
    "date":dtf["Date"][i].replace("False","date inconnue"),
    "date_deb":dtf["date_deb"][i],
    "date_fin":dtf["date_fin"][i],
    "descripteurs":descri,
    "folio":dtf["folio"][i],
    "origin":dtf["related_dataset_id"][i],
    "label":dtf["archival_reference"][i]+" fol."+dtf["folio"][i]+" par "+((dtf["contributor"][i].replace(":"," : ")).replace("_", " ")).replace("False","créateur inconnu")+", "+dtf["place"][i]+", "+dtf["Date"][i].replace("False","date inconnue")+".",
    "Quotient":"",
    "index":int(i),
    }

    else :
        i = {
    "id":(dtf["id"][i].replace(" ","_")).replace(".","_"),
    "lat":dtf["lat"][i],
    "lon":dtf["lon"][i],
    "contributor":((dtf["contributor"][i].replace(":"," : ")).replace("_", " ")).replace("False","Créateur inconnu"),
    "manuscrit":dtf["archival_reference"][i],
    "title":dtf["title"][i],
    "place":dtf["place"][i],
    "région":dtf["place_type"][i],
    "date":dtf["Date"][i].replace("False","date inconnue"),
    "date_deb":dtf["date_deb"][i],
    "date_fin":dtf["date_fin"][i],
    "descripteurs":descri,
    "folio":dtf["folio"][i],
    "origin":dtf["related_dataset_id"][i],
    "label":dtf["archival_reference"][i]+" fol."+dtf["folio"][i]+" par "+((dtf["contributor"][i].replace(":"," : ")).replace("_", " ")).replace("False","créateur inconnu")+", "+dtf["place"][i].replace("False","origine inconnue")+", "+dtf["Date"][i].replace("False","date inconnue")+".",
    "Quotient":"",
    "index":int(i),
    }

    base_images.append(i)

t = len(dtf)

def carto(corrélations) :
    carto_dict = []

    for i in corrélations :
        e = i["région"]
        u = i["lon"]
        if e != "Localisation inconnue" or e == "Catalunya" :
            if u != "False" :
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
            {"attribution": "Quentin Bernet, 2022."}
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
        for(i in points) {
        var Origin = (points[i].origin).split(","),	//value searched
            lat = points[i].lat,	
            lon = points[i].lon,
            label = points[i].label
            descri = points[i].descripteurs
            artiste = (points[i].contributor).split(",")
            ville = (points[i].place).split(",");


        heat_points.push([lat,lon,0.3])};

        var heat = L.heatLayer(heat_points, {gradient:{0.2: '#2D3053', 0.7: '#9B93BD', 1: 'beige'}, minOpacity:0.75, blur:35, radius: 30}).addTo(map);
                
                
                
                '''

    return script

def carto_corrélations(corrélations, input) :

    corrélations = []
    for i in base_images :
        if input == i["id"]:
            obj = i


    for y in base_images :

                a=0
                if obj["id"]!=y["id"] :
                    quotient_list = 0

                    if str(obj["origin"]) != 'False':
                      for d in list(obj["origin"].split(",")) :
                        if d==y["id"] :
                          a+=2

                    if str(y["contributor"]) != "Créateur inconnu" and str(obj["contributor"])!="Créateur inconnu":
                      for d in list(obj["contributor"].split(",")) :
                        for dd in list(y["contributor"].split(",")) :
                          if d==dd :
                            a+=2

                    if  str(obj["place"])==str(y["place"]) and obj["place"] != "False":
                            a+=1.5
                    if  str(obj["région"])==str(y["région"]) and obj["région"] != "Localisation inconnue":
                            a+=1

                    for d in obj["descripteurs"] :
                      for dd in y["descripteurs"] :
                        if d==dd :
                          quotient_list+=1

                    if len(obj["descripteurs"])>len(y["descripteurs"]):
                      limite=len(obj["descripteurs"])
                    else :
                      limite=len(y["descripteurs"])

                    quotient_list=(quotient_list/limite)*100
                    
                    a+=quotient_list*0.9

                    if y["id"] is not False :

                        if int(obj["date_deb"])==int(y["date_deb"]) :
                                y["Quotient"]=float(a+2)
                                corrélations.append(y)


                        elif int(obj["date_deb"])<int(y["date_deb"]) and obj["date_deb"] !=0:
                            if int(y["date_deb"])-int(obj["date_deb"]) <= 80 :
                                y["Quotient"]=float(a-(int(y["date_deb"])-int(obj["date_deb"]))*0.2)
                                corrélations.append(y)


                        elif int(y["date_deb"])<int(obj["date_deb"]) and int(y["date_deb"])!=0:
                            if int(obj["date_deb"])-int(y["date_deb"]) <= 80 :
                                y["Quotient"]=float(a-(int(obj["date_deb"])-int(y["date_deb"]))*0.2)
                                corrélations.append(y)


                        else :
                                
                                y["Quotient"]=float(a-100)
                
    a=0
        
    corrélations.sort(key=lambda x:x["Quotient"], reverse = True)

    if len(corrélations) > 300 :
        corrélations=corrélations[:300]

    for i in base_images :
      if i["id"] == input :
        input = i

    carto_dict = []

    for i in corrélations:
        if i["région"] != "Localisation inconnue" or i["région"] == "Catalunya" :
            if i["lon"] != "False":
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
    zoom: 6,
    center : [43.950001, 4.81667]});

    L.tileLayer(
            "https://api.mapbox.com/styles/v1/quentinbernet/cla6lh9e1000714mt0kv7e87z/tiles/256/{z}/{x}/{y}?access_token=pk.eyJ1IjoicXVlbnRpbmJlcm5ldCIsImEiOiJja3ltenMxb2MwN2s3MnBuOXM4cGJma3d5In0.fPSmSgvw8iuMJ7eXobdtAw",
            {"attribution": "Quentin Bernet, 2022."}
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
        for(i in points) {
        var Origin = (points[i].origin).split(","),	//value searched
            lat = points[i].lat,	
            lon = points[i].lon,
            label = points[i].label
            descri = points[i].descripteurs
            artiste = (points[i].contributor).split(",")
            ville = (points[i].place).split(",");


        heat_points.push([lat,lon,0.3])};

        var heat = L.heatLayer(heat_points, {gradient:{0.2: '#2D3053', 0.7: '#9B93BD', 1: 'beige'}, minOpacity:0.75, blur:35, radius: 30}).addTo(map);

        var circle = new L.circleMarker (['''+str(input["lat"])+","+str(input["lon"])+'''], {label:label, icon:blur2, opacity: 0.4, radius:10, fillColor:'none', color:'blanchedalmond'});
            circle.addTo(map);
        
        '''



    return script


def corrélateur(base_images,input) :

    corrélations = []
    for i in base_images :
        if input == i["id"]:
            obj = i


    for y in base_images :

                a=0
                if obj["id"]!=y["id"] :
                    quotient_list = 0
                    
                    if str(obj["origin"]) != 'False':
                      for d in list(obj["origin"].split(",")) :
                        if d==y["id"] :
                          a+=2

                    if str(y["contributor"]) != "Créateur inconnu" and str(obj["contributor"])!="Créateur inconnu":
                      for d in list(obj["contributor"].split(",")) :
                        for dd in list(y["contributor"].split(",")) :
                          if d==dd :
                            a+=2

                    if  str(obj["place"])==str(y["place"]) and obj["place"] != "False":
                            a+=1.5
                    if  str(obj["région"])==str(y["région"]) and obj["région"] != "Localisation inconnue":
                            a+=1

                    for d in obj["descripteurs"] :
                      for dd in y["descripteurs"] :
                        if d==dd :
                          quotient_list+=1

                    if len(obj["descripteurs"])>len(y["descripteurs"]):
                      limite=len(obj["descripteurs"])
                    else :
                      limite=len(y["descripteurs"])

                    quotient_list=(quotient_list/limite)*100
                    
                    a+=quotient_list*0.9

                    if y["id"] is not False :

                        if int(obj["date_deb"])==int(y["date_deb"]) :
                                y["Quotient"]=float(a+2)
                                corrélations.append(y)


                        elif int(obj["date_deb"])<int(y["date_deb"]) and obj["date_deb"] !=0:
                            if int(y["date_deb"])-int(obj["date_deb"]) <= 80 :
                                y["Quotient"]=float(a-(int(y["date_deb"])-int(obj["date_deb"]))*0.2)
                                corrélations.append(y)


                        elif int(y["date_deb"])<int(obj["date_deb"]) and int(y["date_deb"])!=0:
                            if int(obj["date_deb"])-int(y["date_deb"]) <= 80 :
                                y["Quotient"]=float(a-(int(obj["date_deb"])-int(y["date_deb"]))*0.2)
                                corrélations.append(y)


                        else :
                                
                                y["Quotient"]=float(a-100)

                        print(y["Quotient"], end=", ")

    a=0
    corrélations.sort(key=lambda x:x["Quotient"], reverse = True)

    if len(corrélations) > 200 :
        corrélations=corrélations[:200]

    print(corrélations)

    #url = str(img[x])
    
    def imprime() :
        corrélations.sort(key=lambda x:x["Quotient"], reverse = True)
        if obj["id"] is not False :

            a = '<div id="résultat"><div id="map"></div><div id="résultat1"><img src="''" height="auto" width="350px"><br><br>'
            a += "Vous avez choisi "+str(obj["id"])+", "+str(obj["title"])+ " fol."+str(obj["folio"])+", "+" par "+str(obj["contributor"])+", "+str(obj["date"])+', '+str(obj["place"]).replace("False", "origine exacte inconnue")+'. </div><div id="netgraph"><div id="loadingScreen">Chargement...</div><div id="mynetwork"></div></div></div><br><br>'
        
        else :
            a = '<div id="résultat"><div id="map"></div><div id="résultat1">'
            a += 'Vous avez choisi '+str(obj["id"])+", "+str(obj["title"])+ " fol."+str(obj["folio"])+", "+' par '+str(obj["contributor"])+', '+str(obj["date"])+' (Pas de reproduction), '+str(obj["place"]).replace("False", "origine exacte inconnue")+'. </div><div id="netgraph"><div id="loadingScreen">Chargement...</div><div id="mynetwork"></div></div></div><br><br>'
        z = -1
        if len(corrélations)<= 35 :
            longueur = len(corrélations)
        else :
            longueur = 35
        a += '<div id="résultats">'
        for i in range(longueur) :
            z+=1
            a += '<a id="compart" href="http://127.0.0.1:5000/item_'+corrélations[z]["id"]+'"> <img id="résultat_indiv" src="'+corrélations[z]["id"]+'" height="410vh" width="auto"><br><div id="cartel"> Proche de '+corrélations[z]["id"]+" : "+corrélations[z]["label"]+"</div></a><br>"+'''
    '''
            #if z == 5 or z == 10 or z == 15 or z == 20:
            #    a += '</div><br><div id="résultats">'
            if i % 4 == 0 :
                    a+='</div><br><div id="résultats">'
        a += "</div>"
        return a
    b = imprime()

    def résultat () :
        if corrélations != [] :
            return b
        else :
            return "<div id='résultat'>Pas de corrélations pour cette oeuvre.</div>"

    return résultat()

def clean_data(param) :
        param=str(param)
        param=param.replace("Attribué à ","")
        param=param.replace(" ?","")
        param=param.replace("?","")
        param=param.replace("-"," ")
        param=param.replace("Î","I")
        param=param.replace(" (environs)","")
        return param

def netgraph(corrélations) :

    texte = str(clean_data(request.form["input"]))

    input = clean_data(texte)

    script='''

<script type="text/javascript">


const input = "'''+input+'''"
'''

    graph_dict = []

    for i in corrélations:
        if i["région"] != "Localisation inconnue" or i["région"] == "Catalunya" :
            if i["place"] != "False":
                graph_dict.append(i)

    villes=[]
    artistes=[]

    for valeur in graph_dict:
        if valeur['place'] != "False" :
            for i in list(valeur['place'].split(",")) :
                villes.append(i)

        if valeur["contributor"] != "Créateur inconnu":
            for i in list(valeur['contributor'].split(",")) :
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
  
    var len_total = '''+str(int(len(graph_dict)*2))+'''
    var len_total2 = '''+str(int(len(graph_dict)*3))+'''

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
        min: 5,
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
      width: 0.35,
      length:3,
      smooth: {
          enabled:true,
          roundness:0.75,
          type:"dynamic",
          },
    },
    interaction: {
    hover:true,
    tooltipDelay:50,
    }
  };

for (i in points) {

        var origin = (points[i].origin).split(",")
            lat = points[i].lat	//position found
            lon = points[i].lon
            label = points[i].label
            title = points[i].title
            descri = points[i].descripteurs
            artiste = (points[i].contributor).split(",")
            ville = (points[i].place).split(",")
            id = points[i].id
            manuscrit= points[i].manuscrit;

            nodes.add(
                {
                  id: id,
                  label: id+' '+label,
                  artiste:artiste,
                  ville:ville,
                  origin:origin,
                  title:label,
                  descri:descri,
                  manuscrit:manuscrit,
                  value: 1,
                  group: 1,
                  color:{highlight:'crimson', hover:'crimson', border: 'beige', background:'darkpurple'},
              
                  mass: 5,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })

            edges.add({from: input, hidden: true, length:33, to: id})

            for (i in origin) {
            edges.add({from: origin[i], to: id})};

            for (i in artiste) {
            edges.add({from: artiste[i], to:id})};

            for (i in ville) {
            edges.add({from: ville[i], to:id})};

};


var analysednodes = []
nodes.forEach(node => {
    nodes.forEach(node2 => {
    var quotient_list = 0
    for (const o of node2["descri"]) {
        if (node["descri"].includes(o)&&node!=node2&&node["manuscrit"]!=node2["manuscrit"]) {quotient_list+=1}
    }if (node["descri"].length>node2["descri"].length){
      var limite = node["descri"].length*0.75
    } else {
      var limite = node2["descri"].length*0.75
    }
    if (quotient_list>1&&quotient_list>limite&&analysednodes.includes(String(node2["id"]+node["id"]))==false){edges.add({from : node["id"], to: node2["id"], color:'#5353CC'});analysednodes.push(String(node["id"]+node2["id"]))}
    })
})

    function populate (dict){
    for (i in dict) {
    if (dict[i] != input) {
        nodes.add(
                {
                  id: dict[i],
                  label: dict[i],
                  title: dict[i],
                  descri:dict[i],
                  ville:"aucune",
                  artiste:"aucun",
                  manuscrit:"aucun",        
                  font:{
                  size:30,
                  },
                  value: 4,
                  group: 1,
                  color:{highlight:'grey', border: 'indigo', background:'#9B93BD'},
              
                  mass: 9,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })

}}
    
};

var villes = '''+str(villes_uniques)+''';
var artistes = '''+str(Artistes_uniques)+''';

populate(villes)
populate(artistes)

calculateNodePositions(nodes, villes, artistes, edges)

const netw = new vis.Network(container, data, options).once('beforeDrawing', function(e) {

        netw.focus("'''+str(input)+'''",{
            scale:0.14,
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

    script+=carto(corrélations)
    script+='''

</script>'''

    return script

def netgraph_corrélations(corrélations,input) :

    corrélations = []


    for i in base_images :
        if input == i["id"]:
            obj = i


    for y in base_images :

                a=0
                if obj["id"]!=y["id"] :
                    quotient_list = 0
                    
                    if str(obj["origin"]) != 'False':
                      for d in list(obj["origin"].split(",")) :
                        if d==y["id"] :
                          a+=2

                    if str(y["contributor"]) != "Créateur inconnu" and str(obj["contributor"])!="Créateur inconnu":
                      for d in list(obj["contributor"].split(",")) :
                        for dd in list(y["contributor"].split(",")) :
                          if d==dd :
                            a+=2

                    if  str(obj["place"])==str(y["place"]) and obj["place"] != "False":
                            a+=1.5
                    if  str(obj["région"])==str(y["région"]) and obj["région"] != "Localisation inconnue":
                            a+=1
                    for d in obj["descripteurs"] :
                      for dd in y["descripteurs"] :
                        if d==dd :
                          quotient_list+=1

                    if len(obj["descripteurs"])>len(y["descripteurs"]):
                      limite=len(obj["descripteurs"])
                    else :
                      limite=len(y["descripteurs"])

                    quotient_list=(quotient_list/limite)*100
                    
                    a+=quotient_list*0.9
                    

                    if y["id"] is not False :

                        if int(obj["date_deb"])==int(y["date_deb"]) :
                                y["Quotient"]=float(a+2)
                                corrélations.append(y)


                        elif int(obj["date_deb"])<int(y["date_deb"]) and obj["date_deb"] !=0:
                            if int(y["date_deb"])-int(obj["date_deb"]) <= 80 :
                                y["Quotient"]=float(a-(int(y["date_deb"])-int(obj["date_deb"]))*0.2)
                                corrélations.append(y)


                        elif int(y["date_deb"])<int(obj["date_deb"]) and int(y["date_deb"])!=0:
                            if int(obj["date_deb"])-int(y["date_deb"]) <= 80 :
                                y["Quotient"]=float(a-(int(obj["date_deb"])-int(y["date_deb"]))*0.2)
                                corrélations.append(y)


                        else :
                                
                                y["Quotient"]=float(a-100)
                
    a=0

    graph_dict = []
    


    z=0
    corrélations.sort(key=lambda x:x["Quotient"], reverse = True)
    
    if len(corrélations)>650:
      corrélations=corrélations[:650]

    corrélations.sort(key=lambda x:x["index"])

    for i in corrélations:
            graph_dict.append(i)

    villes_uniques = []
    Artistes_uniques = []

    villes=[]
    artistes=[]

    for valeur in graph_dict:
        if valeur['place'] != "False" :
            for i in list(valeur['place'].split(",")) :
                villes.append(i)

        if valeur["contributor"] != "Créateur inconnu":
            for i in list(valeur['contributor'].split(",")) :
                artistes.append(i)

    if obj['place'] != "False" :
            for i in list(obj['place'].split(",")) :
                villes.append(i)

    if obj["contributor"] != "Créateur inconnu":
            for i in list(obj['contributor'].split(",")) :
                artistes.append(i)

    villes_uniques = list(set(villes))
    Artistes_uniques = list(set(artistes))
    #descripteurs = set(itertools.chain.from_iterable(descripteurs))
    
    for i in base_images :
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
    id: input,
    label: input,
    title: "'''+str(obj["id"])+", "+ str(i["contributor"])+", "+str(i["title"])+", "+str(i["date"])+"."+'''",
    ville:"'''+str(obj["place"])+'''",
    artiste:"'''+str(obj["contributor"])+'''",
    origin:"'''+str(obj["origin"])+'''",
    descri:"'''+str(obj["descripteurs"])+'''",
    manuscrit:"'''+str(obj["manuscrit"])+'''",
    value: 9,
    fixed:true,
    font:{
            size:30,
        },
    group: 1,
    color:{highlight:'grey', border: 'indigo', background:'black', edges:'indigo'},

    mass: 10,
    borderWidth: 2.5,
    x: 300,
    y: 300,
  },)

var ville = "'''+str(obj["place"])+'''".split(",")
artiste="'''+str(obj["contributor"])+'''".split(",")
origin="'''+str(obj["origin"])+'''".split(",");

            for (i in origin) {
            edges.add({from: origin[i], to: input})};

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
        min: 5,
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
      width: 0.35,
      length:3,
      smooth: {
          enabled:true,
          roundness:0.75,
          type:"dynamic",
          },
    },
    interaction: {
    hover:true,
    tooltipDelay:50,
    }
  };

for (i in points) {

        var origin = (points[i].origin).split(",")
            lat = points[i].lat	//position found
            lon = points[i].lon
            label = points[i].label
            title = points[i].title
            descri = points[i].descripteurs
            artiste = (points[i].contributor).split(",")
            ville = (points[i].place).split(",")
            id = points[i].id
            manuscrit= points[i].manuscrit;

if (id!=input){
            nodes.add(
                {
                  id: id,
                  label: id+' '+label,
                  artiste:artiste,
                  ville:ville,
                  origin:origin,
                  title:label,
                  descri:descri,
                  manuscrit:manuscrit,
                  value: 1,
                  group: 1,
                  color:{highlight:'crimson', hover:'crimson', border: 'beige', background:'darkpurple'},
              
                  mass: 5,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })
};

            for (i in origin) {
            edges.add({from: origin[i], to: id})};

            for (i in artiste) {
            edges.add({from: artiste[i], to:id})};

            for (i in ville) {
            edges.add({from: ville[i], to:id})};

};



var analysednodes = []
nodes.forEach(node => {
    nodes.forEach(node2 => {
    var quotient_list = 0
    for (const o of node2["descri"]) {
        if (node["descri"].includes(o)&&node!=node2&&node["manuscrit"]!=node2["manuscrit"]) {quotient_list+=1}
    }if (node["descri"].length>node2["descri"].length){
      var limite = node["descri"].length*0.75
    } else {
      var limite = node2["descri"].length*0.75
    }
    if (quotient_list>1&&quotient_list>limite&&analysednodes.includes(String(node2["id"]+node["id"]+String(limite)))==false){edges.add({from : node["id"], to: node2["id"], color:'#5353CC'});analysednodes.push(String(node["id"]+node2["id"]+String(limite)))}
    })
})

    function populate (dict){
    for (i in dict) {
        nodes.add(
                {
                  id: dict[i],
                  label: dict[i],
                  title: dict[i],
                  descri:dict[i],
                  ville:"aucune",
                  artiste:"aucun",
                  manuscrit:"aucun",        
                  font:{
                  size:30,
                  },
                  value: 4,
                  group: 1,
                  color:{highlight:'grey', border: 'indigo', background:'#9B93BD'},
                  mass: 9,
                  borderWidth: 1,
                  x: 1,
                  y: 1,
                })

}};

var villes = '''+str(villes_uniques)+''';
var artistes = '''+str(Artistes_uniques)+''';

populate(villes)
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
    script+=str(carto_corrélations(corrélations, input))
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
    
    b = "<div id='résultat'>Erreur de requête.</div>"
    a = render_template('result.html', contenu = b, titre = str(request.form["input"]))

    texte = request.form["input"]

    def requéter(param) :
        texte = request.form["input"]
        requête=[]
        if len(list(texte.split(",")))>1:
          texte = list(texte.split(","))
          if texte[len(texte)-1]=="[and]" or texte[len(texte)-1]==" [and]" :
            for e in texte :
              for i in param :
                score=0
                for key, value in i.items():
                    pattern = e.lower().strip()
                    regex = re.compile("^"+pattern+"$")
                    result = regex.search(str(value).lower())
                    if result :
                        if key != i["title"] and value != i["title"] and key != i["label"] and value != i["label"] :
                            score+=1
                if score==(len(texte)-1) and i not in requête:
                  requête.append(i)
          else :
            for e in texte :
              for i in param :
                for key, value in i.items():
                    pattern = e.lower().strip()
                    regex = re.compile(pattern)
                    result = regex.search(str(value).lower())
                    if result :
                        if key != i["title"] and value != i["title"] and key != i["label"] and value != i["label"] :
                            if i not in requête :
                                requête.append(i)
        else :
          for i in param :
              for key, value in i.items():
                  pattern = texte.lower().strip()
                  regex = re.compile(pattern)
                  result = regex.search(str(value).lower())
                  if result :
                      if key != i["title"] and value != i["title"] and key != i["label"] and value != i["label"] :
                          if i not in requête :
                              requête.append(i)

        #if len(requête) > 200 :
            #requête=requête[:200]

        return requête

    corrélations = requéter(base_images)

    def is_id(param) :
        pattern = request.form["input"]
        for i in param :
                value = i["id"]
                regex = re.compile(pattern)
                result = regex.search(str(value).lower())
                if result :
                    return True

    if request.method == 'POST' and is_id(base_images) is True :
        input = (str(request.form["input"]).replace("^","")).replace("$","")
        d = corrélateur(base_images, input)
        c = render_template('result2.html', script=netgraph_corrélations(base_images,input), contenu = d, titre = str(request.form["input"]))
        return c

    elif request.method == 'POST' and corrélations != [] :
        if len(corrélations)>=1:
            d='<div id="résultat">'+'''</br><div id="map"></div><div id="netgraph"><div id="loadingScreen">Chargement...</div><div id="mynetwork"></div></div></div><br><h2>'''+texte+", "+ str(len(corrélations))+" correspondances."'</h2><div id="résultats">'

            for i in range(len(corrélations)) :
                d+='<a id="compart" href="http://127.0.0.1:5000/item_'+str(corrélations[i]["id"])+'"><img id="résultat_indiv" src="'+str(corrélations[i]["title"])+'" height="410vh" width="auto"><br><div id="cartel">'+str(corrélations[i]["contributor"])+', '+str(corrélations[i]["title"])+" fol."+str(corrélations[i]["folio"])+', '+str(corrélations[i]["date"])+", "+str(corrélations[i]["place"])+".</div></a>"+'''
        '''
                if i % 4 == 0 :
                    d+='</div><br><div id="résultats">'
            d+='</div>'

            return render_template('result.html', script=netgraph(corrélations), contenu = d, titre = str(request.form["input"]))

    else :
        return a

@app.route('/résult', methods = ['POST', 'GET'])
def result2() :
    b = "<div id='résultat'>Erreur de requête.</div>"
    a = render_template('result.html', contenu = b)

    def is_id(param) :
        pattern = request.form["input"]
        for i in param :
            for key, value in i :
                search = re.search(pattern,str(value).lower())
                if search :
                    return True

    if request.method == 'POST' and is_id(base_images) is True :
        input = str(request.form["input"])
        
        d = corrélateur(base_images, input)
        c = render_template('result2.html', script=netgraph_corrélations(base_images,input), contenu = d, titre = str(request.form["input"]))
        return c

    else :
        return a

        
template = Template('''
@app.route('/item_${Idx}', methods = ['POST', 'GET'])
def item_${Idx}():
    input = '${Idx}'
    d = corrélateur(base_images, input)
    c = render_template('result2.html', script=netgraph_corrélations(base_images,input), contenu = d)
    return c''')
print("chargement des pages individuelles")

for i in base_images :
        exec(template.substitute(Idx=i["id"]))


if __name__ == '__main__':
   app.run(debug=True)
