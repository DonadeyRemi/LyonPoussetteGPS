#!/usr/bin/python
# -*- encoding: utf8 -*-

import json
import math
from queue import PriorityQueue

f_point_debouche = "point_debouche.geojson"


def charger_donnees():
    f_troncons_geojson = "troncon_trame_viaire.geojson"
    f_noeuds_geojson = "noeud_trame_viaire.geojson"
    f_chausses_geojson = "chaussees_trotoirs.geojson"
    
    with open(f_troncons_geojson,encoding="utf-8") as fichier :
        data = json.load(fichier)
    dico_rues = {}    
    for segment in data["features"]:
        co_gps_rue = list(segment["geometry"]["coordinates"])
        rue = segment["properties"]["codefuv"]
        troncon = segment["properties"]["codetroncon"]
        for i in range(len(co_gps_rue)):
            co_gps_rue[i][0] = round(co_gps_rue[i][0],12) #longitude
            co_gps_rue[i][1] = round(co_gps_rue[i][1],12) #latitude

        if rue not in dico_rues.keys():
            dico_rues[rue] = {troncon: {"GPS" : co_gps_rue} }
        else:
            dico_rues[rue][troncon] = {"GPS" : co_gps_rue}
        dico_rues[rue][troncon]["Importance"] = segment["properties"]["importance"]
        dico_rues[rue][troncon]["Type_circulation"] = segment["properties"]["typecirculation"] #exple: pieton, velo, ...
        dico_rues[rue][troncon]["Sens_circulation"] = segment["properties"]["senscirculation"]

    with open(f_chausses_geojson,encoding='utf-8') as fichier :
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

    with open(f_noeuds_geojson,encoding='utf-8') as fichier :
        data = json.load(fichier)   
    rues_adjacentes = {}
    for carrefour in data["features"] :
        co_gps_car = list(carrefour["geometry"]["coordinates"])
        co_gps_car[0] = round(co_gps_car[0],12)
        co_gps_car[1] = round(co_gps_car[1],12)
        if len(carrefour["properties"]['codefuvcarrefour']) > 0 :
            l_rue_ad = carrefour["properties"]['codefuvcarrefour'].split("+")
            l_rue_troncon_ad = []
            for rue in l_rue_ad :
                if dico_rues.get(f'{rue}',"ERROR") != "ERROR":
                    l_troncons = []
                    for code_tr, proprietes in dico_rues[rue].items():                        
                        if proprietes["GPS"][0] == co_gps_car or proprietes["GPS"][-1] == co_gps_car: #demander pourquoi indice -1 et pas 1 car pas 2 coordonnées gps ? car il y a plusieur co gps pour décrire les virage du troncon
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
    #print(rues_adjacentes)
    #print(len(rues_adjacentes))
    return rues_adjacentes,dico_rues

def give_troncon_nearest_gps(co_gps_user,dico_rues):
    """Trouve le couple troncon + FUV le plus proche des coordonnées gps fournis par l'utilisateur

    Args:
        co_gps_user (tuple): coordonnées GPS (long,lat)
        dico_rues (dict): le dictionnaire contenant les paramètres pour chaques couples troncon+FUV

    Returns:
        dict: {(FUV,troncon) : [co_gps]}
    """
    d_min = 2e+6 #ici on va comparer les distance carré entre elles (et la distance maximale étant la circonsphérence de la terre)
    id_rue_troncon = {(0,0) : co_gps_user}
    for fuv in dico_rues.keys():
        for troncon in dico_rues[fuv].keys():
            for co_gps in dico_rues[fuv][troncon]['GPS'] :
                #d = math.acos(math.sin(math.radians(co_gps_user[0])*math.sin(math.radians(co_gps[0])))) + math.cos(math.radians(co_gps_user[0]))*math.cos(math.radians(co_gps[0]))*math.cos(math.radians(co_gps_user[1]-co_gps[1]))*6371 #formule de la distance entre 2 points sur une sphère
                d = 6371*(math.pi/2 - math.asin(math.sin(co_gps[1])*math.sin(co_gps_user[1]) + math.cos(co_gps_user[0]-co_gps[0])*math.cos(co_gps_user[1])*math.cos(co_gps[1])))
                if d < d_min :
                    id_rue_troncon = {(fuv,troncon) : co_gps}
                    d_min = d


    return id_rue_troncon

def give_troncon_nearest_address(adresse,dico_rues):
    """Permet de retourner le couple identifiant Fuv+Troncon le plus proche de l'addresse donnée, retourne un dictionnare avec tout à 0 si il ne trouve pas

    Args:
        adresse (str): l'addresse sous la forme "numéro_nom_commune"
        dico_rues (dict): le dictionnaire contenant les propriétés de tous les couples d'identifiants

    Returns:
        dict: le couple d'identifiant le plus proche {(fuv,troncon) : [co_gps]}
    """
    nom_voie = adresse.split("_")[1]
    numero = adresse.split("_")[0]
    commune = adresse.split("_")[2]
    id_rue_troncon = {(0,0) : [0,0]} #a changer mais retourne ca si pas trouvé
    for fuv in dico_rues.keys():
        for troncon in dico_rues[fuv].keys():
            try : 
                if dico_rues[fuv][troncon]["Commune"] == commune and dico_rues[fuv][troncon]["Nom"] == nom_voie :
                    id_rue_troncon = {(fuv,troncon) : dico_rues[fuv][troncon]['GPS'][0]} # ici je vais retourner la première co GPS mais à voir plus tard si on essaie de prendre la plus proche avec le numéro
            except KeyError as e :
                print(f"[KeyError] , la clé commune ou nom n'existe pas pour cet identifiant {(fuv,troncon)}")
    return id_rue_troncon 


def dist_between(start_fuv_troncon, end_fuv_troncon, dico_rues):
    """Calcule la distance en ligne "droite", distance à vol d'oisieau entre ces 2 identifiants de rues

    Args:
        start_fuv_troncon (tuple): identifiant (FUV,troncon) correspondant au premier point
        end_fuv_troncon (tuple): idientifiant (FUV,troncon) correspondant au deuxième point
        dico_rues (dict): le dictionnaire de tous les identifiants (FUV,troncon) avec leurs propriétés et donc les coordonnées GPS

    Returns:
        float: la distance à vol d'oiseau en km
    """
        D = 6371*(math.pi/2 - math.asin(math.sin(dico_rues[end_fuv_troncon]['GPS'][1])*math.sin(dico_rues[start_fuv_troncon]['GPS'][1]) + math.cos(dico_rues[end_fuv_troncon]['GPS'][0]-dico_rues[start_fuv_troncon]['GPS'][0])*math.cos(dico_rues[start_fuv_troncon]['GPS'][1])*math.cos(dico_rues[end_fuv_troncon]['GPS'][1])))
        
        return D 

def astar(start_fuv_troncon, end_fuv_troncon, graph): # J'ai pas trouvé de dico dans le bon format : dico d'adjacences par coordonées
    #start et end nodes : tuples
    queue = PriorityQueue() #from queue import PriorityQueue
    queue.put(start_fuv_troncon,0)
    path = {start_fuv_troncon : start_fuv_troncon}
    cost = {start_fuv_troncon : 0}
    
    
    while not queue.empty():
        current_node = queue.get() 
        
        if current_node == end_fuv_troncon :
            return final_dist, path
            print(final_dist, path)
            break
            
        for next_fuv_troncon in graph[current_node]: #pas bon
            new_cost = cost[current_node] + graph[current_node][next_fuv_troncon]
            if next_fuv_troncon not in cost or new_cost < cost[next_fuv_troncon]:
                cost[next_fuv_troncon]= new_cost
                priority = new_cost + dist_between(next_fuv_troncon,end_fuv_troncon)
                queue.put(next_fuv_troncon, priority)
                path[next_fuv_troncon] = current_node
                
    return path, cost



if __name__ == "__main__" :
    adj,rue = charger_donnees()
    #print(give_troncon_nearest_gps([4.851479,45.874598],rue))

    print(give_troncon_nearest_address("25_Allée des Hélianthes_Montanay",rue))
    
    """
    for k in adj.keys() :
        if len(adj[k]) == 1 :
            print(k,adj[k])
    """