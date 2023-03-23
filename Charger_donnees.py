# -*- coding: utf-8 -*-
"""
Created on Thu Mar 23 12:56:41 2023

@author: timhu
"""

import json
f_troncons_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Troncons_trame_viaire.geojson"
f_noeuds_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Noeuds_trame_viaire.geojson"
f_chausses_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Chaussees_et_trottoirs.geojson"

def charger_donnees():
    with open(f_troncons_geojson) as fichier :
        data = json.load(fichier)
    dico_rues = {}    
    for segment in data["features"]:
        co_gps_rue = list(segment["geometry"]["coordinates"])
        rue = segment["properties"]["codefuv"]
        troncon = segment["properties"]["codetroncon"]
        for i in range(len(co_gps_rue)):
            co_gps_rue[i][0] = arrondi(co_gps_rue[i][0], 12)
            co_gps_rue[i][1] = arrondi(co_gps_rue[i][1], 12)

        if rue not in dico_rues.keys():
            dico_rues[rue] = {troncon: {"GPS" : co_gps_rue} }
        else:
            dico_rues[rue][troncon] = {"GPS" : co_gps_rue}
        dico_rues[rue][troncon]["Importance"] = segment["properties"]["importance"]
        dico_rues[rue][troncon]["Type_circulation"] = segment["properties"]["typecirculation"] #exple: pieton, velo, ...
        dico_rues[rue][troncon]["Sens_circulation"] = segment["properties"]["senscirculation"]

    with open(f_chausses_geojson) as fichier :
        data = json.load(fichier) 
    for segment in data["features"]:
        proprietes = segment["properties"]
        troncon = proprietes["codetroncon"]
        rue = proprietes["codefuv"]
        if rue in dico_rues.keys() and troncon in dico_rues[rue].keys():
            #sens circulation?
            dico_rues[rue][troncon]["Nom"] = proprietes["nomvoie1"]
            dico_rues[rue][troncon]["Commune"] = proprietes["commune1"]
            dico_rues[rue][troncon]["Code_postal"] = proprietes["insee1"]
            dico_rues[rue][troncon]["Denomination_route"] = proprietes["denominationroutiere"]
            dico_rues[rue][troncon]["Longueur"] = proprietes.get("longueurreellechaussee",0.0)  #ou "longueurcalculee"
            if dico_rues[rue][troncon]["Longueur"] == "":
                dico_rues[rue][troncon]["Longueur"] = proprietes["longueurcalculee"]
            dico_rues[rue][troncon]["Limitation_vitesse"] = proprietes["limitationvitesse"]
            dico_rues[rue][troncon]["Largeur"] = proprietes.get("largeurcirculeechaussee",0.0)
            dico_rues[rue][troncon]["Pente_max"] = proprietes.get("pentemaximale",-1)
            dico_rues[rue][troncon]["Pente_moy"] = proprietes.get("pentemoyenne",-1)
            dico_rues[rue][troncon]["Revetement_chaussee"] = proprietes["revetementchaussee"]
            dico_rues[rue][troncon]["Revetement_trottoir_D"] = proprietes["revetementtrottoirdroit"]
            dico_rues[rue][troncon]["Largeur_trottoir_D"] = proprietes.get("largeurtrottoirdroit",0.0)
            dico_rues[rue][troncon]["Revetement_trottoir_G"] = proprietes["revetementtrottoirgauche"]
            dico_rues[rue][troncon]["Largeur_trottoir_G"] = proprietes.get("largeurtrottoirgauche",0.0)

    with open(f_noeuds_geojson) as fichier :
        data = json.load(fichier)   
    rues_adjacentes = {}
    for carrefour in data["features"] :
        co_gps_car = list(carrefour["geometry"]["coordinates"])
        co_gps_car[0] = arrondi(co_gps_car[0], 12)
        co_gps_car[1] = arrondi(co_gps_car[1], 12)
        if len(carrefour["properties"]['codefuvcarrefour']) > 0 :
            l_rue_ad = carrefour["properties"]['codefuvcarrefour'].split("+")
            l_rue_troncon_ad = []
            for rue in l_rue_ad :
                if dico_rues.get(f'{rue}',"ERROR") != "ERROR":
                    l_troncons = []
                    for code_tr, proprietes in dico_rues[rue].items():                        
                        if proprietes["GPS"][0] == co_gps_car or proprietes["GPS"][-1] == co_gps_car:
                            l_troncons.append(code_tr)
                    for troncon in l_troncons:
                        l_rue_troncon_ad.append((rue,troncon))                                
            if l_rue_troncon_ad != []:
                for (rue,troncon) in l_rue_troncon_ad:
                    if (rue,troncon) not in rues_adjacentes.keys() :
                        if len(l_rue_troncon_ad) == 1 :
                            rues_adjacentes[(rue,troncon)] = []
                        else:
                            rues_adjacentes[(rue,troncon)] = []
                            for i in l_rue_troncon_ad :
                                if i != (rue,troncon) :
                                    rues_adjacentes[(rue,troncon)].append(i)
                    else:
                        for i in l_rue_troncon_ad :
                            if i != (rue,troncon) :
                                rues_adjacentes[(rue,troncon)].append(i)
    
    #print(dico_rues)
    print(rues_adjacentes)
    #print(len(rues_adjacentes))

def arrondi(nombre, nb_chiffres):
    nombre_str = str(nombre)
    nb_chiffres += nombre_str.index(".") + 1
    if len(nombre_str) > nb_chiffres :
        if int(nombre_str[nb_chiffres]) >= 5:
            modif = str(int(nombre_str[(nb_chiffres-1)]) + 1)
            nombre = float(nombre_str[:nb_chiffres-1]+modif)
        else:
            nombre = float(nombre_str[:nb_chiffres])
    return nombre

charger_donnees() 