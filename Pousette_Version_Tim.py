# -*- coding: utf-8 -*-
"""
Created on Tue Apr 11 16:29:13 2023

@author: timhu
"""


# co gps extrem : [[4.685632778305, 45.557074952992], [5.135618602316, 45.940168465059]]

import tkinter as tk
import math
from tkinter import ttk
from tkinter.ttk import Separator
from tkinter import messagebox
from tkinter import scrolledtext #!!!
from tkscrolledframe import ScrolledFrame

#import Load_Files

import tkintermapview

##############################################################################
########################    Load_Files_Remi.py     ###########################

import json
#import math
from queue import PriorityQueue

def charger_donnees_troncon():
    f_troncons_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Troncons_trame_viaire.geojson"
    arrondi_gps = 12
   
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
    return dico_noeuds, dico_rues

def charger_donnees_chausses(dico_noeuds, dico_rues):     
    f_chausses_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Chaussees_et_trottoirs.geojson"
    arrondi_gps = 12
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
            if proprietes["senscirculation"] == "Double":
                dico_rues[rue][troncon]["Sens_circulation"] = proprietes["senscirculation"]
            else:
                dico_rues[rue][troncon]["Sens_circulation"] = None
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
        
        for co_gps in co_gps_rue:
            tuple_gps = (co_gps[0],co_gps[1])
            if tuple_gps not in dico_noeuds.keys():
                dico_noeuds[tuple_gps]={}
            if rue not in dico_noeuds[tuple_gps].keys():
                dico_noeuds[tuple_gps][rue]=[]
            if troncon not in dico_noeuds[tuple_gps][rue]:
                dico_noeuds[tuple_gps][rue].append(troncon)
    return dico_noeuds, dico_rues
    
def correction_dico_noeuds(dico_noeuds):
    a_supprimer = []
    for tuple_gps in dico_noeuds:
        if len(dico_noeuds[tuple_gps]) < 2:
            for rue in dico_noeuds[tuple_gps]:
                if len(dico_noeuds[tuple_gps][rue]) < 2:
                    a_supprimer.append(tuple_gps)
    for tuple_gps in a_supprimer:
        dico_noeuds.pop(tuple_gps)
    return dico_noeuds
    
def charger_donnees_adj(dico_noeuds):
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
    return rues_adj_gps  
             
def charger_donnees_adresses():
    f_point_debouche = r"C:/Users/timhu/Documents/1_Scolaire/INSA_2A/Informatique/Projet/Donnees_projet/Points_debouche_adresse.geojson"
    arrondi_gps = 12                    
    with open(f_point_debouche,encoding='utf-8') as fichier :
        data = json.load(fichier)
    dico_adresses_num = {}
    dico_adresses_rues = {}
    dico_adresses_communes = {}
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
        
        if commune not in dico_adresses_communes.keys():
            dico_adresses_communes[commune] = {}
        if voie not in dico_adresses_communes[commune].keys():
            dico_adresses_communes[commune][voie] = {}
        if numero not in dico_adresses_communes[commune][voie].keys():
            dico_adresses_communes[commune][voie][numero] = co_gps_adresse
    
    return dico_adresses_num, dico_adresses_rues, dico_adresses_communes

def charger_donnees_centre(dico_adresses_communes):
    for commune in dico_adresses_communes.keys():
        somme_lat = 0.0
        somme_lon = 0.0
        compteur = 0
        for rue in dico_adresses_communes[commune].keys():
            for numero in dico_adresses_communes[commune][rue].keys():
                compteur += 1
                somme_lon += dico_adresses_communes[commune][rue][numero][0]
                somme_lat += dico_adresses_communes[commune][rue][numero][1]
        co_centre = [somme_lon/compteur,somme_lat/compteur]
        dico_adresses_communes[commune]["centre"]={"0":co_centre}
    return dico_adresses_communes

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
    id_rue_troncon = (0,0)
    for fuv in dico_rues.keys():
        for troncon in dico_rues[fuv].keys():
            for co_gps in dico_rues[fuv][troncon]['GPS'] :
                d = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_user[1],co_gps_user[0])
                if d < d_min :
                    id_rue_troncon = (fuv,troncon)
                    d_min = d
    return id_rue_troncon

def gestion_saisie(saisie_user, l_communes):
    liste_saisie = saisie_user.split(", ")
    latitude = None
    longitude = None
    com_possibles = []
    commune = None
    rue = None
    numero = None
    if len(liste_saisie) > 1 :
        try:
            longitude = float(liste_saisie[-1])
            latitude = float(liste_saisie[0])
            print(f'Coordonnées GPS reconnues : \nLatitude : {latitude} \nLongitude : {longitude}')
        except:
            commune = liste_saisie.pop(-1)
            print(f'Commune reconnue : {commune}')
    else:
        for i in range(len(l_communes)):
            if liste_saisie[0].lower() in l_communes[i].lower():
                com_possibles.append(l_communes[i])
                print(f'Centre commune reconnu : {commune}')
    if commune == None and com_possibles != []:
        print('Commune non-reconnue ou non-renseignée.')
    if com_possibles == [] and longitude == None and latitude == None:
        liste_rue = liste_saisie[0].split(" ")
        a_suppr = []
        for i in range(len(liste_rue)):
            if liste_rue[i] == "" or liste_rue[i] == " ":
                a_suppr.append(i)
        a_suppr.reverse()
        for i in a_suppr:
            liste_rue.pop(i)
        # on teste s'il y a un numero
        try :
            numero = int(liste_rue[0])
            liste_rue.pop(0)
            print(f'Numéro reconnu : {numero}')
        except :
            print("Aucun numéro reconnu ou renseigné.")
        print(f"Rue saisie: {liste_rue}")
        if len(liste_rue) > 0:
            rue = ""
            for i in range(len(liste_rue)):
                rue += liste_rue[i]
                if i < len(liste_rue)-1:
                    rue += " "
            rue.strip(",")
            print(f"Rue detectée : {rue}")
        else:
            print("Aucune rue saisie")
    print()
    return numero, rue, commune, com_possibles, latitude, longitude

def give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, dico_adresses_num, dico_adresses_rues, dico_adresses_communes):
    nb_prop_max = 6
    liste_adresses = []
    # on essaye de savoir où en est la saisie
    # cas ou l'utilisateur saisi des co GPS
    if latitude != None and longitude != None:
        if longitude < 4.685632778305:
            longitude = 4.685632778305
        elif longitude > 5.135618602316:
            longitude = 5.135618602316
        if latitude < 45.557074952992:
            latitude = 45.557074952992
        elif latitude > 45.940168465059:
            latitude = 45.940168465059
        liste_adresses.append(str(latitude)+", "+str(longitude))    
        
    # cas où seulement la commune est saisie
    elif com_possibles != []:
        for com in com_possibles:
            if len(liste_adresses) < nb_prop_max:
                print(f"Centre commune : {commune}")
                liste_adresses.append(com+" centre")
    # cas où seul le numero est marqué
    elif commune == None and rue == None and numero != None:
        print(f"Numéro uniquement : {numero}")
        for num in dico_adresses_num.keys():
            # le numéro existe ou compose un numéro
            if len(liste_adresses) < nb_prop_max and str(numero).lower() == num.lower():
                for rue in dico_adresses_num[num].keys():
                    if len(liste_adresses) < nb_prop_max :
                        for commune in dico_adresses_num[num][rue].keys():
                            if len(liste_adresses) < nb_prop_max :
                                liste_adresses.append(num+" "+rue+", "+commune)
    # cas où au moins le début de la rue est indiqué mais pas la commune
    elif commune == None and rue != None:
        print(f"Rue en partie : {rue}")
        for voie in dico_adresses_rues.keys():
            # la rue existe
            if len(liste_adresses) < nb_prop_max and rue.lower() in voie.lower():
                # le numero existe dans la rue
                if str(numero) in dico_adresses_rues[voie].keys():
                    for com in dico_adresses_rues[voie][str(numero)].keys():
                        if len(liste_adresses) < nb_prop_max :
                            liste_adresses.append(str(numero)+" "+voie+", "+com)
                # le numero n'est pas renseigné mais on propose des options
                elif numero == None :
                    for num in dico_adresses_rues[voie].keys():
                        if len(liste_adresses) < nb_prop_max :
                            for commune in dico_adresses_rues[voie][num].keys():
                                if len(liste_adresses) < nb_prop_max :
                                    liste_adresses.append(num+" "+voie+", "+commune)
        # si la liste est encore vide à ce stade, cela signifie que
        #   le numero est renseigné mais qu'il n'existe pas dans la rue
        #   on ignore donc le numéro saisi et on propose des alternatives
        if len(liste_adresses) == 0:
            for voie in dico_adresses_rues.keys():
                # la rue existe
                if len(liste_adresses) < nb_prop_max and rue.lower() in voie.lower():
                    for num in dico_adresses_rues[voie].keys():
                        if len(liste_adresses) < nb_prop_max :
                            for commune in dico_adresses_rues[voie][num].keys():
                                if len(liste_adresses) < nb_prop_max :
                                    liste_adresses.append(num+" "+voie+", "+commune)
    #cas ou la commune est saisie en plus de la rue
    elif commune != None and rue != None:
        print(f"Commune : {commune} + rue : {rue}")
        # on cherche une correspondance de la saisie avec une commune de la base
        com_possibles = []
        for i in range(len(list(dico_adresses_communes.keys()))):
            if commune.lower() in list(dico_adresses_communes.keys())[i].lower():
                com_possibles.append(list(dico_adresses_communes.keys())[i])

        # la commune existe et la rue existe dans cette commune
        if com_possibles != []:
            for com in com_possibles:
                if len(liste_adresses) < nb_prop_max and rue in dico_adresses_communes[com].keys():
                    # le numero existe dans la rue
                    if str(numero) in dico_adresses_rues[rue].keys():
                        liste_adresses.append(str(numero)+" "+rue+", "+com)
                    # le numero n'est pas renseigné ou n'existe pas dans la rue
                    #   mais on propose des options alternatives
                    elif numero == None :
                        for num in dico_adresses_rues[rue].keys():
                            if len(liste_adresses) < nb_prop_max :
                                liste_adresses.append(num+" "+rue+", "+com)
            # si la liste est encore vide à ce stade, cela signifie que
            #   le numero est renseigné mais qu'il n'existe pas dans la rue
            #   on ignore donc le numéro saisi et on propose des alternatives
            if len(liste_adresses) == 0:
                for com in com_possibles:
                    if len(liste_adresses) < nb_prop_max and rue in dico_adresses_communes[com].keys():
                        for num in dico_adresses_rues[rue].keys():
                            if len(liste_adresses) < nb_prop_max :
                                liste_adresses.append(num+" "+rue+", "+com)
            # si la liste est toujours vide à ce stade, cela signifie que
            #   la rue est renseigné mais qu'elle n'existe pas dans la/les commune(s)
            #   on ignore donc la rue saisie et on propose de prendre le centre de la commune
            if len(liste_adresses) == 0:
                for com in com_possibles:
                    if len(liste_adresses) < nb_prop_max :
                        liste_adresses.append(com+" centre")
    print()
    print(liste_adresses)
    print()
    print()
    return liste_adresses   

def dist_lat_lon_deg(start_lat,start_lon,end_lat,end_lon): 
    distance = 0.0
    if abs(math.sin(math.radians(start_lat)) * math.sin(math.radians(end_lat)) + math.cos(math.radians(start_lon) - math.radians(end_lon)) * math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat))) < 1:
        #formule de la distance entre 2 points sur une sphère
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
        #print(current)
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
    #print(came_from, '\n\n')

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

def compute_cross(fuv_tr_pre, fuv_tr_suiv, dico_rues, rues_adjacentes):
    #On recup les infos sur les segments precedent et suivant
    info_pre = dico_rues[fuv_tr_pre[0]][fuv_tr_pre[1]]
    info_suiv = dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]]
    dico_fuv_tr_gps = {"precedent":{},"suivant":{},"adjacents":{}}
    co_gps_noeud = []
    co_gps_pre = info_pre['GPS'].copy()
    co_gps_suiv = info_suiv['GPS'].copy()
    #on identifie quel cote des segment est lié au noeud
    #(donc on idetifie aussi les co GPS du noeud)
    # et on inverse l'ordre des co GPS des segments si besoin
    # debut de la liste des co GPS d'un segment = le noeud
    if info_pre['GPS'][0] == info_suiv['GPS'][0] or info_pre['GPS'][0] == info_suiv['GPS'][-1]:
        co_gps_noeud = info_pre['GPS'][0]
    else:
        co_gps_noeud = info_pre['GPS'][-1]
        co_gps_pre.reverse()
    if info_suiv['GPS'][0] != co_gps_noeud:
        co_gps_suiv.reverse()
    # on met tout ca dans le dico    
    dico_fuv_tr_gps["suivant"][fuv_tr_suiv] = co_gps_suiv
    dico_fuv_tr_gps["precedent"][fuv_tr_pre] = co_gps_pre
    
    #on identifie quels segments sont adjacents au noeud parmi les adjacents du segment precedent
    #si on en trouve d'autre que le segment suivant on fait le meme processus que pour le suivant/precedent
    # (connaitre le sens et renverser l'ordre si besoin, et mettre dans le dico)
    for fuv_tr in rues_adjacentes[fuv_tr_pre]:
        info_adj = dico_rues[fuv_tr[0]][fuv_tr[1]]
        if co_gps_noeud in info_adj['GPS'] and fuv_tr != fuv_tr_suiv:
            co_gps_adj = info_adj['GPS'].copy()
            if info_adj['GPS'][0] != co_gps_noeud:
                co_gps_adj.reverse()
            dico_fuv_tr_gps["adjacents"][fuv_tr] = co_gps_adj.copy()
    # on faitr un autre dico, construit de la meme facon mais qui aura les co cartésienne et pas GPS
    # appel a la fonction de conversion
    dico_fuv_tr_xy = {"precedent":{},"suivant":{},"adjacents":{}}
    for categorie in dico_fuv_tr_gps:
        for troncon in dico_fuv_tr_gps[categorie]:
            for co_gps in dico_fuv_tr_gps[categorie][troncon]:
                if troncon not in dico_fuv_tr_xy[categorie].keys():
                    dico_fuv_tr_xy[categorie][troncon] = [xy_lat_long(co_gps[1],co_gps[0],co_gps_noeud[-1])]
                else:
                    dico_fuv_tr_xy[categorie][troncon].append(xy_lat_long(co_gps[1],co_gps[0],co_gps_noeud[-1]))
    return dico_fuv_tr_xy, co_gps_noeud[-1]

def xy_lat_long(latitude, longitude, latitude_ref):
    #on fait en sorte que la longitude soit comprise entre 0 et 360 et non entre -180 et 180
    longitude = longitude + 180
    #on la rapporte de 0 à 2000
    x = ((longitude*2000*math.cos(math.radians(latitude_ref)))/360)
    #idem mais la latitude est comprise entre 0 et 180
    latitude = latitude + 90
    # donc on la rapporte de 0 à 1000
    hauteur = (latitude*1000)/180 
    y = 1000 - hauteur
    return [x, y]

def calcul_angle(x1, y1, x2, y2):
    #tout est dans le titre
    delta_x = x2 - x1
    delta_y = y2 - y1
    alpha = math.pi/2
    if delta_x != 0:
        alpha = math.atan(delta_y/delta_x)
        if delta_x < 0:
            alpha += math.pi
    elif delta_y < 0:
        delta_x += math.pi
    return alpha

def rotation_repere(angle, dico_fuv_tr_adj):
    # on fait un nouveau dico, tjrs sur le meme model et en co cartésienne
    # mais avec les co cartésienne qui font que le segment precdent est vertical
    # globalement cest un changement de base de mécanique appliqué à toutes les co
    dico_fuv_tr_rot = {"precedent":{},"suivant":{},"adjacents":{}}
    for categorie in dico_fuv_tr_adj:
        for troncon in dico_fuv_tr_adj[categorie]:
            for co_xy in dico_fuv_tr_adj[categorie][troncon]:
                x_rot = math.sin(angle)*co_xy[0] - math.cos(angle)*co_xy[1]
                y_rot = math.cos(angle)*co_xy[0] + math.sin(angle)*co_xy[1]
                if troncon not in dico_fuv_tr_rot[categorie].keys():
                    dico_fuv_tr_rot[categorie][troncon] = [[x_rot, y_rot]]
                else:
                    dico_fuv_tr_rot[categorie][troncon].append([x_rot, y_rot])
    return dico_fuv_tr_rot

def xy_cartesien(dist_min, dico_fuv_tr_rot, xy_noeud, width_canvas, height_canvas):
    #on fait un nouveau dico, tjrs sur le meme model et en co cartésienne
    # mais cette fois ci l'echelle change pour que les co correspondent avec l'affichage dans le canvas
    dico_fuv_tr_carte = {"precedent":{},"suivant":{},"adjacents":{}}
    for categorie in dico_fuv_tr_rot:
        for troncon in dico_fuv_tr_rot[categorie]:
            for co_xy in dico_fuv_tr_rot[categorie][troncon]:
                x_carte = (co_xy[0] - xy_noeud[0] + dist_min)*width_canvas/(2*dist_min)
                y_carte = (co_xy[1] - xy_noeud[1] + dist_min)*height_canvas/(2*dist_min)
                if troncon not in dico_fuv_tr_carte[categorie].keys():
                    dico_fuv_tr_carte[categorie][troncon] = [[x_carte, y_carte]]
                else:
                    dico_fuv_tr_carte[categorie][troncon].append([x_carte, y_carte])
    return dico_fuv_tr_carte

def calcul_norme_min(dico_fuv_tr_rot):
    #Determination de l'extrémité d'un segment adjacent la plus proche du noeud
    # selon la norme infini (cf. cours de maths)
    # permet d'avoir la vision la plus large possible sans voir d'autres noeuds
    norme_min = math.inf
    for categorie in dico_fuv_tr_rot:
        for troncon in dico_fuv_tr_rot[categorie]:
            co_gps = dico_fuv_tr_rot[categorie][troncon]
            norme = max(abs(co_gps[-1][0]-co_gps[0][0]),abs(co_gps[-1][1]-co_gps[0][1]))
            if norme < norme_min and norme != 0 :
                norme_min = norme
    return norme_min

def calcul_dist_min(dico_fuv_tr_adj):
    #Determination de l'extrémité d'un segment adjacent la plus proche du noeud
    # selon la norme 2 (cf. cours de maths)
    # permet de prevoir la vision qu'on aura et les points gps qui seront ou non surement dans la fenetre
    dist_min = math.inf
    for categorie in dico_fuv_tr_adj:
        for troncon in dico_fuv_tr_adj[categorie]:
            dist = distance(dico_fuv_tr_adj[categorie][troncon], 0, -1)
            if dist < dist_min and dist != 0 :
                dist_min = dist
    return dist_min

def distance(co_gps, index1, index2):
    # distance selon la norme 2 entre 2 points definis par leur index dans une liste de coordonnees
    return math.sqrt((co_gps[index2][0]-co_gps[index1][0])**2+(co_gps[index2][1]-co_gps[index1][1])**2)

def instructions(dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv, dico_rues):
    i = 1
    while i < len(dico_fuv_tr_carte["suivant"][fuv_tr_suiv]) - 1 and distance(dico_fuv_tr_carte["suivant"][fuv_tr_suiv], 0, i) < 200*math.sqrt(2)/2:
        i += 1
    x_suivant = dico_fuv_tr_carte["suivant"][fuv_tr_suiv][i][0]
    y_suivant = dico_fuv_tr_carte["suivant"][fuv_tr_suiv][i][1]
    x_noeud = dico_fuv_tr_carte["precedent"][fuv_tr_pre][0][0]
    y_noeud = dico_fuv_tr_carte["precedent"][fuv_tr_pre][0][1]
    
    texte_instruction = ""
    if fuv_tr_pre[0] == fuv_tr_suiv[0]:
        texte_instruction += "Continuer "
    else:
        texte_instruction += "Prendre "
    if calcul_angle(x_suivant, y_suivant, x_noeud, y_noeud) < 3*math.pi/8:
        texte_instruction += "à gauche "
    elif calcul_angle(x_suivant, y_suivant, x_noeud, y_noeud) > 5*math.pi/8:
        texte_instruction += "à droite "
    else:
        texte_instruction += "tout droit "
    texte_instruction += "sur "
    if dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]].get("Nom","") != "" and dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]].get("Nom","") != 'Voie sans denomination' and dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]].get("Nom","") != 'Voie sans dénomination':
        texte_instruction += dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]]["Nom"]
    elif dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]].get("Denomination_route","") != "":
        texte_instruction += dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]]["Denomination_route"]
    else:
        texte_instruction += "route sans nom"
    return texte_instruction

def consigne_noeud(fuv_tr_pre, fuv_tr_suiv, dico_rues, rues_adjacentes):
    #Recherche des segments adjacents, compilation de leurs co GPS dans un dictionnaire
    #puis passage en co cartesienne
    dico_fuv_tr_adj, lat_noeud = compute_cross(fuv_tr_pre, fuv_tr_suiv, dico_rues, rues_adjacentes)
    #calcul des points qui seront visible et qu'il faut donc prendre en compte pour l'orientation 
    dist_min = calcul_dist_min(dico_fuv_tr_adj)
    i = 1
    while i < len(dico_fuv_tr_adj["precedent"][fuv_tr_pre]) - 1 and distance(dico_fuv_tr_adj["precedent"][fuv_tr_pre], 0, i) < dist_min:
        i += 1
    #Calcul de l'angle entre le segment precedent (premier et dernier point GPS potentiellement dans le cadre final)
    # et l'horizontale (axe x)
    x_noeud = dico_fuv_tr_adj["precedent"][fuv_tr_pre][0][0]
    y_noeud = dico_fuv_tr_adj["precedent"][fuv_tr_pre][0][1]
    x_precedent = dico_fuv_tr_adj["precedent"][fuv_tr_pre][i][0]
    y_precedent = dico_fuv_tr_adj["precedent"][fuv_tr_pre][i][1]
    alpha_pre = calcul_angle(x_noeud, y_noeud, x_precedent, y_precedent)
    #Rotation du repere pour avoir le segment precedent en bas de l'ecran, vertical
    dico_fuv_tr_rot = rotation_repere(alpha_pre, dico_fuv_tr_adj)
    #Determination de l'extrémité d'un segment adjacent la plus proche du noeud
    # selon la norme infini (cf. cours de maths)
    # permet d'avoir la vision la plus large possible sans voir d'autres noeuds
    norme_min = calcul_norme_min(dico_fuv_tr_rot)
    xy_noeud = dico_fuv_tr_rot["precedent"][fuv_tr_pre][0]
    #Mise à l'echelle des co en fonction de la distance min
    dico_fuv_tr_carte = xy_cartesien(norme_min, dico_fuv_tr_rot, xy_noeud, 400, 400)
    #détermination de la consigne
    text_instruction = instructions(dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv, dico_rues)
    return text_instruction
# if __name__ == "__main__" :
#     adj,rue = charger_donnees_troncon()


##############################################################################
##############################################################################
    

class MainWindow():
    def __init__(self) :
        # on initialise d'abord la fenetre principale sur un affichage de chargement, le temps que les donnees se chargent
        self.root = tk.Tk()
        self.root.geometry("300x200")
        self.loading_label_1 = tk.Label(self.root, text = "Chargement des données", font = "Calibri 16")
        self.loading_label_1.pack()
        self.loading_label_2 = tk.Label(self.root, text = "Veuillez patienter", font = "Calibri 13")
        self.loading_label_2.pack()
        self.progress_bar = ttk.Progressbar(self.root, orient = tk.HORIZONTAL, length = 100, mode = 'determinate')
        self.progress_bar.pack()
        self.root.title("Lyonyroule")
        # la fonction load_all_datas est lancée au bout de 100ms après le démarage (cf. ligne 679 (plus à jour))
        #itineraire fictif pour test fenetre trajet
        #self.itineraire = [('22416', 'T54924'),('37324', 'T54925'),('37324', 'T54926'),('36078', 'T23765')]
        #self.itineraire = [('33788','T27222'),('33787','T27233'),('33787','T35503'),('33785','T35505'),('33786','T27243'),('33793','T27247'),('33792','T27266'),('33796','T27274'),('33796','T27275'),('33794','T27269')]
        self.fen_trajet = None
        self.itineraire = []
        self.depart = (None,None)
        self.arrivee = (None,None)
        self.dist_trajet = 0
        self.saisie_user_start = ""
        self.saisie_user_end = ""
        #self.itineraire.reverse()

    def initWidget(self):
        self.loading_label_1.destroy()
        self.loading_label_2.destroy()
        self.progress_bar.destroy()
        self.root.geometry("1000x600")
        
        self.map_widget = tkintermapview.TkinterMapView(self.root, width=800, height=600, corner_radius=0)
        self.map_widget.pack(side=tk.LEFT,fill=tk.BOTH)
        # set current widget position and zoom
        self.map_widget.set_position(45.76177569754233, 4.8358160526802685)  #on centre sur Lyon
        self.map_widget.set_zoom(11)

        separator_canvas = Separator(self.root,orient=tk.VERTICAL)
        separator_canvas.pack(side=tk.LEFT,fill=tk.Y)

        #frame qui contient les widget en mode choix itinaire
        self.frame_princ = tk.Frame(self.root)

        self.frame_dest = tk.Frame(self.frame_princ,padx=5,pady=5)

        # self.var_entry_start = tk.StringVar(value="Départ")
        # self.start_entry = tk.Entry(self.frame_dest,bg='gray',fg='black',textvariable=self.var_entry_start)
        # self.start_entry.pack(side=tk.TOP,fill=tk.X)
        # self.start_entry.bind("<Button-1>",self.effacer_prop_start)
        
        self.liste_depart = []
        self.var_entry_start = tk.StringVar(value = "Départ")
        self.start_selection = ttk.Combobox(self.frame_dest, textvariable=self.var_entry_start, values = self.liste_depart, width = 80)
        self.start_selection.bind("<KeyRelease>",self.get_entry_start)
        self.start_selection.bind("<Button-1>",self.effacer_start)
        self.start_selection.bind("<KeyRelease-Return>", self.down_start)
        self.start_selection.bind("<<ComboboxSelected>>", self.choose_start)
        self.start_selection.bind("<FocusOut>",self.ecrire_start)
        self.start_selection.pack(side=tk.TOP, anchor = tk.N, fill=tk.X)
        
        self.liste_arrivee = []
        self.var_entry_end = tk.StringVar(value = "Arrivée")
        self.end_selection = ttk.Combobox(self.frame_dest, textvariable=self.var_entry_end, values = self.liste_arrivee)
        self.end_selection.bind("<KeyRelease>",self.get_entry_end)
        self.end_selection.bind("<Button-1>",self.effacer_end)
        self.end_selection.bind("<KeyRelease-Return>", self.down_end)
        self.end_selection.bind("<<ComboboxSelected>>", self.choose_end)
        self.end_selection.bind("<FocusOut>",self.ecrire_end)
        self.end_selection.pack(side=tk.TOP,anchor = tk.N, fill=tk.X)

        self.frame_dest.pack(side=tk.TOP,fill=tk.X)

        separator_dest = Separator(self.frame_princ,orient=tk.HORIZONTAL)
        separator_dest.pack(side=tk.TOP,fill=tk.X)

        self.frame_opt = tk.Frame(self.frame_princ,padx=5,pady=5)

        self.choice_poussette = tk.IntVar()
        self.check_button_poussette = tk.Checkbutton(self.frame_opt,
                                                     bg = 'gray', fg = 'black', anchor = 'w',
                                                     text = "  Poussette/Fauteil",
                                                     onvalue = True, offvalue = False,
                                                     variable = self.choice_poussette)
        #self.check_button_poussette = tk.Checkbutton(self.frame_opt,bg='gray',fg='black',text="Poussette/Fauteil",onvalue=True,offvalue=False,variable=self.choice_poussette)
        self.check_button_poussette.pack(side=tk.TOP,fill=tk.X)

        self.choice_bike = tk.IntVar()
        self.check_button_bike = tk.Checkbutton(self.frame_opt,
                                                bg='gray', fg = 'black', anchor = 'w',
                                                text = "          Vélo", onvalue=True,
                                                offvalue = False, variable = self.choice_bike)
        #self.check_button_bike = tk.Checkbutton(self.frame_opt,bg='gray',fg='black',text="Vélo",onvalue=True,offvalue=False,variable=self.choice_bike)
        self.check_button_bike.pack(side=tk.TOP,fill=tk.X)


        self.choice_voiture = tk.IntVar()
        self.check_button_voiture = tk.Checkbutton(self.frame_opt,
                                                   bg = 'gray',fg = 'black', text = "        Voiture",
                                                   onvalue = True, anchor = 'w',
                                                   offvalue=False, variable = self.choice_voiture)
        self.check_button_voiture.pack(side=tk.TOP,fill=tk.X)

        self.choice_foot = tk.IntVar()
        self.check_button_foot = tk.Checkbutton(self.frame_opt,
                                                bg='gray', fg = 'black', anchor = 'w',
                                                text="          Pied", onvalue = True, 
                                                offvalue = False, variable = self.choice_foot)
        self.check_button_foot.pack(side=tk.TOP,fill=tk.X)
        # self.choice_voiture = tk.IntVar()
        # self.check_button_voiture = tk.Checkbutton(self.frame_opt,bg='gray',fg='black',text="Voiture",onvalue=True,offvalue=False,variable=self.choice_voiture)
        # self.check_button_voiture.pack(side=tk.TOP,fill=tk.X)

        # self.choice_foot = tk.IntVar()
        # self.check_button_foot = tk.Checkbutton(self.frame_opt,bg='gray',fg='black',text="Pied",onvalue=True,offvalue=False,variable=self.choice_foot)
        # self.check_button_foot.pack(side=tk.TOP,fill=tk.X)

        self.frame_opt.pack(side=tk.TOP,fill=tk.X)

        self.button_opt_av = tk.Button(self.frame_princ,text="Paramètres avancés",bg='gray',fg='black',relief='flat')
        self.button_opt_av.pack(side=tk.BOTTOM,fill=tk.X,padx=5,pady=5)
        self.button_opt_av.bind('<Button-1>',self.bouton_param_av)

        self.button_research = tk.Button(self.frame_princ,text="Lancer la recherche",bg='gray',fg='black',relief='flat')
        self.button_research.pack(side=tk.BOTTOM,fill=tk.X)
        self.button_research.bind('<Button-1>',self.start_research)

        separator_bt = Separator(self.frame_princ,orient=tk.HORIZONTAL)
        separator_bt.pack(side=tk.TOP,fill=tk.X)

        self.frame_princ.pack(fill=tk.Y)

        #frame qui contient les widgets en mode trajet
        self.frame_trajet = tk.Frame(self.root)

        self.var_prop_trajet = tk.StringVar(value=f"Votre Trajet\n {self.var_entry_start.get()}\n vers\n {self.var_entry_end.get()}")

        self.label_trajet_prop = tk.Label(self.frame_trajet,textvariable=self.var_prop_trajet,padx=5,pady=5)
        self.label_trajet_prop.pack(side=tk.TOP,fill=tk.X)

        self.button_change_iti = tk.Button(self.frame_trajet,text="Modifier votre itineraire",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_change_iti.pack(side=tk.TOP,fill=tk.X)
        self.button_change_iti.bind("<Button-1>",self.bouton_change_iti)
       
        self.button_start_iti = tk.Button(self.frame_trajet,text="Commencer votre itinéraire",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_start_iti.pack(side=tk.BOTTOM,fill=tk.X)
        self.button_start_iti.bind("<Button-1>",self.open_window_trajet)
        
        self.frame_detail_etapes = ScrolledFrame(self.root, width = 150)
        self.frame_detail_etapes.pack()
        self.inner_frame_etapes = self.frame_detail_etapes.display_widget(tk.Frame)
        label = tk.Label(self.inner_frame_etapes, anchor="center", justify="center", text="Détail de l'itinéraire :\n")
        label.pack(side=tk.TOP, fill = tk.X)    

        self.frame_trajet.pack_forget()
        self.frame_detail_etapes.pack_forget()
    
    # def choix_adresse(self):
    #     print("ok")

    def loop(self):
        self.root.mainloop()
        
    def get_entry_start(self, event):
        if event.widget.get() != self.saisie_user_start and event.widget.get() != "":
            self.saisie_user_start = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = gestion_saisie(self.saisie_user_start, list(self.dico_adresses_communes.keys()))
            self.liste_depart = give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.start_selection.configure(values = self.liste_depart)
        self.start_selection.configure(foreground = "red")
        self.depart = (None,None)
        if len(self.liste_depart) == 1 and len(event.widget.get()) > 1:
            self.start_selection.event_generate('<Down>',when="tail")
    
    def down_start(self, event):
        if event.widget.get() != self.saisie_user_start and event.widget.get() != "":
            self.saisie_user_start = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = gestion_saisie(self.saisie_user_start, list(self.dico_adresses_communes.keys()))
            self.liste_depart = give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.start_selection.configure(values = self.liste_depart)
        self.start_selection.event_generate('<Down>',when="tail")
            
    def choose_start(self, event):
        self.start_selection.configure(foreground = "green")
        saisie = event.widget.get().split(", ")
        try:
            longitude = float(saisie[1])
            latitude = float(saisie[0])
            co_gps = [longitude,latitude]
        except:
            choix = saisie[0].split(" ")
            a_suppr = []
            for i in range(len(choix)):
                if choix[i] == "" or choix[i] == " ":
                    a_suppr.append(i)
            a_suppr.reverse()
            for i in a_suppr:
                choix.pop(i)
                
            if len(saisie) == 1:
                choix.pop(-1)
                commune = ""
                for i in range(len(choix)):
                    commune += choix[i]
                    if i < len(choix)-1:
                            commune += " "
                co_gps = self.dico_adresses_communes[commune]["centre"]["0"]
            else:
                commune = saisie[1]
                numero = choix.pop(0)
                rue = ""
                for i in range(len(choix)):
                    rue += choix[i]
                    if i < len(choix)-1:
                            rue += " "
                co_gps = self.dico_adresses_num[numero][rue][commune]
        self.depart = give_troncon_nearest_gps(co_gps, self.dico_rues)
        
        print()
        print(f"FUV+TRONCON départ : {self.depart}")
        print()
    
    def effacer_start(self,event):
        if self.start_selection.get() == "Départ":
            self.start_selection.set("")
            
    def ecrire_start(self,event):
        saisie = self.start_selection.get()
        saisie = saisie.strip(" ")
        if saisie == "":
            self.start_selection.set("Départ")
            self.start_selection.configure(foreground = "black")
            
    def get_entry_end(self, event):
        if event.widget.get() != self.saisie_user_end and event.widget.get() != "":
            self.saisie_user_end = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = gestion_saisie(self.saisie_user_end, list(self.dico_adresses_communes.keys()))
            self.liste_arrivee = give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.end_selection.configure(values = self.liste_arrivee)
        self.end_selection.configure(foreground = "red")
        self.arrivee = (None,None)
        if len(self.liste_arrivee) == 1 and len(event.widget.get()) > 1:
            self.end_selection.event_generate('<Down>',when="tail")
    
    def down_end(self, event):
        if event.widget.get() != self.saisie_user_end and event.widget.get() != "":
            self.saisie_user_end = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = gestion_saisie(self.saisie_user_end, list(self.dico_adresses_communes.keys()))
            self.liste_arrivee = give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.end_selection.configure(values = self.liste_arrivee)
        self.end_selection.event_generate('<Down>',when="tail")
    
    def choose_end(self, event):
        self.end_selection.configure(foreground = "green")
        saisie = event.widget.get().split(", ")
        try:
            longitude = float(saisie[1])
            latitude = float(saisie[0])
            co_gps = [longitude,latitude]
        except:
            choix = saisie[0].split(" ")
            a_suppr = []
            for i in range(len(choix)):
                if choix[i] == "" or choix[i] == " ":
                    a_suppr.append(i)
            a_suppr.reverse()
            for i in a_suppr:
                choix.pop(i)
                
            if len(saisie) == 1:
                choix.pop(-1)
                commune = ""
                for i in range(len(choix)):
                    commune += choix[i]
                    if i < len(choix)-1:
                            commune += " "
                co_gps = self.dico_adresses_communes[commune]["centre"]["0"]
            else:
                commune = saisie[1]
                numero = choix.pop(0)
                rue = ""
                for i in range(len(choix)):
                    rue += choix[i]
                    if i < len(choix)-1:
                            rue += " "
                co_gps = self.dico_adresses_num[numero][rue][commune]
        self.arrivee = give_troncon_nearest_gps(co_gps, self.dico_rues)
        
        print()
        print(self.arrivee)
        print()
    
    def effacer_end(self,event):
        if self.end_selection.get() == "Arrivée":
            self.end_selection.set("")
            
    def ecrire_end(self,event):
        saisie = self.end_selection.get()
        saisie = saisie.strip(" ")
        if saisie == "":
            self.end_selection.set("Arrivée")
            self.end_selection.configure(foreground = "black")

    def bouton_param_av(self,event):
        print("Vous avez cliquez sur le boutons des parametres avancés")
        print(f"Ville de départ {self.var_entry_start.get()}")
        print(f"Ville d'arrivee {self.var_entry_end.get()}")
        print(f"Choix Poussette {self.choice_poussette.get()}")

        self.dialog_params_av = TopLevelParams(self.root)

    def start_research(self,event):
        """Fonction callback du bouton de calcul de l'itineraire, il lance la recherche de l'itineraire
        Args:
            event (dict): the tk event object return after the user event
        """
        if self.depart != (None,None) and self.arrivee != (None,None) and self.depart != self.arrivee:
            self.itineraire, self.dist_trajet = a_star(self.depart,self.arrivee,self.carrefour_adjacences, self.dico_rues)
            print(self.dico_rues[self.itineraire[0][0]][self.itineraire[0][1]]['GPS'])
            #on cache la frame principale et affiche la frame itineraire
            self.frame_princ.pack_forget()
            self.var_prop_trajet.set(f"Votre Trajet\n {self.var_entry_start.get()} vers {self.var_entry_end.get()}")
            self.frame_trajet.pack(fill=tk.Y)
            self.frame_detail_etapes.pack(fill=tk.BOTH)
            
            # on appelle la fonction qui affiche la carte principale
            self.show_large_map()
            self.l_button_etape = []
            for i in range(len(self.itineraire)-1):
                text_detail_etapes = str(i+1) + " : " + consigne_noeud(self.itineraire[i], self.itineraire[i+1], self.dico_rues, self.carrefour_adjacences)
                button_etape = tk.Button(self.inner_frame_etapes,text=text_detail_etapes,bg='gray',fg='black', command = lambda idx=i: self.open_window_trajet_middle(idx))
                button_etape.pack(side = tk.TOP, fill = tk.X)
                self.l_button_etape.append(button_etape)
                #self.button_etape.bind("<Button-1>",self.open_window_trajet)
        else :
            messagebox.showinfo("Itinéraire incomplet", "Adresse(s) de départ et/ou d'arrivée non renseignée(s) ou non reconnue(s). \nVeuillez compléter les champs manquants.")
            
    def show_large_map(self):
        co_trajet = []
        for fuv_rue in self.itineraire :
            co_gps_liste = self.dico_rues[fuv_rue[0]][fuv_rue[1]]['GPS']
            if len(co_trajet) != 0 :
                if (co_gps_liste[0][1],co_gps_liste[0][0]) == co_trajet[len(co_trajet)-1] or (co_gps_liste[0][1],co_gps_liste[0][0]) == co_trajet[0]:
                    for co_gps in co_gps_liste :
                        co_trajet.append((co_gps[1],co_gps[0]))
                elif (co_gps_liste[len(co_gps_liste)-1][1],co_gps_liste[len(co_gps_liste)-1][0]) == co_trajet[len(co_trajet)-1] or (co_gps_liste[len(co_gps_liste)-1][1],co_gps_liste[len(co_gps_liste)-1][0]) == co_trajet[0]:
                    for i in range(len(co_gps_liste)-1,-1,-1):
                        co_trajet.append((co_gps_liste[i][1],co_gps_liste[i][0]))

                #else : 
                    #print((co_gps_liste[0][1],co_gps_liste[0][0]),co_trajet[len(co_trajet)-1],co_gps_liste[len(co_gps_liste)-1][1],co_gps_liste[len(co_gps_liste)-1][0])

            else :
                fuv_rue_suiv = self.itineraire[1]
                co_gps_liste_suiv = self.dico_rues[fuv_rue_suiv[0]][fuv_rue_suiv[1]]['GPS']
                if co_gps_liste[0] == co_gps_liste_suiv[0] or co_gps_liste[0] == co_gps_liste_suiv[-1]:
                    co_gps_liste.reverse()
                for co_gps in co_gps_liste :
                    co_trajet.append((co_gps[1],co_gps[0]))


        print(co_trajet)
        #ajout d'un marker au debut et fin
        marker_debut = self.map_widget.set_marker(co_trajet.pop(0)[0],co_trajet.pop(0)[1],text="Start")
        marker_fin = self.map_widget.set_marker(co_trajet.pop()[0],co_trajet.pop()[1],text="End")
        co_trajet.insert(0,marker_debut.position)
        co_trajet.insert(len(co_trajet)-1,marker_fin.position)
        self.map_widget.set_path(co_trajet)

        
    def bouton_change_iti(self,event):
        msg_user = messagebox.askyesno("Changer d'itineraire ?","Voulez vous vraiment changer d'itinéraire ?\n Celui-ci sera perdu")
        if msg_user == True :
            #Affiche de nouveau le frame principal
            self.frame_trajet.pack_forget()
            self.frame_detail_etapes.pack_forget()
            self.frame_princ.pack(fill=tk.Y)
     
    def open_window_trajet(self,event):
        """Fonction callback du bouton commencer le trajet, ouvre la fenetre du trajet carrefour par carrefour
        Args:
            event (dict): the tk event object return after the user event 
        """
        print(self.fen_trajet)
        # if self.fen_trajet != None:
        #     print()
        #     print("destroy")
        #     print()
        #     self.fen_trajet.toplevel_parcour.destroy()
        self.fen_trajet = TopLevelParcour(self.root, self.dico_rues, self.carrefour_adjacences, self.itineraire, 0)
        print(self.fen_trajet)
        
    def open_window_trajet_middle(self, idx):
        """Fonction callback du bouton commencer le trajet, ouvre la fenetre du trajet carrefour par carrefour
        Args:
            event (dict): the tk event object return after the user event 
        """
        print(self.fen_trajet)
        # if self.fen_trajet != None:
        #     print()
        #     print("destroy")
        #     print()
        #     self.fen_trajet.toplevel_parcour.destroy()
        self.fen_trajet = TopLevelParcour(self.root, self.dico_rues, self.carrefour_adjacences, self.itineraire, idx)
        self.root.after(1000,self.fen_trajet.destroy())       


    def load_all_datas(self):
        self.dico_noeuds, self.dico_rues = charger_donnees_troncon()
        self.progress_bar['value'] = 25
        self.root.update_idletasks()
        self.dico_noeuds, self.dico_rues = charger_donnees_chausses(self.dico_noeuds, self.dico_rues)
        self.progress_bar['value'] = 50
        self.root.update_idletasks()
        self.dico_noeuds = correction_dico_noeuds(self.dico_noeuds)
        self.progress_bar['value'] = 60
        self.root.update_idletasks()
        self.carrefour_adjacences = charger_donnees_adj(self.dico_noeuds)
        self.progress_bar['value'] = 75
        self.root.update_idletasks()
        self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes = charger_donnees_adresses()
        self.progress_bar['value'] = 95
        self.root.update_idletasks()
        self.dico_adresses_communes = charger_donnees_centre(self.dico_adresses_communes)
        self.progress_bar['value'] = 100
        self.root.update_idletasks()
        #une fois le chargement de donnees effectue, on met a jour l'affichage pour afficher le menu d'acceuil
        self.root.after(500,self.initWidget) 

class TopLevelParams():
    def __init__(self,mainwindow):
        self.mainwindow = mainwindow
        self.toplevel_params = tk.Toplevel(self.mainwindow)
        
        self.init_widget()
        self.toplevel_params.mainloop()
        
    def init_widget(self):
        self.var_width_road = tk.DoubleVar(value=5.0)
        self.slidder_width_road = tk.Scale(self.toplevel_params,from_=0,to=20,variable=self.var_width_road,tickinterval=5,resolution=0.5,label="Seuil largeur de la chaussée",orient=tk.HORIZONTAL)
        self.slidder_width_road.pack(fill=tk.X)

        self.var_slope_max = tk.DoubleVar(value=4.0)
        self.slidder_slope_max = tk.Scale(self.toplevel_params,label="Pente maximale",from_=0,to=12,resolution=0.1,tickinterval=1.0,orient=tk.HORIZONTAL,variable=self.var_slope_max)
        self.slidder_slope_max.pack(fill=tk.X)

class TopLevelParcour():
    def __init__(self, mainwindow, dico_rues, rues_adjacentes, itineraire, etape):
        self.mainwindow = mainwindow
        self.dico_rues = dico_rues
        self.rues_adjacentes = rues_adjacentes
        self.itineraire = itineraire
        self.etape = etape
        print(f'etape : {self.etape}')
        
        # self.liste_dist_min=[]
        self.liste_echelles = [0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000]
        
        self.toplevel_parcour = tk.Toplevel(self.mainwindow)
        self.toplevel_parcour.resizable(height = False, width = False) 
        self.toplevel_parcour.title = "Trajet"
        
        self.f_par_width = 400
        self.f_par_height = 500
        self.toplevel_parcour.geometry(f"{self.f_par_width}x{self.f_par_height}")

        self.init_widget()
        self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])

        self.toplevel_parcour.mainloop()


    def init_widget(self):
        
        self.width_canvas = 400
        self.height_canvas = 400
        
        self.label_instruction = tk.Label(self.toplevel_parcour, text = "Instructions", font = "Calibri 16", height=2, wraplength=400)
        self.label_instruction.pack(side=tk.TOP)
        
        self.main_canvas = tk.Canvas(self.toplevel_parcour,width = self.width_canvas, height = self.height_canvas,bg='blue')
        self.main_canvas.pack(side=tk.TOP)

        self.frame_bt = tk.Frame(self.toplevel_parcour)

        self.button_past_step = tk.Button(self.frame_bt,text="Etape Précédente",bg='gray',fg='black',relief='flat')
        self.button_past_step.bind('<Button-1>', self.precedent)
        self.toplevel_parcour.bind('<Left>', self.precedent)
        self.button_past_step.grid(column=0,row=0,padx=5,pady=5)

        self.button_forward_step = tk.Button(self.frame_bt,text="Etape Suivante",bg='gray',fg='black',relief='flat')
        self.button_forward_step.bind('<Button-1>', self.suivant)
        self.toplevel_parcour.bind('<Right>', self.suivant)
        self.button_forward_step.grid(column=2,row=0,padx=5,pady=5)

        self.frame_bt.pack()
    
    def precedent(self, event):
        if self.etape > 0:
            self.main_canvas.delete(self.ligne_pre)
            self.main_canvas.delete(self.ligne_suiv)
            self.main_canvas.delete(self.rond_noeud)
            self.main_canvas.delete(self.ligne_nord)
            self.main_canvas.delete(self.texte_nord)
            self.main_canvas.delete(self.rect_nord)
            self.main_canvas.delete(self.rect_echelle)
            self.main_canvas.delete(self.text_echelle)
            for ligne in self.liste_ligne_adj :
                self.main_canvas.delete(ligne)
            for rect in self.liste_rect_echelle :
                self.main_canvas.delete(rect)
            self.etape -= 1
            self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])
    
    def suivant(self, event):
        self.etape += 1
        self.main_canvas.delete(self.ligne_pre)
        self.main_canvas.delete(self.ligne_suiv)
        self.main_canvas.delete(self.rond_noeud)
        self.main_canvas.delete(self.ligne_nord)
        self.main_canvas.delete(self.texte_nord)
        self.main_canvas.delete(self.rect_nord)
        self.main_canvas.delete(self.rect_echelle)
        self.main_canvas.delete(self.text_echelle)
        for ligne in self.liste_ligne_adj :
            self.main_canvas.delete(ligne)
        for rect in self.liste_rect_echelle :
            self.main_canvas.delete(rect)
        if self.etape + 1 < len(self.itineraire):
            self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])
        else:
            self.toplevel_parcour.destroy()
            
    def show_iti(self, fuv_tr_pre, fuv_tr_suiv):
        #Recherche des segments adjacents, compilation de leurs co GPS dans un dictionnaire
        #puis passage en co cartesienne
        dico_fuv_tr_adj, lat_noeud = compute_cross(fuv_tr_pre, fuv_tr_suiv, self.dico_rues, self.rues_adjacentes)
        #calcul des points qui seront visible et qu'il faut donc prendre en compte pour l'orientation 
        dist_min = calcul_dist_min(dico_fuv_tr_adj)
        i = 1
        while i < len(dico_fuv_tr_adj["precedent"][fuv_tr_pre]) - 1 and distance(dico_fuv_tr_adj["precedent"][fuv_tr_pre], 0, i) < dist_min:
            i += 1
        #Calcul de l'angle entre le segment precedent (premier et dernier point GPS potentiellement dans le cadre final)
        # et l'horizontale (axe x)
        x_noeud = dico_fuv_tr_adj["precedent"][fuv_tr_pre][0][0]
        y_noeud = dico_fuv_tr_adj["precedent"][fuv_tr_pre][0][1]
        x_precedent = dico_fuv_tr_adj["precedent"][fuv_tr_pre][i][0]
        y_precedent = dico_fuv_tr_adj["precedent"][fuv_tr_pre][i][1]
        alpha_pre = calcul_angle(x_noeud, y_noeud, x_precedent, y_precedent)
        
        #Rotation du repere pour avoir le segment precedent en bas de l'ecran, vertical
        dico_fuv_tr_rot = rotation_repere(alpha_pre, dico_fuv_tr_adj)
        #Determination de l'extrémité d'un segment adjacent la plus proche du noeud
        # selon la norme infini (cf. cours de maths)
        # permet d'avoir la vision la plus large possible sans voir d'autres noeuds
        norme_min = calcul_norme_min(dico_fuv_tr_rot)
        xy_noeud = dico_fuv_tr_rot["precedent"][fuv_tr_pre][0]
        #Mise à l'echelle des co en fonction de la distance min
        dico_fuv_tr_carte = xy_cartesien(norme_min, dico_fuv_tr_rot, xy_noeud, self.width_canvas, self.height_canvas)

        #determination des coordonnées du nord
        co_nord = [[370-math.cos(alpha_pre)*20, 30+math.sin(alpha_pre)*20], [370+math.cos(alpha_pre)*20, 30-math.sin(alpha_pre)*20]]
        #determination de l'echelle
        echelle = 0.1 * math.cos(math.radians(lat_noeud)) * norme_min * 2 * 6371000 * 2 * math.pi / 2000
        i = 0
        echelle_choisie = 0
        cote_echelle = 0
        while i < len(self.liste_echelles) and echelle_choisie == 0:
            if echelle < self.liste_echelles[i]:
                echelle_choisie = self.liste_echelles[i]
                cote_echelle = 40*echelle_choisie/echelle
            i += 1
        #Dessin sur le canvas et affichage des informations
        self.dessine_noeud(dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv, co_nord, cote_echelle, echelle_choisie)
        text_instruction = instructions(dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv, self.dico_rues)
        self.label_instruction.configure(text = str(self.etape) + " : " + text_instruction)
        
    def dessine_noeud(self, dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv, co_nord, cote_echelle, echelle_choisie):
        #on trace les eventuels chemins adjacents
        self.liste_ligne_adj =[]
        for troncon in dico_fuv_tr_carte["adjacents"]:
            ligne = self.main_canvas.create_line(dico_fuv_tr_carte["adjacents"][troncon], fill = "grey", width = 10)
            self.liste_ligne_adj.append(ligne)
        #on trace les segments suivant et precedent
        self.ligne_pre = self.main_canvas.create_line(dico_fuv_tr_carte["precedent"][fuv_tr_pre], fill = "red", width = 15)
        self.ligne_suiv = self.main_canvas.create_line(dico_fuv_tr_carte["suivant"][fuv_tr_suiv], fill = "red", width = 15)
        #on trace le noeud
        x_noeud = dico_fuv_tr_carte["precedent"][fuv_tr_pre][0][0]
        y_noeud = dico_fuv_tr_carte["precedent"][fuv_tr_pre][0][1]
        self.rond_noeud = self.main_canvas.create_oval(x_noeud-20,y_noeud-20,x_noeud+20,y_noeud+20, fill = "red")
        #on trace le nord
        self.rect_nord = self.main_canvas.create_rectangle(348,8,392,80, fill = "white")
        self.ligne_nord = self.main_canvas.create_line(co_nord, fill = "black", width = 4, arrow = "last", arrowshape = (16,20,6))
        self.texte_nord = self.main_canvas.create_text(370, 65, text = "N", fill = "black", font ="15")
        #on trace l'echelle
        #self.rect_b_echelle = self.main_canvas.create_rectangle(387-cote_echelle,367,393,393, fill = "white")
        self.rect_echelle = self.main_canvas.create_rectangle(390-cote_echelle,380,390,390, fill = "black")
        self.liste_rect_echelle = []
        if echelle_choisie%3 == 0:
            for i in range(3):
                rect_blanc = self.main_canvas.create_rectangle(390-((2*i+1)*cote_echelle/6),380,390-((2*i)*cote_echelle/6),390, fill = "white")
                self.liste_rect_echelle.append(rect_blanc)
        else:
            for i in range(2):
                rect_blanc = self.main_canvas.create_rectangle(390-((2*i+2)*cote_echelle/5),380,390-((2*i+1)*cote_echelle/5),390, fill = "white")
                self.liste_rect_echelle.append(rect_blanc)        
        self.text_echelle = self.main_canvas.create_text((2*390 - cote_echelle)/2,370,text = str(echelle_choisie)+" m", fill = "white", font ="Calibri 12")


        

        

if __name__ == "__main__":
    root = MainWindow()
    #on lance le chargement de donnees juste apres que l'affichage de la premiere fenetre se soit fait
    root.root.after(100,root.load_all_datas) 
    root.loop()