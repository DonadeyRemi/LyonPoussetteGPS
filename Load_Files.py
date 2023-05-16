# -*- coding: utf-8 -*-
"""
Created on Mon Mar 27 15:20:19 2023

@author: timhu
"""

import json
import math
from queue import PriorityQueue

def charger_donnees_troncon():
    """Charge des dictionnaires les données du fichier relatif au troncons

    Returns:
        dict: dico_noeud: les données des noeuds (carrefours)
        dict: dico_rue les données des code FUV
    """
    f_troncons_geojson = "troncon_trame_viaire.geojson"
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
        dico_rues[rue][troncon]["Denomination_route"] = segment["properties"]["denomroutiere"]
        dico_rues[rue][troncon]["Limitation_vitesse"] = "50"
        longueur_seg = 0
        
        for i in range(len(co_gps_rue)-1):
            longueur_seg += dist_lat_lon_deg(co_gps_rue[i][1],co_gps_rue[i][0],co_gps_rue[i+1][1],co_gps_rue[i+1][0])
        dico_rues[rue][troncon]["Longueur"] = longueur_seg
        
        co_gps_rue = [co_gps_rue[0],co_gps_rue[-1]]
        for co_gps in co_gps_rue:
            tuple_gps = (co_gps[0],co_gps[1])
            if tuple_gps not in dico_noeuds.keys():
                dico_noeuds[tuple_gps]={}
            if rue not in dico_noeuds[tuple_gps].keys():
                dico_noeuds[tuple_gps][rue]=[]
            if troncon not in dico_noeuds[tuple_gps][rue]:
                dico_noeuds[tuple_gps][rue].append(troncon)
    return dico_noeuds, dico_rues

def charger_donnees_chaussees(dico_noeuds, dico_rues):
    """Ajoute les données relatives au fichier chaussee et trotoirs

    Args:
        dico_noeuds (dict): dictionnaire contenant l'ensemble des noeuds du réseaux routier
        dico_rues (dict): dictionnaire clé (fuv,troncon) avec l'ensemble des propriétés des routes

    Returns:
        dict:dico des noeuds
        dict:dico des rues
    """
    f_chaussees_geojson = "chaussees_trotoirs.geojson"
    arrondi_gps = 12
    with open(f_chaussees_geojson,encoding='utf-8') as fichier :
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
            if dico_rues[rue][troncon]["Denomination_route"] == "" :
                dico_rues[rue][troncon]["Denomination_route"] = proprietes["denominationroutiere"]
            if dico_rues[rue][troncon]["Sens_circulation"] == "" :
                dico_rues[rue][troncon]["Sens_circulation"] = "Double"
            
        else:    
            if rue not in dico_rues.keys():
                dico_rues[rue] = {troncon: {"GPS" : co_gps_rue} }
            else:
                dico_rues[rue][troncon] = {"GPS" : co_gps_rue}
            dico_rues[rue][troncon]["Sens_circulation"] = "Double"
            dico_rues[rue][troncon]["Nom"] = proprietes["nomvoie1"]
            dico_rues[rue][troncon]["Commune"] = proprietes["commune1"]
            dico_rues[rue][troncon]["Code_postal"] = proprietes["insee1"]
            dico_rues[rue][troncon]["Denomination_route"] = proprietes["denominationroutiere"]
        
        dico_rues[rue][troncon]["Longueur"] = proprietes.get("longueurreellechaussee",None)
        if dico_rues[rue][troncon]["Longueur"] == None:
            dico_rues[rue][troncon]["Longueur"] = proprietes["longueurcalculee"]
        dico_rues[rue][troncon]["Limitation_vitesse"] = proprietes["limitationvitesse"]
        if dico_rues[rue][troncon]["Limitation_vitesse"] == "":
            dico_rues[rue][troncon]["Limitation_vitesse"] = "50"
        dico_rues[rue][troncon]["Largeur"] = proprietes.get("largeurcirculeechaussee",None)
        dico_rues[rue][troncon]["Pente_max"] = proprietes.get("pentemaximale",None)
        dico_rues[rue][troncon]["Pente_moy"] = proprietes.get("pentemoyenne",None)
        dico_rues[rue][troncon]["Revetement_chaussee"] = proprietes["revetementchaussee"]
        dico_rues[rue][troncon]["Revetement_trottoir_D"] = proprietes["revetementtrottoirdroit"]
        dico_rues[rue][troncon]["Largeur_trottoir_D"] = proprietes.get("largeurtrottoirdroit",None)
        dico_rues[rue][troncon]["Revetement_trottoir_G"] = proprietes["revetementtrottoirgauche"]
        dico_rues[rue][troncon]["Largeur_trottoir_G"] = proprietes.get("largeurtrottoirgauche",None)
        
        co_gps_rue = [co_gps_rue[0],co_gps_rue[-1]]
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
    """Ajuste le dictionnaire des noeuds pour enlever les doublons inutiles

    Args:
        dico_noeuds (dict): le dictionnaire noeuds (carrefours)

    Returns:
        dict: dico_noeuds
    """
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
    """Creation du dictionnaire d'adjacence

    Args:
        dico_noeuds (dict): le dictionnaire des noeuds (FUV troncons)

    Returns:
        dict: le dictionnaire d'adjacences
    """
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

def charger_donnees_adj_poussette(dico_noeuds,dico_rues):
    """creer le dictionnaire d'adjacence pour le moyen de transport poussette 

    Args:
        dico_noeuds (dict): le dictionnaire des noeuds (FUV troncons)
        dico_rues (dict): le dictionnaire qui contient les proprietes des rues

    Returns:
        dict: le dictionnaire d'adjacence
    """
    pente_max = 8
    pente_moy = 5
    largeur_min_trot = 1.5
    revettements_eviter = ["Pavés","Végétation","Non revêtu"]
    importance_eviter = ["Grand axe"]
    rues_adj_poussette = {}
    for noeud in dico_noeuds:
        liste_adj = []
        for rue in dico_noeuds[noeud]:
            for troncon in dico_noeuds[noeud][rue]:
                if ((dico_rues[rue][troncon].get("Pente_max",None) == None or dico_rues[rue][troncon]["Pente_max"] <= pente_max) 
                and (dico_rues[rue][troncon].get("Pente_moy",None) == None or dico_rues[rue][troncon]["Pente_moy"] <= pente_moy)
                and (dico_rues[rue][troncon].get("Largeur_trottoir_D",None) == None or dico_rues[rue][troncon].get("Largeur_trottoir_G",None) == None 
                or dico_rues[rue][troncon]["Largeur_trottoir_D"] >= largeur_min_trot or dico_rues[rue][troncon]["Largeur_trottoir_G"] >= largeur_min_trot) 
                and (dico_rues[rue][troncon].get("Revetement_trottoir_D",None) == None or dico_rues[rue][troncon].get("Revetement_trottoir_G",None) == None 
                or dico_rues[rue][troncon]["Revetement_trottoir_D"] not in revettements_eviter or dico_rues[rue][troncon]["Revetement_trottoir_G"] not in revettements_eviter)
                and (dico_rues[rue][troncon].get("Importance",None) == None or dico_rues[rue][troncon]["Importance"] not in importance_eviter)):
                        liste_adj.append((rue,troncon))
        for (rue,troncon) in liste_adj:
            if (rue,troncon) not in rues_adj_poussette.keys() :
                if len(liste_adj) == 1 :
                    rues_adj_poussette[(rue,troncon)] = []
                else:
                    rues_adj_poussette[(rue,troncon)] = []
                    for i in liste_adj :
                        if i != (rue,troncon) and i not in rues_adj_poussette[(rue,troncon)] :
                            rues_adj_poussette[(rue,troncon)].append(i)
            else:
                for i in liste_adj :
                    if i != (rue,troncon) and i not in rues_adj_poussette[(rue,troncon)] :
                        rues_adj_poussette[(rue,troncon)].append(i)
    return rues_adj_poussette  

def charger_donnees_adj_velo(dico_noeuds,dico_rues):
    """creer le dictionnaire d'adjacence pour le moyen de transport velo

    Args:
        dico_noeuds (dict): le dictionnaire des noeuds (FUV troncons)
        dico_rues (dict): le dictionnaire qui contient les proprietes des rues

    Returns:
        dict: le dictionnaire d'adjacence
    """
    type_eviter = ["Escalier"]
    revettements_eviter = ["Végétation","Non revêtu"]
    importance_eviter = ["Grand axe"]
    rues_adj_velo = {}
    for noeud in dico_noeuds:
        liste_adj = []
        for rue in dico_noeuds[noeud]:
            for troncon in dico_noeuds[noeud][rue]:
                if ((dico_rues[rue][troncon].get("Revetement_chaussee",None) == None or dico_rues[rue][troncon]["Revetement_chaussee"] not in revettements_eviter)
                and (dico_rues[rue][troncon].get("Importance",None) == None or dico_rues[rue][troncon]["Importance"] not in importance_eviter)
                and (dico_rues[rue][troncon].get("Type_circulation",None) == None or dico_rues[rue][troncon]["Type_circulation"] not in type_eviter)):
                        liste_adj.append((rue,troncon))
        for (rue,troncon) in liste_adj:
            if (rue,troncon) not in rues_adj_velo.keys() :
                if len(liste_adj) == 1 :
                    rues_adj_velo[(rue,troncon)] = []
                else:
                    rues_adj_velo[(rue,troncon)] = []
                    for i in liste_adj :
                        if i != (rue,troncon) and i not in rues_adj_velo[(rue,troncon)] :
                            rues_adj_velo[(rue,troncon)].append(i)
            else:
                for i in liste_adj :
                    if i != (rue,troncon) and i not in rues_adj_velo[(rue,troncon)]:
                        rues_adj_velo[(rue,troncon)].append(i)
    return rues_adj_velo

def charger_donnees_adj_voiture(dico_noeuds,dico_rues):
    """creer le dictionnaire d'adjacence pour le moyen de transport voiture

    Args:
        dico_noeuds (dict): le dictionnaire des noeuds (FUV troncons)
        dico_rues (dict): le dictionnaire qui contient les proprietes des rues

    Returns:
        dict: le dictionnaire d'adjacence
    """
    largeur_min_chaussee = 2.5
    type_eviter = ["Escalier","Bus","Pietons"]
    revettements_eviter = ["Végétation","Non revêtu"]
    rues_adj_voiture = {}
    for noeud in dico_noeuds:
        liste_adj = []
        for rue in dico_noeuds[noeud]:
            for troncon in dico_noeuds[noeud][rue]:
                if ((dico_rues[rue][troncon].get("Largeur",None) == None or dico_rues[rue][troncon]["Largeur"] >= largeur_min_chaussee)
                and (dico_rues[rue][troncon].get("Type_circulation",None) == None or dico_rues[rue][troncon]["Type_circulation"] not in type_eviter)
                and (dico_rues[rue][troncon].get("Revetement_chaussee",None) == None or dico_rues[rue][troncon]["Revetement_chaussee"] not in revettements_eviter)):
                    liste_adj.append((rue,troncon))
        for (rue,troncon) in liste_adj:
            if (rue,troncon) not in rues_adj_voiture.keys() :
                if len(liste_adj) == 1 :
                    rues_adj_voiture[(rue,troncon)] = []
                else:
                    rues_adj_voiture[(rue,troncon)] = []
                    for i in liste_adj :
                        if i != (rue,troncon) and i not in rues_adj_voiture[(rue,troncon)] :
                            rues_adj_voiture[(rue,troncon)].append(i)
            else:
                for i in liste_adj :
                    if i != (rue,troncon) and i not in rues_adj_voiture[(rue,troncon)] :
                        rues_adj_voiture[(rue,troncon)].append(i)
    return rues_adj_voiture 

def charger_donnees_adj_pied(dico_noeuds,dico_rues):
    """creer le dictionnaire d'adjacence pour le moyen de transport pied

    Args:
        dico_noeuds (dict): le dictionnaire des noeuds (FUV troncons)
        dico_rues (dict): le dictionnaire qui contient les proprietes des rues

    Returns:
        dict: le dictionnaire d'adjacence
    """
    largeur_min_trot = 0.5
    revettements_eviter = ["Pavés","Végétation","Non revêtu"]
    importance_eviter = ["Grand axe"]
    rues_adj_pied = {}
    for noeud in dico_noeuds:
        liste_adj = []
        for rue in dico_noeuds[noeud]:
            for troncon in dico_noeuds[noeud][rue]:
                if ((dico_rues[rue][troncon].get("Largeur_trottoir_D",None) == None or dico_rues[rue][troncon].get("Largeur_trottoir_G",None) == None 
                or dico_rues[rue][troncon]["Largeur_trottoir_D"] >= largeur_min_trot or dico_rues[rue][troncon]["Largeur_trottoir_G"] >= largeur_min_trot) 
                and (dico_rues[rue][troncon].get("Revetement_trottoir_D",None) == None or dico_rues[rue][troncon].get("Revetement_trottoir_G",None) == None 
                or dico_rues[rue][troncon]["Revetement_trottoir_D"] not in revettements_eviter or dico_rues[rue][troncon]["Revetement_trottoir_G"] not in revettements_eviter)
                and (dico_rues[rue][troncon].get("Importance",None) == None or dico_rues[rue][troncon]["Importance"] not in importance_eviter)):
                        liste_adj.append((rue,troncon))
        for (rue,troncon) in liste_adj:
            if (rue,troncon) not in rues_adj_pied.keys() :
                if len(liste_adj) == 1 :
                    rues_adj_pied[(rue,troncon)] = []
                else:
                    rues_adj_pied[(rue,troncon)] = []
                    for i in liste_adj :
                        if i != (rue,troncon) and i not in rues_adj_pied[(rue,troncon)] :
                            rues_adj_pied[(rue,troncon)].append(i)
            else:
                for i in liste_adj :
                    if i != (rue,troncon) and i not in rues_adj_pied[(rue,troncon)] :
                        rues_adj_pied[(rue,troncon)].append(i)
    return rues_adj_pied
             
def charger_donnees_adresses():
    """charge les donnees des debouches (lieu d'arrivee et depart)

    Returns:
        dict: dictionnaire des numeros des adresses
        dict: dictionnaire des nom des rues des adresses
        dict: dictionnaire des nom des villes des adresses
    """
    f_point_debouche = "point_debouche.geojson"
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
    """calcule les coordonnees gps des centres des villes/communes

    Args:
        dico_adresses_communes (dict): dictionnaires des noms des communes des adresses

    Returns:
        dict: dictionnaire des coordonnees GPS des centres des communes
    """
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


def give_troncon_nearest_gps(co_gps_start, co_gps_end ,dico_rues,choix_transport):
    """Trouve le couple troncon + FUV le plus proche des coordonnées gps fournis par l'utilisateur pour l'adresse de départ et d'arrivée
    Args:
        co_gps_user (tuple): coordonnées GPS (long,lat)
        dico_rues (dict): le dictionnaire contenant les paramètres pour chaques couples troncon+FUV
    Returns:
        dict: {(FUV,troncon) : [co_gps]}
    """
    d_min_start = 2e+7 #ici on va comparer les distance carré entre elles (et la distance maximale étant la circonsphérence de la terre)
    d_min_end = 2e+7 #ici on va comparer les distance carré entre elles (et la distance maximale étant la circonsphérence de la terre)
    id_rue_troncon_start = (0,0)
    id_rue_troncon_end = (0,0)
    if choix_transport == 1 :
        #velo
        type_eviter = ["Escalier"]
        revettements_eviter = ["Végétation","Non revêtu"]
        importance_eviter = ["Grand axe"]
        for fuv in dico_rues.keys():
            for troncon in dico_rues[fuv].keys():
                if ((dico_rues[fuv][troncon].get("Revetement_chaussee",None) == None or dico_rues[fuv][troncon]["Revetement_chaussee"] not in revettements_eviter)
                and (dico_rues[fuv][troncon].get("Importance",None) == None or dico_rues[fuv][troncon]["Importance"] not in importance_eviter)
                and (dico_rues[fuv][troncon].get("Type_circulation",None) == None or dico_rues[fuv][troncon]["Type_circulation"] not in type_eviter)):
                    for co_gps in dico_rues[fuv][troncon]['GPS'] :
                        d_start = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_start[1],co_gps_start[0])
                        d_end = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_end[1],co_gps_end[0])
                        if d_start < d_min_start :
                            id_rue_troncon_start = (fuv,troncon)
                            d_min_start = d_start
                        if d_end < d_min_end :
                            id_rue_troncon_end = (fuv,troncon)
                            d_min_end = d_end

    elif choix_transport == 2 :
        #voiture
        largeur_min_chaussee = 2.5
        type_eviter = ["Escalier","Bus","Pietons"]
        revettements_eviter = ["Végétation","Non revêtu"]
        for fuv in dico_rues.keys():
            for troncon in dico_rues[fuv].keys():
                if ((dico_rues[fuv][troncon].get("Largeur",None) == None or dico_rues[fuv][troncon]["Largeur"] >= largeur_min_chaussee)
                and (dico_rues[fuv][troncon].get("Type_circulation",None) == None or dico_rues[fuv][troncon]["Type_circulation"] not in type_eviter)
                and (dico_rues[fuv][troncon].get("Revetement_chaussee",None) == None or dico_rues[fuv][troncon]["Revetement_chaussee"] not in revettements_eviter)):
                    for co_gps in dico_rues[fuv][troncon]['GPS'] :
                        d_start = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_start[1],co_gps_start[0])
                        d_end = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_end[1],co_gps_end[0])
                        if d_start < d_min_start :
                            id_rue_troncon_start = (fuv,troncon)
                            d_min_start = d_start
                        if d_end < d_min_end :
                            id_rue_troncon_end = (fuv,troncon)
                            d_min_end = d_end

    elif choix_transport == 3 :
        # a pied
        largeur_min_trot = 0.5
        revettements_eviter = ["Pavés","Végétation","Non revêtu"]
        importance_eviter = ["Grand axe"]
        for fuv in dico_rues.keys():
            for troncon in dico_rues[fuv].keys():
                if ((dico_rues[fuv][troncon].get("Largeur_trottoir_D",None) == None or dico_rues[fuv][troncon].get("Largeur_trottoir_G",None) == None 
                or dico_rues[fuv][troncon]["Largeur_trottoir_D"] >= largeur_min_trot or dico_rues[fuv][troncon]["Largeur_trottoir_G"] >= largeur_min_trot) 
                and (dico_rues[fuv][troncon].get("Revetement_trottoir_D",None) == None or dico_rues[fuv][troncon].get("Revetement_trottoir_G",None) == None 
                or dico_rues[fuv][troncon]["Revetement_trottoir_D"] not in revettements_eviter or dico_rues[fuv][troncon]["Revetement_trottoir_G"] not in revettements_eviter)
                and (dico_rues[fuv][troncon].get("Importance",None) == None or dico_rues[fuv][troncon]["Importance"] not in importance_eviter)):
                    for co_gps in dico_rues[fuv][troncon]['GPS'] :
                        d_start = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_start[1],co_gps_start[0])
                        d_end = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_end[1],co_gps_end[0])
                        if d_start < d_min_start :
                            id_rue_troncon_start = (fuv,troncon)
                            d_min_start = d_start
                        if d_end < d_min_end :
                            id_rue_troncon_end = (fuv,troncon)
                            d_min_end = d_end

    else :
        # par defaut poussette
        pente_max = 8
        pente_moy = 5
        largeur_min_trot = 1.5
        revettements_eviter = ["Pavés","Végétation","Non revêtu"]
        importance_eviter = ["Grand axe"]
        for fuv in dico_rues.keys():
            for troncon in dico_rues[fuv].keys():
                if ((dico_rues[fuv][troncon].get("Pente_max",None) == None or dico_rues[fuv][troncon]["Pente_max"] <= pente_max) 
                and (dico_rues[fuv][troncon].get("Pente_moy",None) == None or dico_rues[fuv][troncon]["Pente_moy"] <= pente_moy)
                and (dico_rues[fuv][troncon].get("Largeur_trottoir_D",None) == None or dico_rues[fuv][troncon].get("Largeur_trottoir_G",None) == None 
                or dico_rues[fuv][troncon]["Largeur_trottoir_D"] >= largeur_min_trot or dico_rues[fuv][troncon]["Largeur_trottoir_G"] >= largeur_min_trot) 
                and (dico_rues[fuv][troncon].get("Revetement_trottoir_D",None) == None or dico_rues[fuv][troncon].get("Revetement_trottoir_G",None) == None 
                or dico_rues[fuv][troncon]["Revetement_trottoir_D"] not in revettements_eviter or dico_rues[fuv][troncon]["Revetement_trottoir_G"] not in revettements_eviter)
                and (dico_rues[fuv][troncon].get("Importance",None) == None or dico_rues[fuv][troncon]["Importance"] not in importance_eviter)):
                    for co_gps in dico_rues[fuv][troncon]['GPS'] :
                        d_start = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_start[1],co_gps_start[0])
                        d_end = dist_lat_lon_deg(co_gps[1],co_gps[0],co_gps_end[1],co_gps_end[0])
                        if d_start < d_min_start :
                            id_rue_troncon_start = (fuv,troncon)
                            d_min_start = d_start
                        if d_end < d_min_end :
                            id_rue_troncon_end = (fuv,troncon)
                            d_min_end = d_end
    return id_rue_troncon_start, id_rue_troncon_end
    
def gestion_saisie(saisie_user, l_communes):
    """Donne l'adresse complete valide d'une saisie de l'utilisateur

    Args:
        saisie_user (str): saise de l'utilisateur dans le champs d'entree de l'interface graphique
        l_communes (list): la liste des communes

    Returns:
        int: numero de l'adresse
        str: le nom de la rue de l'adresse
        str: le nom de la commune de l'adresse
        list: la liste des communes possibles
        float: la latitude de l'adresse
        float: la longitude de l'adresse
    """
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
    """Donne une liste des adresse possible en rapport avec la saisie de l'utilisateur

    Args:
        numero (int): le numero de l'adresse
        rue (str): le nom de la rue
        commune (str): le nom de la commune
        com_possibles (list): liste des communes possible
        latitude (float): la latitude de l'adresse
        longitude (float): la longitude de l'adresse
        dico_adresses_num (dict): le dictionnaire des numéros des adresses
        dico_adresses_rues (dict): le dictionnaire des noms des rues
        dico_adresses_communes (dict): le dictionnaire des noms des communes

    Returns:
        list:liste d'adresse possible
    """
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
                liste_adresses.append(commune+" centre")
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
    """
    Donne la distance entre 2 points connaissant leurs coordonnées GPS
    return :
        float: la distance entre 2 points
    """ 
    distance = 0.0
    if abs(math.sin(math.radians(start_lat)) * math.sin(math.radians(end_lat)) + math.cos(math.radians(start_lon) - math.radians(end_lon)) * math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat))) < 1:
        # formule de la distance entre 2 points sur une sphère
        distance = 6371000*math.acos(math.sin(math.radians(start_lat)) * math.sin(math.radians(end_lat)) + math.cos(math.radians(start_lon) - math.radians(end_lon)) * math.cos(math.radians(start_lat)) * math.cos(math.radians(end_lat)))
    return distance

def a_star(start, goal, rues_adjacentes, dico_rues, crit_sens, crit_vitesse):
    """Algorithme de parcours de graphs qui donne le chemins le plus courts entre 2 points en suivant le graphs

    Args:
        start (tuple): point de depart (FUV,Troncon)
        goal (tuple): point d'arrivee (FUV,Troncon)
        rues_adjacentes (dict): le dictionnaire d'adjacence du graph parcouru
        dico_rues (dict): le dictionnaire des proprietes des rues
        crit_sens (Bool): active ou non le sens des rues
        crit_vitesse (Bool): active ou non la vitesse des rues

    Returns:
        list: la liste des couples (FUV,Troncon) du chemin calculé
        float: la distance de ce chemin calculé
    """
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
        if crit_sens:
            sens_current = dico_rues[current[0]][current[1]]["Sens_circulation"]
        else:
            sens_current = "Double"
            
        if sens_current == "Conforme":
            lat_lon_current.pop(0)
        elif sens_current == "Inverse":
            lat_lon_current.pop(-1)
        # Récupérer le noeud avec la plus petite priorité dans la file
        if current == goal: 
            itinerary = True
        else:
            for next_node in rues_adjacentes[current]:# On récupère le tuple coordonées des adj : (fuv,troncon)
                lat_lon_node = [dico_rues[next_node[0]][next_node[1]]['GPS'][0],dico_rues[next_node[0]][next_node[1]]['GPS'][-1]]
                if crit_sens:
                    sens = dico_rues[next_node[0]][next_node[1]]["Sens_circulation"]
                else:
                    sens = "Double"
                if (sens == "Conforme" and lat_lon_node[0] in lat_lon_current) or (sens == "Inverse" and lat_lon_node[-1] in lat_lon_current) or (sens=="Double"):
                    if crit_vitesse:
                        vitesse = int(dico_rues[next_node[0]][next_node[1]]["Limitation_vitesse"])
                    else:
                        vitesse = 1
                    new_cost = cost_so_far[current] + (dico_rues[next_node[0]][next_node[1]]["Longueur"]/vitesse)  # Calculer le coût pour atteindre le voisin en passant par le noeud actuel
                    if next_node not in cost_so_far.keys() or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost  # Mettre à jour le coût pour atteindre le voisin
                        if lat_lon_current[0] == lat_lon_node[0] or lat_lon_current[-1] == lat_lon_node[0]:
                            co_end_node = lat_lon_node[-1]
                        else:
                            co_end_node = lat_lon_node[0]
                        if crit_vitesse:
                            vitesse_max = 50
                        else:
                            vitesse_max = 1
                        priority = new_cost + (dist_lat_lon_deg(co_end_node[1],co_end_node[0],co_moy_goal[1],co_moy_goal[0])/vitesse_max)  # Calculer la priorité pour le voisin
                        queue.put((priority, next_node))  # Ajouter le voisin à la file avec sa nouvelle priorité
                        came_from[next_node] = current  # Stocker le noeud actuel comme parent du voisin exploré
                        
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

    print ("Le chemin le plus court est : ", path,', Pour une distance de ', dist_path, 'mètres (sauf mode voiture)')
    return path, dist_path

def compute_cross(fuv_tr_pre, fuv_tr_suiv, dico_rues, rues_adjacentes):
    """Permet de convertir les coordonnées GPS (lat,long) en un systeme de coordonnées cartesiennes pour tracer facilement les routes sur un canvas

    Args:
        fuv_tr_pre (_type_): _description_
        fuv_tr_suiv (_type_): _description_
        dico_rues (dict): le dictionnaire qui contient les proprietes des rues
        rues_adjacentes (dict): le dictionnaire d'adjacence

    Returns:
        dict: le dictionnaire d'adjence en coordonnees cartesienne
        float: 
    """
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
    return dico_fuv_tr_xy, co_gps_noeud[-1], co_gps_noeud[0]

def xy_lat_long(latitude, longitude, latitude_ref):
    """effectue le conversion de la latitude et de la longitude en coordonnées cartesienne

    Args:
        latitude (float): la latitude du point
        longitude (float): la longitude du point
        latitude_ref (float): la latitude de reférence du lieu

    Returns:
        list: les coordonnées cartesiennes du point
    """
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
    """Donne l'angle entre 2 points dans le systeme de coordonnees GPS

    Args:
        x1 (float): abscisse du premier point
        y1 (float): ordonnee du premier point
        x2 (float): abscisse du deuxieme point
        y2 (float): ordonnee du deuxieme point

    Returns:
        float: l'angle
    """
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
    """Effectue la rotations des coordonnées pour changer de repere dans les coordonnées cartesienne (pour toujours mettre la route suivante vers le haut même vision que dans la voiture)

    Args:
        angle (float): l'angle de rotation
        dico_fuv_tr_adj (dict): le dictionnaire d'adjacence en coordonnées cartesienne

    Returns:
        dict: le dictionnaire d'adjacence avec la rotation effectuée
    """
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
    """donne un dictionnaire en coordonnée cartesienne et a l'echelle de l'affichage

    Args:
        dist_min (float): la distance minimale a afficher
        dico_fuv_tr_rot (dict): le dictionanire des coordonnées en cartesiennes
        xy_noeud (tuple): la position du noeud central d'affichage
        width_canvas (float): largeur du canvas
        height_canvas (float): hauteur du canvas

    Returns:
        dict: le nouveau dictionnaire
    """
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
    """donne la norme minimale

    Args:
        dico_fuv_tr_rot (dict): le dictionnaire des (fUV,Troncons)

    Returns:
        float: la norme minimale
    """
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
    """Calcule la distance minimale

    Args:
        dico_fuv_tr_adj (dict): le dictionnaire des (fUV,Troncons)

    Returns:
        float: la distance minimale
    """
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
    """calcule la distance entre 2 points

    Args:
        co_gps (list): liste de coordonnees gps
        index1 (int): le tuple du coordonnees gps choisi
        index2 (int): le tuple du coordonnees gps choisi

    Returns:
        float: la distance
    """
    # distance selon la norme 2 entre 2 points definis par leur index dans une liste de coordonnees
    return math.sqrt((co_gps[index2][0]-co_gps[index1][0])**2+(co_gps[index2][1]-co_gps[index1][1])**2)


def instructions(dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv, dico_rues):
    """Retourne les instructions en texte selon la nouvelle direction/route à prendre

    Args:
        dico_fuv_tr_carte (dict): le dictionnaire d'adjancence (FUV,Troncon)
        fuv_tr_pre (tuple): code (fuv,troncon) du point precedent
        fuv_tr_suiv (tuple): code (fuv,troncon) du point suivant
        dico_rues (dict): le dictionnaire contient les proprietes des rues
    Returns:
        str: les instructions à afficher sur l'interface graphique
    """

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
    """Donne la consigne associe a un noeud pour un suivant

    Args:
        fuv_tr_pre (tuple): code (fuv,troncon) du noeud precedent
        fuv_tr_suiv (tuple): code (fuv,troncon) noeud suivant
        dico_rues (dict): dictionnaire des proprietes de rues
        rues_adjacentes (dict): dictionnaire d'adjacence

    Returns:
        str: les instructions
    """
    #Recherche des segments adjacents, compilation de leurs co GPS dans un dictionnaire
    #puis passage en co cartesienne
    dico_fuv_tr_adj, lat_noeud, long_noeud = compute_cross(fuv_tr_pre, fuv_tr_suiv, dico_rues, rues_adjacentes)
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

if __name__ == "__main__" :
    adj,rue = charger_donnees_troncon()