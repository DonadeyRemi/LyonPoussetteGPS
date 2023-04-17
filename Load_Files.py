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

def distance(start_fuv_troncon, end_fuv_troncon, dico_rues):
    """
    Calcule la distance en ligne "droite", distance à vol d'oisieau entre ces 2 identifiants de rues

    Args:
        start_fuv_troncon (tuple): identifiant (FUV,troncon) correspondant au premier point
        end_fuv_troncon (tuple): idientifiant (FUV,troncon) correspondant au deuxième point
        dico_rues (dict): le dictionnaire de tous les identifiants (FUV,troncon) avec leurs propriétés et donc les coordonnées GPS
    Returns:
        float: la distance
    """
    fuv_start= start_fuv_troncon[0]
    troncon_start = start_fuv_troncon[1]
    fuv_end= end_fuv_troncon[0]
    troncon_end = end_fuv_troncon[1]
    
    D = 6371*(math.pi/2 - math.asin(math.sin(dico_rues[fuv_end][troncon_end]['GPS'][0][1])*math.sin(dico_rues[fuv_start][troncon_start]['GPS'][0][1]) + math.cos(dico_rues[fuv_end][troncon_end]['GPS'][0][0]-dico_rues[fuv_start][troncon_start]['GPS'][0][0])*math.cos(dico_rues[fuv_start][troncon_start]['GPS'][0][1])*math.cos(dico_rues[fuv_end][troncon_end]['GPS'][0][1])))
    return D


def a_star(start, goal, rues_adjacentes, dico_rues):
    queue = PriorityQueue()  # Créer une file de priorité pour les noeuds à explorer
    queue.put((0, start))  # Ajouter le tuple (pondération, noeud) à la file 
    came_from = {}  # Créer un dictionnaire pour stocker les parents de chaque noeud exploré
    cost_so_far = {}  # Créer un dictionnaire pour stocker le coût pour atteindre chaque noeud exploré
    came_from[start] =  None # Le noeud de départ n'a pas de parent
    cost_so_far[start] = 0  # Le coût pour atteindre le noeud de départ est 0

    while not queue.empty():
        current = queue.get()[1] #l'indice zéro est celui de priorité
        print(current)
        # Récupérer le noeud avec la plus petite priorité dans la file
        if current == goal: 
            break

        for next_node in rues_adjacentes[current]:# On récupère le tuple coordonées des adj : (lat,lon)
            new_cost = cost_so_far[current] + distance(current, next_node,dico_rues)  # Calculer le coût pour atteindre le voisin en passant par le noeud actuel
            if next_node not in cost_so_far.keys() or  new_cost < cost_so_far[next_node]:
                cost_so_far[next_node] = new_cost  # Mettre à jour le coût pour atteindre le voisin
                priority = new_cost + distance(next_node, goal,dico_rues)  # Calculer la priorité pour le voisin
                queue.put((priority, next_node))  # Ajouter le voisin à la file avec sa nouvelle priorité
                came_from[next_node] = current  # Stocker le noeud actuel comme parent du voisin exploré
    print(came_from, '\n\n')
        
    
    # Pour avoir le parcourt du départ à l'arrivée
    path = [goal]
    while start not in path:
        path.append(came_from[path[-1]])
    path.reverse()
        
    return ("Le chemin le plus court est : ", path,', Pour un distance de ' ,cost_so_far[goal])


if __name__ == "__main__" :
    adj,rue = charger_donnees()
    #print(give_troncon_nearest_gps([4.851479,45.874598],rue))

    print(give_troncon_nearest_address("25_Allée des Hélianthes_Montanay",rue))
    
    """
    for k in adj.keys() :
        if len(adj[k]) == 1 :
            print(k,adj[k])
    """
