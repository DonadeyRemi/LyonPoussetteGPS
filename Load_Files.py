# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:20:19 2023

@author: timhu
"""

import json
import math
from queue import PriorityQueue

f_point_debouche = "point_debouche.geojson"

def charger_donnees():
    arrondi_gps = 12
    f_troncons_geojson = "troncon_trame_viaire.geojson"
    f_chausses_geojson = "chaussees_trotoirs.geojson"
    f_point_debouche = "point_debouche.geojson"
   
    with open(f_troncons_geojson,encoding='utf-8') as fichier :
        data = json.load(fichier)
    dico_noeuds = {}
    dico_rues = {} 
    for segment in data["features"]:
        co_gps_rue = list(segment["geometry"]["coordinates"])
        rue = segment["properties"]["codefuv"]
        troncon = segment["properties"]["codetroncon"]
        for i in range(len(co_gps_rue)):
            co_gps_rue[i][0] = round(co_gps_rue[i][0],arrondi_gps)
            co_gps_rue[i][1] = round(co_gps_rue[i][1],arrondi_gps)
        
        if rue not in dico_rues.keys():
            dico_rues[rue] = {troncon: {"GPS" : co_gps_rue} }
        else:
            dico_rues[rue][troncon] = {"GPS" : co_gps_rue}
        dico_rues[rue][troncon]["Importance"] = segment["properties"]["importance"]
        dico_rues[rue][troncon]["Type_circulation"] = segment["properties"]["typecirculation"] #exple: pieton, velo, ...
        dico_rues[rue][troncon]["Sens_circulation"] = segment["properties"]["senscirculation"]
        dico_rues[rue][troncon]["Nom"] = segment["properties"]["nom"]
        dico_rues[rue][troncon]["Commune"] = segment["properties"]["nomcommune"]
        dico_rues[rue][troncon]["Code_postal"] = segment["properties"]["codeinsee"]
        dico_rues[rue][troncon]["Denomination_route"] = segment["properties"]["denomroutiere"]
        longueur_seg = 0
        
        for i in range(len(co_gps_rue)-1):
            longueur_seg += dist_lat_lon_deg(co_gps_rue[i][1],co_gps_rue[i][0],co_gps_rue[i+1][1],co_gps_rue[i+1][0])
        dico_rues[rue][troncon]["Longueur"] = longueur_seg
        
        for co_gps in co_gps_rue:
            tuple_gps = (co_gps[0],co_gps[1])
            if tuple_gps not in dico_noeuds.keys():
                dico_noeuds[tuple_gps]={}
            if rue not in dico_noeuds[tuple_gps].keys():
                dico_noeuds[tuple_gps][rue]=[]
            if troncon not in dico_noeuds[tuple_gps][rue]:
                dico_noeuds[tuple_gps][rue].append(troncon)
    
                
    pente_max = -10
    pente_min = 100
    with open(f_chausses_geojson,encoding='utf-8') as fichier :
        data = json.load(fichier)
    for segment in data["features"]:
        proprietes = segment["properties"]
        troncon = proprietes["codetroncon"]
        rue = proprietes["codefuv"]
        co_gps_rue = list(segment["geometry"]["coordinates"])
        for i in range(len(co_gps_rue)):
            co_gps_rue[i][0] = round(co_gps_rue[i][0],arrondi_gps)
            co_gps_rue[i][1] = round(co_gps_rue[i][1],arrondi_gps)        
        
        if rue in dico_rues.keys() and troncon in dico_rues[rue].keys():
            #sens circulation?
            if dico_rues[rue][troncon]["Nom"] == "" or dico_rues[rue][troncon]["Nom"] == "Voie sans denomination":
                dico_rues[rue][troncon]["Nom"] = proprietes["nomvoie1"]
            if dico_rues[rue][troncon]["Commune"] == "":
                dico_rues[rue][troncon]["Commune"] = proprietes["commune1"]
            if dico_rues[rue][troncon]["Code_postal"] == "":
                dico_rues[rue][troncon]["Code_postal"] = proprietes["insee1"]
            if dico_rues[rue][troncon]["Denomination_route"] == "" :
                dico_rues[rue][troncon]["Denomination_route"] = proprietes["denominationroutiere"]
            
        else:    
            if rue not in dico_rues.keys():
                dico_rues[rue] = {troncon: {"GPS" : co_gps_rue} }
            else:
                dico_rues[rue][troncon] = {"GPS" : co_gps_rue}
            dico_rues[rue][troncon]["Nom"] = proprietes["nomvoie1"]
            dico_rues[rue][troncon]["Commune"] = proprietes["commune1"]
            dico_rues[rue][troncon]["Code_postal"] = proprietes["insee1"]
            dico_rues[rue][troncon]["Denomination_route"] = proprietes["denominationroutiere"]
        
        dico_rues[rue][troncon]["Longueur"] = proprietes.get("longueurreellechaussee",None)
        if dico_rues[rue][troncon]["Longueur"] == None:
            dico_rues[rue][troncon]["Longueur"] = proprietes["longueurcalculee"]
        dico_rues[rue][troncon]["Limitation_vitesse"] = proprietes["limitationvitesse"]
        dico_rues[rue][troncon]["Largeur"] = proprietes.get("largeurcirculeechaussee",None)
        dico_rues[rue][troncon]["Pente_max"] = proprietes.get("pentemaximale",None)
        dico_rues[rue][troncon]["Pente_moy"] = proprietes.get("pentemoyenne",None)
        dico_rues[rue][troncon]["Revetement_chaussee"] = proprietes["revetementchaussee"]
        dico_rues[rue][troncon]["Revetement_trottoir_D"] = proprietes["revetementtrottoirdroit"]
        dico_rues[rue][troncon]["Largeur_trottoir_D"] = proprietes.get("largeurtrottoirdroit",None)
        dico_rues[rue][troncon]["Revetement_trottoir_G"] = proprietes["revetementtrottoirgauche"]
        dico_rues[rue][troncon]["Largeur_trottoir_G"] = proprietes.get("largeurtrottoirgauche",None)

        if proprietes.get("pentemaximale",None) > pente_max and proprietes.get("pentemaximale",None) != None :
            pente_max = proprietes.get("pentemaximale",None)
        
        for co_gps in co_gps_rue:
            tuple_gps = (co_gps[0],co_gps[1])
            if tuple_gps not in dico_noeuds.keys():
                dico_noeuds[tuple_gps]={}
            if rue not in dico_noeuds[tuple_gps].keys():
                dico_noeuds[tuple_gps][rue]=[]
            if troncon not in dico_noeuds[tuple_gps][rue]:
                dico_noeuds[tuple_gps][rue].append(troncon)
        
    a_supprimer = []
    for tuple_gps in dico_noeuds:
        if len(dico_noeuds[tuple_gps]) < 2:
            for rue in dico_noeuds[tuple_gps]:
                if len(dico_noeuds[tuple_gps][rue]) < 2:
                    a_supprimer.append(tuple_gps)
    for tuple_gps in a_supprimer:
        dico_noeuds.pop(tuple_gps)

    rues_adj_gps = {}
    for noeud in dico_noeuds:
        liste_adj = []
        for rue in dico_noeuds[noeud]:
            for troncon in dico_noeuds[noeud][rue]:
                liste_adj.append((rue,troncon))
        for (rue,troncon) in liste_adj:
            if (rue,troncon) not in rues_adj_gps.keys() :
                if len(liste_adj) == 1 :
                    rues_adj_gps[(rue,troncon)] = []
                else:
                    rues_adj_gps[(rue,troncon)] = []
                    for i in liste_adj :
                        if i != (rue,troncon) and i not in rues_adj_gps[(rue,troncon)] :
                            rues_adj_gps[(rue,troncon)].append(i)
            else:
                for i in liste_adj :
                    if i != (rue,troncon) and i not in rues_adj_gps[(rue,troncon)]:
                        rues_adj_gps[(rue,troncon)].append(i)
    
    with open(f_point_debouche,encoding='utf-8') as fichier :
        data = json.load(fichier)
    dico_adresses_num = {}
    dico_adresses_rues = {}
    l_communes = []
    for adresse in data["features"]:
        proprietes = adresse["properties"]
        numero = proprietes["numero"]
        voie = proprietes["voie"]
        commune = proprietes["commune"] 
        co_gps_adresse = list(adresse["geometry"]["coordinates"])
        co_gps_adresse[0] = round(co_gps_adresse[0],arrondi_gps)
        co_gps_adresse[1] = round(co_gps_adresse[1],arrondi_gps)
        
        if numero not in dico_adresses_num.keys():
            dico_adresses_num[numero] = {}
        if voie not in dico_adresses_num[numero].keys():
            dico_adresses_num[numero][voie] = {}
        if commune not in dico_adresses_num[numero][voie].keys():
            dico_adresses_num[numero][voie][commune] = co_gps_adresse
        
        if voie not in dico_adresses_rues.keys():
            dico_adresses_rues[voie] = {}
        if numero not in dico_adresses_rues[voie].keys():
            dico_adresses_rues[voie][numero] = {}
        if commune not in dico_adresses_rues[voie][numero].keys():
            dico_adresses_rues[voie][numero][commune] = co_gps_adresse
            
        if commune not in l_communes:
            l_communes.append(commune)
    
    return rues_adj_gps,dico_rues, dico_adresses_num, dico_adresses_rues, l_communes


def setup_adjacence_param(rues_adjacentes,dico_rues,largeur_chaussee_m = None ,pente_m = None, revet_chaussee_enl = None ,revet_trot_enl = None ,largeur_trot_max= None):
    """Réduit le dictionnaire d'adjacence des rues total selon les paramètres de l\'utilisateur donnés par l'application
    Args:
        rues_adjacentes (dict): dictionnaire d'adjajacence totale des rues keys (FUV,Troncon) val [list](FUV,Troncon)
        dico_rues (dict): le dictionnaire des toutes les rues avec leurs propriétés
        largeur_chaussee_m (float, optional): la largeur maximale choisie par l'utilisateur. Defaults to None.
        pente_m (float, optional): la pente maximale de la rue choisie par l'utilisateur. Defaults to None.
        revet_chaussee_enl (list, optional): une liste contenant les revetements que ne veut pas l'utilisateur. Defaults to None.
        revet_trot_enl (list, optional): une liste contenant les revetement des trotoirs que ne veut pas l'utilisateur. Defaults to None.
        largeur_trot_max (float, optional): la largeur maximale du trotoir que ne veut pas l'utilisateur. Defaults to None.
    Returns:
        dict: le nouveau dictionnaire d'adjacence des rues
    """
    nv_rues_adjacentes = rues_adjacentes
    for key in rues_adjacentes.keys():
        FUV = key[0]
        Troncon = key[1]
        if largeur_chaussee_m != None and dico_rues[FUV][Troncon]["Largeur"] > largeur_chaussee_m:
            #possibilité de supprimer aussi les référence de ces tuple (fuv,troncon) dans les listes d'adjacences
            del nv_rues_adjacentes[(FUV,Troncon)]

        if pente_m != None and dico_rues[FUV][Troncon]["Pente_max"] > pente_m :
            del nv_rues_adjacentes[(FUV,Troncon)]

        if largeur_trot_max != None and (dico_rues[FUV][Troncon]["Largeur_trottoir_D"] > largeur_trot_max or dico_rues[FUV][Troncon]["Largeur_trottoir_G"] > largeur_trot_max ) :
            del nv_rues_adjacentes[(FUV,Troncon)]

        if revet_chaussee_enl != None :
            for revet_chausee in revet_chaussee_enl :
                if dico_rues[FUV][Troncon]["Revetement_chaussee"] == revet_chausee :
                    del nv_rues_adjacentes[(FUV,Troncon)]

        if revet_trot_enl != None :
            for revet_trot in revet_trot_enl :
                if dico_rues[FUV][Troncon]["Revetement_trottoir_D"] == revet_trot or dico_rues[FUV][Troncon]["Revetement_trottoir_G"] == revet_trot :
                    del nv_rues_adjacentes[(FUV,Troncon)]

    return nv_rues_adjacentes

def give_troncon_nearest_gps(co_gps_user,dico_rues):
    """Trouve le couple troncon + FUV le plus proche des coordonnées gps fournis par l'utilisateur
    Args:
        co_gps_user (tuple): coordonnées GPS (long,lat)
        dico_rues (dict): le dictionnaire contenant les paramètres pour chaques couples troncon+FUV
    Returns:
        dict: {(FUV,troncon) : [co_gps]}
    """
    d_min = 2e+7 #ici on va comparer les distance carré entre elles (et la distance maximale étant la circonsphérence de la terre)
    id_rue_troncon = {(0,0) : co_gps_user}
    for fuv in dico_rues.keys():
        for troncon in dico_rues[fuv].keys():
            for co_gps in dico_rues[fuv][troncon]['GPS'] :
                d = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_user[1],co_gps_user[0])
                if d < d_min :
                    id_rue_troncon = {(fuv,troncon) : co_gps}
                    d_min = d

    return id_rue_troncon
    
def give_troncon_address(saisie_user, dico_adresses_num, dico_adresses_rues, liste_communes):
    l_saisie = saisie_user.split(" ")
    a_suppr = []
    for i in range(len(l_saisie)):
        if l_saisie[i] == "" or l_saisie[i] == " ":
            a_suppr.append(i)
    a_suppr.reverse()
    for i in a_suppr:
        l_saisie.pop(i)
    print(f"l_saisie : {l_saisie}")        
    liste_adresses = []
    # on teste s'il y a un numero
    try :
        numero = int(l_saisie[0])
        l_saisie.pop(0)
        print(numero)
    except :
        numero = None
        print("Aucun numéro detecté")
    # on essaye de savoir ou en est la saisie
    # cas ou au moins la rue et peut etre meme et/ou commune commence(nt) à etre indiquée(s)
    if len(l_saisie) > 0 or numero == None:
        # cas ou la commune est indiquée et existe dans le GL (=on suppose adresse complete)
        if l_saisie[-1] in liste_communes:
            commune = l_saisie.pop(-1)
            print(commune)
            rue = None
            if len(l_saisie) > 0:
                rue = ""
                for i in range(len(l_saisie)):
                    rue += l_saisie[i]
                    if i < len(l_saisie)-1:
                        rue += " "
            print(rue)
            # la rue existe
            if rue in dico_adresses_rues.keys():
                # le numero n'existe pas mais on propose des alternatives
                if numero == None or str(numero) not in dico_adresses_rues[rue].keys():
                    print("le numéro n'existe pas")
                    for num in dico_adresses_rues[rue].keys():
                        if len(liste_adresses) < 6 and commune in dico_adresses_rues[rue][num].keys():
                            liste_adresses.append(num+" "+rue+" "+commune)
                # l'adresse est parfaite
                else:
                    print(numero)
                    liste_adresses.append(str(numero)+" "+rue+" "+commune)
            # seule la commune a été saisie ou la rue n'existe pas
            else: 
                if rue != None:
                    print("la rue n'existe pas")
                    liste_adresses.append("rue inconnue")
                print("centre commune")
                liste_adresses.append(commune + " centre")
                # a develloper
                
        #cas ou la commune n'est pas renseignée ou n'est pas dans le Grand Lyon
        else :
            commune = None
            print("La commune n'est pas renseignée ou n'est pas dans le Grand Lyon")
            rue = None
            if len(l_saisie) > 0:
                rue = ""
                for i in range(len(l_saisie)):
                    rue += l_saisie[i]
                    if i < len(l_saisie)-1:
                        rue += " "
            print(rue)
            for voie in dico_adresses_rues.keys():
                # la rue existe
                if len(liste_adresses) < 6 and rue.lower() in voie.lower():
                    # le numero n'existe pas mais on propose des alternatives
                    if numero == None : #or str(numero) not in dico_adresses_rues[voie].keys(): # ne marche pas bien
                        print("le numéro n'existe pas")
                        for num in dico_adresses_rues[voie].keys():
                            if len(liste_adresses) < 6 :
                                for commune in dico_adresses_rues[voie][num].keys():
                                    if len(liste_adresses) < 6 :
                                        liste_adresses.append(num+" "+voie+" "+commune)
                    # le numero et la rue existe
                    elif str(numero) in dico_adresses_rues[voie].keys():
                        print(numero)
                        for com in dico_adresses_rues[voie][str(numero)].keys():
                            if len(liste_adresses) < 6 :
                                liste_adresses.append(str(numero)+" "+voie+" "+com)
            if len(liste_adresses) == 0:
                for voie in dico_adresses_rues.keys():
                    # la rue existe
                    if len(liste_adresses) < 6 and rue.lower() in voie.lower():
                        # le numero n'existe pas mais on propose des alternatives
                        print("le numéro n'existe pas")
                        for num in dico_adresses_rues[voie].keys():
                            if len(liste_adresses) < 6 :
                                for commune in dico_adresses_rues[voie][num].keys():
                                    if len(liste_adresses) < 6 :
                                        liste_adresses.append(num+" "+voie+" "+commune)
    # cas ou seul le numero est marqué
    elif numero != None:
        for num in dico_adresses_num.keys():
            if len(liste_adresses) < 6 and str(numero).lower() in num.lower():
                for rue in dico_adresses_num[num].keys():
                    if len(liste_adresses) < 6 :
                        for commune in dico_adresses_num[num][rue].keys():
                            if len(liste_adresses) < 6 :
                                liste_adresses.append(num+" "+rue+" "+commune)
    print(liste_adresses)
    return liste_adresses

def dist_lat_lon_deg(start_lat,start_lon,end_lat,end_lon): 
    distance = 0.0
    if abs(math.sin(math.radians(start_lat)) * math.sin(math.radians(end_lat)) + math.cos(math.radians(start_lon) - math.radians(end_lon)) * math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat))) < 1:
        # formule de la distance entre 2 points sur une sphère
        distance = 6371000*math.acos(math.sin(math.radians(start_lat)) * math.sin(math.radians(end_lat)) + math.cos(math.radians(start_lon) - math.radians(end_lon)) * math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat)))
    return distance

def a_star(start, goal, rues_adjacentes, dico_rues):
    queue = PriorityQueue()  # Créer une file de priorité pour les noeuds à explorer
    queue.put((0, start))  # Ajouter le tuple (pondération, noeud) à la file 
    came_from = {}  # Créer un dictionnaire pour stocker les parents de chaque noeud exploré
    cost_so_far = {}  # Créer un dictionnaire pour stocker le coût pour atteindre chaque noeud exploré
    came_from[start] =  None # Le noeud de départ n'a pas de parent
    cost_so_far[start] = 0  # Le coût pour atteindre le noeud de départ est 0
    co_moy_goal = [(dico_rues[goal[0]][goal[1]]['GPS'][0][0]+dico_rues[goal[0]][goal[1]]['GPS'][-1][0])/2,(dico_rues[goal[0]][goal[1]]['GPS'][0][1]+dico_rues[goal[0]][goal[1]]['GPS'][-1][1])/2 ]
    
    itinerary = False
    while not queue.empty() and not itinerary:
        current = queue.get()[1] #l'indice zéro est celui de priorité
        lat_lon_current = [dico_rues[current[0]][current[1]]['GPS'][0],dico_rues[current[0]][current[1]]['GPS'][-1]]
        # print(current)
        # Récupérer le noeud avec la plus petite priorité dans la file
        if current == goal: 
            itinerary = True
        else:
            for next_node in rues_adjacentes[current]:# On récupère le tuple coordonées des adj : (lat,lon)
                new_cost = cost_so_far[current] + dico_rues[next_node[0]][next_node[1]]["Longueur"]  # Calculer le coût pour atteindre le voisin en passant par le noeud actuel
                if next_node not in cost_so_far.keys() or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost  # Mettre à jour le coût pour atteindre le voisin
                    lat_lon_node = [dico_rues[next_node[0]][next_node[1]]['GPS'][0],dico_rues[next_node[0]][next_node[1]]['GPS'][-1]]
                    if lat_lon_current[0] == lat_lon_node[0] or lat_lon_current[-1] == lat_lon_node[0]:
                        co_end_node = lat_lon_node[-1]
                    else:
                        co_end_node = lat_lon_node[0]
                    priority = new_cost + dist_lat_lon_deg(co_end_node[1],co_end_node[0],co_moy_goal[1],co_moy_goal[0])  # Calculer la priorité pour le voisin
                    queue.put((priority, next_node))  # Ajouter le voisin à la file avec sa nouvelle priorité
                    came_from[next_node] = current  # Stocker le noeud actuel comme parent du voisin exploré
    # print(came_from, '\n\n')

    # Pour avoir le parcourt du départ à l'arrivée
    if itinerary:
        path = [goal]
        while start not in path:
            path.append(came_from[path[-1]])
        path.reverse()
        dist_path = cost_so_far[goal]
    else:
        path = []
        dist_path = 0

    print ("Le chemin le plus court est : ", path,', Pour une distance de ', dist_path)
    return path, dist_path

if __name__ == "__main__" :
    adj,rue = charger_donnees()