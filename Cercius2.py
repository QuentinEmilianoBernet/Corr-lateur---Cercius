from flask import Flask, render_template, request
import pandas as pd
from string import Template

def carto(param) :
    df = pd.DataFrame(param)
    df = df.set_index(df['Cotation'])
    df["lat"] = df["lat"].apply(lambda x: float(x))
    df["lon"] = df["lon"].apply(lambda x: float(x))
    lat = df["lat"]
    lon = df["lon"]
    
    def clean(para) :
        para = para.astype(str)
        para = para.fillna("false")
        return para
    x=0
    artiste = clean(df["Artiste"])
    

    labels = clean(df["Artiste"])
    labels = labels.replace("nan", "artiste inconnu")

    ville = clean(df["Provenance"])
    ville = ville.replace("nan", "provenance exacte inconnue")

    Id = df["Cotation"].fillna("Non indexée")
    Origin = df["Modèle connu ou supposé"]

    df["Nom"] = df["Nom"].replace("Verge", "Vierge")
    df["Nom"] = df["Nom"].replace("Viere", "Vierge")
    df["Nom"] = df["Nom"].replace("adores", "adorés")

    nom = clean(df["Nom"])

    date_label = df["Date(circa)"]

    ddf = df.loc[df["lat"]!=-70.0]
    dddf = df.loc[df["lon"]!=-70.0]

    ddf = ddf['lat'][:3]
    dddf = dddf['lon'][:3]

    meanlat = ddf.describe()
    meanlon = dddf.describe()
    meanlat = meanlat[1]
    meanlon = meanlon[1]
    descri = df["descripteurs"].fillna(False).astype(str)


    carto_dict = "["
    x=0
    for i in range(len(df)):
        carto_dict += '''{loc:['''+str(lat[x])+","+str(lon[x])+'''], descri:"'''+str(descri[x])+'''", ville:"'''+str(ville[x])+'''", artiste:"'''+str(artiste[x])+'''", label:"'''+str(nom[x]).replace('"',"")+", "+str(ville[x])+'''.", origin:"'''+str(Origin[x])+'''"},
'''
        x+=1
    carto_dict+="]"
    

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
    zoom: 7,
    center : ['''+str(meanlat)+","+str(meanlon)+''']});

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

        var points ='''+carto_dict+'''


        for(i in points) {
            var Origin = points[i].origin,	//value searched
            loc = points[i].loc,		//position found
            label = points[i].label
            descri = points[i].descri
            artiste = points[i].artiste
            ville = points[i].ville
            
            var marker = new L.marker (new L.latLng(loc), {label:label, icon:blur2, opacity: 0.4, properties:{label:label, Origin:Origin, loc:loc}});
            marker.bindPopup(String(artiste)+", "+String(label));
            marker.addTo(map);}
                
                
                
                '''




    return script
def carto_corrélations(param) :
    df = pd.DataFrame(param)
    df=df[:11]
    df["lat"] = df["lat"].apply(lambda x: float(x[0]))
    df["lon"] = df["lon"].apply(lambda x: float(x[0]))
    lat = df["lat"]
    lon = df["lon"]
    
    x=0
    y=2
    artiste = df["Artiste"]

    labels = df["Artiste"]
    labels = labels.replace("nan", "artiste inconnu")

    ville = df["Ville"]
    ville = ville.replace("nan", "provenance exacte inconnue")

    Id = df["Id"].fillna("Non indexée")
    Origin = df["Origin"]

    df["Nom"] = df["Nom"].replace("Verge", "Vierge")
    df["Nom"] = df["Nom"].replace("Viere", "Vierge")
    df["Nom"] = df["Nom"].replace("adores", "adorés")

    nom = df["Nom"]

    date_label = df["Date"]

    ddf = df.loc[df["lat"]!=-70.0]
    dddf = df.loc[df["lon"]!=-70.0]

    ddf = ddf['lat'][:3]
    dddf = dddf['lon'][:3]

    meanlat = ddf.describe()
    meanlon = dddf.describe()
    meanlat = meanlat[1]
    meanlon = meanlon[1]

    descri = df["descripteurs"].fillna(False)


    carto_dict = "["

    for i in range(len(df)):
        carto_dict += '''{loc:['''+str(lat[x])+","+str(lon[x])+'''], descri:"'''+str(descri[x][0])+'''", ville:"'''+str(ville[x][0])+'''", artiste:"'''+str(artiste[x][0])+'''", label:"'''+str(nom[x][0]).replace('"',"")+", "+str(ville[x][0])+'''.", origin:"'''+str(Origin[x][0])+'''"},
'''
        x+=1
    carto_dict+="]"

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
    center : ['''+str(meanlat)+","+str(meanlon)+''']});

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

        var points ='''+carto_dict+'''


        for(i in points) {
            var Origin = points[i].origin,	//value searched
                loc = points[i].loc,		//position found
                label = points[i].label

            
            var marker = new L.marker (new L.latLng(loc), {label:label, icon:blur2, opacity: 0.3, properties:{label:label, Origin:Origin, loc:loc}});
            marker.bindPopup(label);
            marker.addTo(map);} '''



    return script

def clean_ville(param) :
    param = param.replace(" ?", "")
    param = param.replace(" (environs)", "")
    param = param.replace(".", "")
    for i in param :
        if i is False or i == "False":
            i = "Ville inconnue"
    return param

def clean(param) :
    param = param.astype(str)
    param = param.fillna("false")
    return param

def corrélateur(df,valeur) :

    x=0
    y=2
    lat = df["lat"].fillna(-70)
    df["Approximation"] = df["Approximation"].fillna(0.0)
    lon = df["lon"].fillna(-70)
    df['Coordonnées'] = df[df.columns[11:13]].apply(
    lambda x: ', '.join(x.dropna().astype(str)),
    axis=1
    )
    clean(df["Artiste"])
    nom = clean(df["Nom"])

    labels = clean(df["Artiste"])
    labels = labels.replace("nan", "artiste inconnu")

    ville = clean(df["Provenance"])
    ville = ville.replace("nan", "provenance exacte inconnue")

    Id = df["Cotation"].fillna("Non indexée")
    Origin = df["Modèle connu ou supposé"]

    df["Nom"] = df["Nom"].replace("Verge", "Vierge")
    df["Nom"] = df["Nom"].replace("Viere", "Vierge")
    df["Nom"] = df["Nom"].replace("adores", "adorés")

    places = df["Coordonnées"]
    degré = df["Approximation"].astype(int)
    date_label = clean(df["Date(circa)"])
    date_label = date_label.replace("nan", "date précise inconnue")
    date_deb = clean(df["Date_deb"])
    date_deb = date_deb.apply(lambda x: x.replace(".0", ""))
    date_fin = clean(df["Date_fin"])
    date_fin = date_fin.apply(lambda x: x.replace(".0", ""))

    allaitante = clean(df["Lactans"])
    parapet = clean(df["Parapet"])
    apocalypse = clean(df["Apocalypse"])
    Localisation = clean(df["Localisation"])
    Dieu = clean(df["Dieu (père ou saint-esprit)"])
    Anges = clean(df["Anges"])
    Direction = clean(df["Direction"])
    Direction = Direction.replace("Direction", "Droite")
    Voile = clean(df["Voile"])
    Couronne = clean(df["Couronne"])
    Coussin = clean(df["Coussin"])
    Saints = clean(df["Saints"])

    img = df["Img"]
    img = img.fillna(False)
    acces = df["acces"]
    acces = acces.fillna(False)

    ddf = lat
    dddf = lon

    meanlat = ddf.describe()
    meanlon = dddf.describe()
    meanlat = meanlat[1]
    meanlon = meanlon[1] 

    descri = df["descripteurs"].fillna(False)
    
    z=0
    a=0
    corrélations = []
    corrélation = {"Nom":[], "descripteurs":[], "lat":[], "lon":[], "Quotient":[],"url":[], "Id":[], "Origin":[], "Ville":[], "Titre":[], "Date":[], "Artiste":[]}

    x=int(valeur)+1

    for i in range(190) :
        z = z+1
        if Id[x]!=Id[z] :
            if str(Origin[z]) != 'nan' or str(Origin[x]) != 'nan':
                if  str(Id[x])==str(Origin[z]) or str(Id[z])==str(Origin[x]) or str(Origin[x])==str(Origin[z]):
                    a+=4
            if  str(labels[x])==str(labels[z]) or str(labels[x])==str(labels[z]) :
                    a+=3
            if  str(ville[x])==str(ville[z]) and ville[x] != "provenance exacte inconnue":
                    a+=1.5

            if img[z] is not False :

                if int(date_deb[x])==int(date_deb[z]) :
                        corrélation["Nom"].append(str(Id[z])+", "+ str(labels[z])+", "+str(nom[z])+", "+str(date_label[z])+".")
                        corrélation["Quotient"].append(float(a+0.5))
                        corrélation["url"].append(df.loc[df.index[Id==Id[z]].tolist()[0], "Img"])
                        corrélation["Id"].append(Id[z].replace("VdH", ""))
                        corrélation["Origin"].append(str(Origin[z]))
                        corrélation["Ville"].append(clean_ville(ville[z]))
                        corrélation["Artiste"].append(labels[z])
                        corrélation["Titre"].append(str(nom[z])+", "+str(date_label[z]+"."))
                        corrélation["Date"].append(str(date_label[z]))
                        corrélation["lat"].append(str(lat[z]))
                        corrélation["lon"].append(str(lon[z]))
                        corrélation["descripteurs"].append(str(descri[z]))


                elif int(date_deb[x])<int(date_deb[z]) :
                    if int(date_deb[z])-int(date_deb[x]) <= 50 :
                        corrélation["Nom"].append(str(Id[z])+", "+ str(labels[z])+", "+str(nom[z])+", "+str(date_label[z])+".")
                        corrélation["Quotient"].append(float(a-(int(date_deb[z])-int(date_deb[x]))*0.01))
                        corrélation["url"].append(df.loc[df.index[Id==Id[z]].tolist()[0], "Img"])
                        corrélation["Id"].append(Id[z].replace("VdH", ""))
                        corrélation["Origin"].append(str(Origin[z]))
                        corrélation["Ville"].append(clean_ville(ville[z]))
                        corrélation["Artiste"].append(labels[z])
                        corrélation["Titre"].append(str(nom[z])+", "+str(date_label[z]+"."))
                        corrélation["Date"].append(str(date_label[z]))
                        corrélation["lat"].append(str(lat[z]))
                        corrélation["lon"].append(str(lon[z]))
                        corrélation["descripteurs"].append(str(descri[z]))


                elif int(date_deb[z])<int(date_deb[x]) :
                    if int(date_deb[x])-int(date_deb[z]) <= 50 :
                        corrélation["Nom"].append(str(Id[z])+", "+ str(labels[z])+", "+str(nom[z])+", "+str(date_label[z])+".")
                        corrélation["Quotient"].append(float(a-(int(date_deb[x])-int(date_deb[z]))*0.01))
                        corrélation["url"].append(df.loc[df.index[Id==Id[z]].tolist()[0], "Img"])
                        corrélation["Id"].append(Id[z].replace("VdH", ""))
                        corrélation["Origin"].append(str(Origin[z]))
                        corrélation["Ville"].append(clean_ville(ville[z]))
                        corrélation["Artiste"].append(labels[z])
                        corrélation["Titre"].append(str(nom[z])+", "+str(date_label[z]+"."))
                        corrélation["Date"].append(str(date_label[z]))
                        corrélation["lat"].append(str(lat[z]))
                        corrélation["lon"].append(str(lon[z]))
                        corrélation["descripteurs"].append(str(descri[z]))


                else :
                        corrélation["Nom"].append(str(Id[z])+", "+ str(labels[z])+", "+str(nom[z])+", "+str(date_label[z])+".")
                        corrélation["Quotient"].append(float(a-2))
                        corrélation["url"].append(df.loc[df.index[Id==Id[z]].tolist()[0], "Img"])
                        corrélation["Id"].append(Id[z].replace("VdH", ""))
                        corrélation["Origin"].append(str(Origin[z]))
                        corrélation["Ville"].append(clean_ville(ville[z]))
                        corrélation["Artiste"].append(labels[z])
                        corrélation["Titre"].append(str(nom[z])+", "+str(date_label[z]+"."))
                        corrélation["Date"].append(str(date_label[z]))
                        corrélation["lat"].append(str(lat[z]))
                        corrélation["lon"].append(str(lon[z]))
                        corrélation["descripteurs"].append(str(descri[z]))



            a=0

            if corrélation["Nom"] != [] :
                corrélation = dict(corrélation)
                corrélations.append(corrélation)
            corrélation = {"Nom":[], "descripteurs":[], "lat":[], "lon":[], "Quotient":[],"url":[],"Id":[],"Origin":[], "Ville":[], "Titre":[], "Date":[], "Artiste":[]}
        
    z=0
    
    url = str(img[x])
    
    def imprime() :
        corrélations.sort(key=lambda x:x["Quotient"][0], reverse = True)
        if img[x] is not False :

            a = '<div id="résultat"><div id="map"></div><div id="résultat1"><img src="'+url+'" height="auto" width="350px"><br><br>'
            a += "Vous avez choisi la "+str(Id[x])+", "+str(nom[x])+" par "+str(labels[x])+", "+str(date_label[x])+'. Provenance : '+str(ville[x])+'. </div><div id="netgraph"><div id="loadingScreen">Chargement en cours...</div><div id="mynetwork"></div></div></div><br><br>'
        
        else :
            a = '<div id="résultat"><div id="map"></div><div id="résultat1">'
            a += 'Vous avez choisi la '+str(Id[x])+", "+' par '+str(labels[x])+', '+str(date_label[x])+' (Pas de reproduction). Provenance : '+str(ville[x])+'. </div><div id="netgraph"><div id="loadingScreen">Chargement en cours...</div><div id="mynetwork"></div></div></div><br><br>'
        z = -1
        if len(corrélations)<=12 :
            longueur = len(corrélations)
        else :
            longueur = 12
        a += '<div id="résultats">'
        for i in range(longueur) :
            z+=1
            a += '<a id="compart" href="http://127.0.0.1:5000/VdH'+corrélations[z]["Id"][0]+'"> <img id="résultat_indiv" src="'+corrélations[z]["url"][0]+'" height="410vh" width="auto"><br><div id="cartel"> Proche de la '+corrélations[z]["Nom"][0]+"</div></a><br>"+'''
    '''
            #if z == 5 or z == 10 or z == 15 or z == 20:
            #    a += '</div><br><div id="résultats">'
            if i == 5 or i == 11 :
                    a+='</div><br><div id="résultats">'
        a += "</div>"
        return a
    b = imprime()

    def résultat () :
        if corrélations != [] and url is not False:
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

def netgraph(requête) :

    texte = str(clean_data(request.form["input"]))

    input = clean_data(texte)

    lat = requête["lat"].fillna(-70)
    requête["Approximation"] = requête["Approximation"].fillna(0.0)
    lon = requête["lon"].fillna(-70)
    requête['Coordonnées'] = requête[requête.columns[11:13]].apply(
    lambda x: ', '.join(x.dropna().astype(str)),
    axis=1
    )
    clean(requête["Artiste"])
    nom = clean(requête["Nom"])

    labels = clean(requête["Artiste"])
    labels = labels.replace("nan", "artiste inconnu")
    labels = labels.replace("False", "artiste inconnu")

    ville = clean(requête["Provenance"])
    ville = ville.replace("nan", "provenance exacte inconnue")
    ville = ville.replace("False", "provenance exacte inconnue")

    Id = requête["Cotation"].fillna("Non indexée")
    Origin = requête["Modèle connu ou supposé"]

    requête["Nom"] = requête["Nom"].replace("Verge", "Vierge")
    requête["Nom"] = requête["Nom"].replace("Viere", "Vierge")
    requête["Nom"] = requête["Nom"].replace("adores", "adorés")

    places = requête["Coordonnées"]
    degré = requête["Approximation"].astype(int)
    date_label = clean(requête["Date(circa)"])
    date_label = date_label.replace("nan", "date précise inconnue")
    date_deb = clean(requête["Date_deb"])
    date_deb = date_deb.apply(lambda x: x.replace(".0", ""))
    date_fin = clean(requête["Date_fin"])
    date_fin = date_fin.apply(lambda x: x.replace(".0", ""))


    img = requête["Img"]
    img = img.fillna(False)
    acces = requête["acces"]
    acces = acces.fillna(False)

    ddf = lat
    dddf = lon

    meanlat = ddf.describe()
    meanlon = dddf.describe()
    meanlat = meanlat[1]
    meanlon = meanlon[1] 

    descri = requête["descripteurs"].fillna(False)

    script='''

<script type="text/javascript">

const input = "'''+input+'''"
'''

    graph_dict = "["

    for i in range(len(requête)):
        graph_dict += '''{id:"'''+str(Id.iloc[i])+'''", descri:"'''+str(descri.iloc[i])+'''", ville:"'''+str(ville.iloc[i])+'''", artiste:"'''+str(labels.iloc[i])+'''", label:"'''+str(nom.iloc[i]).replace('"',"")+", "+str(date_label.iloc[i])+", "+str(ville.iloc[i])+'''.", origin:"'''+str(Origin.iloc[i])+'''"},
'''
    graph_dict+="]"
    villes_uniques = list(clean_ville(requête.Provenance).unique())
    Modèles = list(clean(requête.Cotation).unique())
    Artistes_uniques = list(clean(requête.Artiste).unique())
    descripteurs = list(clean(requête.descripteurs).unique()) 
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

  nodes.add(  {
    id: input,
    label: input,
    title: input,
    value: 5,
    font:{
            size:30,
        },
    group: 1,
    color:{highlight:'grey', border: 'indigo', background:'black'},
    physics: true,
    mass: 33,
    borderWidth: 1,
    x: 100,
    y: 0,
  },)

  const options = {
    nodes: {
      shape: "dot",
      scaling: {
        min: 10,
        max: 30,
      },
      font: {
        size: 12,
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
      hideEdgesOnDrag: false,
      tooltipDelay: 50,
      hover:true,
    }
  };

for (i in points) {

var origin = points[i].origin	//value searched
            loc = points[i].loc	//position found
            label = points[i].artiste+", "+points[i].label
            title = points[i].title
            descri = points[i].descri
            artiste = points[i].artiste
            ville = points[i].ville
            id = points[i].id;

if (id!=input){
            nodes.add(
                {
                  id: id,
                  label: id,
                  artiste:artiste,
                  ville:ville,
                  origin:origin,
                  title:label,
                  descri:descri,
                  value: 1,
                  group: 1,
                  color:{highlight:'crimson', hover:'crimson', border: 'beige', background:'darkpurple'},
                  physics: true,
                  mass: 15,
                  borderWidth: 1,
                  x: 0,
                  y: 0,
                })
};
            edges.add({from: input, hidden: true, length:33, to: id})

            if (origin != "False") {
            edges.add({from: origin, to: id})}

            if (artiste != "False") {
            edges.add({from: artiste, to:id});}

            if (ville != "False") {
            edges.add({from: ville, to:id});}

};

    function populate (dict){
    for (i in dict) {
    if (dict[i] != input && dict[i] != "False") {
        nodes.add(
                {
                  id: dict[i],
                  label: dict[i],
                  title: dict[i],
                  descri:dict[i],
                  value: 4,
                  group: 1,
                  color:{highlight:'grey', border: 'indigo', background:'#9B93BD'},
                  physics: true,
                  mass: 5,
                  borderWidth: 1,
                  x: 0,
                  y: 0,
                })

}}
    
};

var villes = '''+str(villes_uniques)+''';
var artistes = '''+str(Artistes_uniques)+''';
var descri = '''+str(descripteurs)+''';

populate(villes)
populate(artistes)

const netw = new vis.Network(container, data, options).once('beforeDrawing', function(e) {

        netw.focus("'''+str(input)+'''",{
            scale:0.14,
            });

            });

netw.on('dblclick', function(e) {

    if (this.style.width !="200%"){
        this.style.width ="200%"
        }
    else {
        this.style.width ="100%"
        }
    });



'''

    script+=str(carto(requête))
    script+='''

</script>'''

    return script

def netgraph_corrélations(df,valeur) :

    def clean(param) :
            param = param.astype(str)
            param = param.fillna("false")
            return param
    x=0
    y=2
    lat = df["lat"].fillna(-70)
    df["Approximation"] = df["Approximation"].fillna(0.0)
    lon = df["lon"].fillna(-70)
    df['Coordonnées'] = df[df.columns[11:13]].apply(
    lambda x: ', '.join(x.dropna().astype(str)),
    axis=1
    )
    clean(df["Artiste"])
    nom = clean(df["Nom"])

    labels = clean(df["Artiste"])
    labels = labels.replace("nan", "artiste inconnu")

    ville = clean(df["Provenance"])
    ville = ville.replace("nan", "provenance exacte inconnue")

    Id = df["Cotation"].fillna("Non indexée")
    Origin = df["Modèle connu ou supposé"].fillna('nan')

    df["Nom"] = df["Nom"].replace("Verge", "Vierge")
    df["Nom"] = df["Nom"].replace("Viere", "Vierge")
    df["Nom"] = df["Nom"].replace("adores", "adorés")

    places = df["Coordonnées"]
    degré = df["Approximation"].astype(int)
    date_label = clean(df["Date(circa)"])
    date_label = date_label.replace("nan", "date précise inconnue")
    date_deb = clean(df["Date_deb"])
    date_deb = date_deb.apply(lambda x: x.replace(".0", ""))
    date_fin = clean(df["Date_fin"])
    date_fin = date_fin.apply(lambda x: x.replace(".0", ""))

    img = df["Img"]
    img = img.fillna(False)
    acces = df["acces"]
    acces = acces.fillna(False)

    ddf = lat
    dddf = lon

    meanlat = ddf.describe()
    meanlon = dddf.describe()
    meanlat = meanlat[1]
    meanlon = meanlon[1] 


    descri = clean(df["descripteurs"])

    z=0
    a=0
    corrélations = []
    corrélation = {"Nom":[], "descripteurs":[], "lat":[], "lon":[], "Quotient":[],"url":[], "Id":[], "Origin":[], "Ville":[], "Titre":[], "Date":[], "Artiste":[]}




    x=int(valeur)+1

    for i in range(190) :
        z = z+1
        if Id[x]!=Id[z] :
            if str(Origin[z]) != 'nan' or str(Origin[x]) != 'nan':
                if  str(Id[x])==str(Origin[z]) or str(Id[z])==str(Origin[x]) or str(Origin[x])==str(Origin[z]):
                    a+=4
            if  str(labels[x])==str(labels[z]) or str(labels[x])==str(labels[z]) :
                a+=3
            if  str(ville[x])==str(ville[z]) and ville[x] != "provenance exacte inconnue":
                a+=1.5

            if img[z] is not False :

                if int(date_deb[x])==int(date_deb[z]) :
                        corrélation["Nom"].append(str(Id[z])+", "+ str(labels[z])+", "+str(nom[z])+", "+str(date_label[z])+".")
                        corrélation["Quotient"].append(float(a+0.5))
                        corrélation["url"].append(df.loc[df.index[Id==Id[z]].tolist()[0], "Img"])
                        corrélation["Id"].append(Id[z].replace("VdH", ""))
                        corrélation["Origin"].append(str(Origin[z]))
                        corrélation["Ville"].append(clean_ville(ville[z]))
                        corrélation["Artiste"].append(labels[z])
                        corrélation["Titre"].append(str(nom[z]))
                        corrélation["Date"].append(str(date_label[z]))
                        corrélation["lat"].append(str(lat[z]))
                        corrélation["lon"].append(str(lon[z]))
                        corrélation["descripteurs"].append(str(descri[z]))


                elif int(date_deb[x])<int(date_deb[z]) :
                    if int(date_deb[z])-int(date_deb[x]) <= 50 :
                        corrélation["Nom"].append(str(Id[z])+", "+ str(labels[z])+", "+str(nom[z])+", "+str(date_label[z])+".")
                        corrélation["Quotient"].append(float(a-(int(date_deb[z])-int(date_deb[x]))*0.01))
                        corrélation["url"].append(df.loc[df.index[Id==Id[z]].tolist()[0], "Img"])
                        corrélation["Id"].append(Id[z].replace("VdH", ""))
                        corrélation["Origin"].append(str(Origin[z]))
                        corrélation["Ville"].append(clean_ville(ville[z]))
                        corrélation["Artiste"].append(labels[z])
                        corrélation["Titre"].append(str(nom[z]))
                        corrélation["Date"].append(str(date_label[z]))
                        corrélation["lat"].append(str(lat[z]))
                        corrélation["lon"].append(str(lon[z]))
                        corrélation["descripteurs"].append(str(descri[z]))


                elif int(date_deb[z])<int(date_deb[x]) :
                    if int(date_deb[x])-int(date_deb[z]) <= 50 :
                        corrélation["Nom"].append(str(Id[z])+", "+ str(labels[z])+", "+str(nom[z])+", "+str(date_label[z])+".")
                        corrélation["Quotient"].append(float(a-(int(date_deb[x])-int(date_deb[z]))*0.01))
                        corrélation["url"].append(df.loc[df.index[Id==Id[z]].tolist()[0], "Img"])
                        corrélation["Id"].append(Id[z].replace("VdH", ""))
                        corrélation["Origin"].append(str(Origin[z]))
                        corrélation["Ville"].append(clean_ville(ville[z]))
                        corrélation["Artiste"].append(labels[z])
                        corrélation["Titre"].append(str(nom[z]))
                        corrélation["Date"].append(str(date_label[z]))
                        corrélation["lat"].append(str(lat[z]))
                        corrélation["lon"].append(str(lon[z]))
                        corrélation["descripteurs"].append(str(descri[z]))


                else :
                        corrélation["Nom"].append(str(Id[z])+", "+ str(labels[z])+", "+str(nom[z])+", "+str(date_label[z])+".")
                        corrélation["Quotient"].append(float(a-2))
                        corrélation["url"].append(df.loc[df.index[Id==Id[z]].tolist()[0], "Img"])
                        corrélation["Id"].append(Id[z].replace("VdH", ""))
                        corrélation["Origin"].append(str(Origin[z]))
                        corrélation["Ville"].append(clean_ville(ville[z]))
                        corrélation["Artiste"].append(labels[z])
                        corrélation["Titre"].append(str(nom[z]))
                        corrélation["Date"].append(str(date_label[z]))
                        corrélation["lat"].append(str(lat[z]))
                        corrélation["lon"].append(str(lon[z]))
                        corrélation["descripteurs"].append(str(descri[z]))



            a=0
            if corrélation["Nom"] != [] :
                corrélation = dict(corrélation)
                corrélations.append(corrélation)
            corrélation = {"Nom":[], "descripteurs":[], "lat":[], "lon":[], "Quotient":[],"url":[],"Id":[], "Origin":[], "Ville":[], "Titre":[], "Date":[], "Artiste":[]}


    graph_dict = "["
    
    for i in range(len(corrélations)):
        graph_dict += '''{id:"'''+str(corrélations[i]["Id"][0])+'''", descri:"'''+str(corrélations[i]["descripteurs"][0])+'''", ville:"'''+str(corrélations[i]["Ville"][0])+'''", artiste:"'''+str(corrélations[i]["Artiste"][0])+'''", label:"'''+str(corrélations[i]["Titre"][0]).replace('"',"")+", "+str(corrélations[i]["Ville"][0])+'''.", origin:"'''+str(corrélations[i]["Origin"][0])+'''"},
'''
    graph_dict+="]" 

    z=0
    corrélations.sort(key=lambda x:x["Quotient"][0], reverse = True)

    villes_uniques = []
    Modèles = []
    Artistes_uniques = []
    descripteurs = []

    for i in range(len(corrélations)) :
        if corrélations[i]["Ville"][0] not in villes_uniques and corrélations[i]["Ville"][0] != "provenance exacte inconnue":
            villes_uniques.append(corrélations[i]["Ville"][0])
        if corrélations[i]["Id"][0] not in Modèles :
            Modèles.append(corrélations[i]["Id"][0])
        if corrélations[i]["Artiste"][0] not in Artistes_uniques and corrélations[i]["Artiste"][0] != "Anonyme":
            Artistes_uniques.append(corrélations[i]["Artiste"][0])

        descr = corrélations[i]["descripteurs"][0]

        for e in range(len(descr)) :
            if descr[e] not in descripteurs and descr[e] is not False :
                descripteurs.append(descr[e])
                


    villes_uniques = list(set(villes_uniques))
    Modèles = list(set(Modèles))
    Artistes_uniques = list(set(Artistes_uniques))
    descripteurs = list(set(descripteurs))
    #descripteurs = set(itertools.chain.from_iterable(descripteurs))

    x=int(valeur)+1

    url = str(img[x])
    ville = str(ville[x])
    artiste = str(labels[x])
    Orig = str(Origin[x])
    descri = str(descri[x])
    input=str(Id[x])

    print(input)

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
    title: "'''+str(Id[x])+", "+ str(labels[x])+", "+str(nom[x])+", "+str(date_label[x])+"."+'''",
    ville:"'''+ville+'''",
    artiste:"'''+artiste+'''",
    descri:"'''+descri+'''",
    value: 5,
    font:{
            size:30,
        },
    group: 1,
    color:{highlight:'grey', border: 'indigo', background:'black'},
    physics: true,
    mass: 29,
    borderWidth: 1,
    x: 100,
    y: 0,
  },)

    edges.add({from: "'''+Orig+'''", to: input})
    edges.add({from: "'''+artiste+'''", to:input});
    edges.add({from: "'''+ville+'''", to:input});

  var container = document.getElementById("mynetwork");

  const options = {
    nodes: {
      shape: "dot",
      scaling: {
        min: 10,
        max: 30,
      },
      font: {
        size: 12,
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
      hideEdgesOnDrag: false,
      tooltipDelay: 50,
      hover:true,
    }
  };

for (i in points) {

var origin = points[i].origin	//value searched
            loc = points[i].loc	//position found
            label = points[i].artiste+", "+points[i].label
            title = points[i].title
            descri = points[i].descri
            artiste = points[i].artiste
            ville = points[i].ville
            id = "VdH"+points[i].id;

if (id!=input){
            nodes.add(
                {
                  id: id,
                  label: id,
                  artiste:artiste,
                  ville:ville,
                  origin:origin,
                  title:label,
                  descri:descri,
                  value: 1,
                  group: 1,
                  color:{highlight:'crimson', hover:'crimson', border: 'beige', background:'darkpurple'},
                  physics: true,
                  mass: 15,
                  borderWidth: 1,
                  x: 0,
                  y: 0,
                })
};
            edges.add({from: origin, to: id})
            edges.add({from: artiste, to:id});
            edges.add({from: ville, to:id});

};

    function populate (dict){
    for (i in dict) {
        nodes.add(
                {
                  id: dict[i],
                  label: dict[i],
                  title: dict[i],
                  descri:dict[i],
                  value: 4,
                  group: 1,
                  color:{highlight:'grey', border: 'indigo', background:'#9B93BD'},
                  physics: true,
                  mass: 5,
                  borderWidth: 1,
                  x: 0,
                  y: 0,
                })

}};

var villes = '''+str(villes_uniques)+''';
var artistes = '''+str(Artistes_uniques)+''';
var descri = '''+str(descripteurs)+''';

populate(villes)
populate(artistes)

const data = {
    nodes: nodes,
    edges: edges
  };


var netw = new vis.Network(container, data, options).once('beforeDrawing', function(e) {

        netw.focus("'''+str(input)+'''",{
            scale:0.4,
            });

            });
    
netw.focus(input,{
      scale:0.4,
      });  


netw.on('dblclick', function(e) {

    if (this.style.width !="200%"){
        this.style.width ="200%"
        }
    else {
        this.style.width ="100%"
        }
    });

'''
    script+=str(carto_corrélations(corrélations))
    script+='''



var villes = '''+str(villes_uniques)+''',
artistes = '''+str(Artistes_uniques)+'''
descri = '''+str(descripteurs)+'''

</script>'''
    
    return script

app = Flask(__name__)
@app.route('/')


def home():
    return render_template('base.html')

@app.route('/corrélateur', methods = ['POST', 'GET'])
def result() :
    
    b = "<div id='résultat'>Erreur de requête, entrez uniquement un nombre entre 1 et 190 ou un nom répertorié dans la base.</div>"
    a = render_template('result.html', contenu = b, titre = str(request.form["input"]))
    df = pd.read_csv(r"C:\Users\uuuu\Documents\mdln.csv")
    
    df = df.fillna(False)
    df["Nom"] = df["Nom"].replace("Verge","Vierge")

    for a in range(len(df)) :
        for name, value in df.items() :
            x=""
            if df.loc[a, str(name)] is True:
                    x += str(name)+","

    d=""

    texte = str(clean_data(request.form["input"]))

    def requéter(df) :
        result = "none"
        dff = df.loc[df['Nom']=="uuuu"]

        for name, values in df.items():
            col = df[str(name)].astype(str)
            pattern = texte
            result = df.loc[col.str.contains(pattern)]
            if result.empty is False :
                dff = pd.concat([dff, result])
                dff.set_index('Cotation')
                dff = dff.drop_duplicates()

        return dff

    requête = requéter(df)

    if request.method == 'POST' and str(requête) != "none" :
        if len(requête)>=1:
            d='<div id="résultat">'+'''</br><div id="map"></div><div id="netgraph"><div id="loadingScreen">Chargement en cours...</div><div id="mynetwork"></div></div></div><br><h2>'''+texte+'</h2><div id="résultats">'

            for i in range(len(requête)) :
                if requête["Img"].iloc[i] is not False :
                    d+='<a id="compart" href="http://127.0.0.1:5000/'+str(requête["Cotation"].iloc[i])+'"><img id="résultat_indiv" src="'+str(requête["Img"].iloc[i])+'" height="410vh" width="auto"><br><div id="cartel">'+str(requête["Artiste"].iloc[i])+', '+str(requête["Nom"].iloc[i])+', '+str(requête["Date(circa)"].iloc[i])+", "+str(requête["Provenance"].iloc[i])+".</div></a>"+'''
        '''
                if i == 6 or i == 11 or i == 16 or i == 21 or i == 26 :
                    d+='</div><br><div id="résultats">'
            d+='</div>'
            return render_template('result.html', script=netgraph(requête), contenu = d, titre = str(request.form["input"]))

    elif request.method == 'POST' and (request.form["input"].replace("VdH"," ")).isdigit() is True :
        valeur = int(request.form["input"])
        df = pd.read_csv(r"C:\Users\uuuu\Documents\mdln.csv")
        d = corrélateur(df, valeur)
        c = render_template('result2.html', script=netgraph_corrélations(df,valeur), contenu = d, titre = str(request.form["input"]))
        return c

    else :
        return a

@app.route('/résult', methods = ['POST', 'GET'])
def result2() :
    b = "<div id='résultat'>Erreur de requête, entrez uniquement un nombre entre 1 et 190 ou un nom répertorié dans la base.</div>"
    a = render_template('result.html', contenu = b)
    if request.method == 'POST' and request.form["input"].isdigit() is True :
        valeur = int(str(request.form['input']))
        df = pd.read_csv(r"C:\Users\uuuu\Documents\mdln.csv")

        for a in range(len(df)) :
            for name, value in df.items() :
                x=""
                if df.loc[a, str(name)] is True:
                        x += str(name)+","
        
        d = corrélateur(df, valeur)
        c = render_template('result.html', script=netgraph_corrélations(df,valeur), contenu = d, titre = str(request.form["input"]))
        return c

    else :
        return a
x=0

template = Template('''
@app.route('/${Idx}', methods = ['POST', 'GET'])
def ${Idx}():
    valeur = int('${Idx}'.replace("VdH",""))
    d = corrélateur(df, valeur)
    c = render_template('result2.html', script=netgraph_corrélations(df,valeur), contenu = d)
    return c''')
        
for i in range(190) :
    
    x+=1
    df = pd.read_csv(r"C:\Users\uuuu\Documents\mdln.csv")
    Id = df["Cotation"].fillna("Non indexée")
    exec(template.substitute(Idx=Id[x]))

if __name__ == '__main__':
   app.run(debug=True)
