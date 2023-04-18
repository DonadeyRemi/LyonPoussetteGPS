# -*- coding: utf-8 -*-
"""
Created on Mon Apr 10 13:11:56 2023

@author: timhu
"""
# Resultats sans le fichier chaussées:
# méthode noeuds+GPS : 38115 clés dans le dico d'adjacences
# méthode 100% GPS : 38134 clés dans le dico d'adjacences

# 27 clés trouvées en plus dans le dico d'adjacences avec la méthode 100% GPS
# 8 clés oubliées --> ces clés sont :
    # - soit des clés isolées qui ne sont pas intérréssantes car pas reliées au réseau 
    # - soit des clés faussement isolées en raison d'une erreur dans les co GPS
    #   dans ce cas le dico d'adjacence avec la méthode noeuds+GPS les incluait mais avec aucune adjacence
# 1656 adjacences supplémentaires trouvées avec avec la méthode 100% GPS
# aucunes oubliées

# Conclusion il semble intérresant d'utiliser la méthode 100% GPS

# Resultat avec le fichier chaussées:
# méthode noeuds+GPS : 38115 clés dans le dico d'adjacences
# méthode 100% GPS : 38239 clés dans le dico d'adjacences
# 130 clés trouvées en plus dans le dico d'adjacences avec la méthode 100% GPS
# 6 clés oubliées --> ces clés sont :
    # - soit des clés isolées qui ne sont pas intérréssantes car pas reliées au réseau 
    # - soit des clés faussement isolées en raison d'une erreur dans les co GPS
    #   dans ce cas le dico d'adjacence avec la méthode noeuds+GPS les incluait mais avec aucune adjacence
# 37465 adjacences supplémentaires trouvées avec avec la méthode 100% GPS
# aucunes oubliées

import json
f_troncons_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Troncons_trame_viaire.geojson"
f_noeuds_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Noeuds_trame_viaire.geojson"
f_chausses_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Chaussees_et_trottoirs.geojson"

def charger_donnees():
    with open(f_troncons_geojson,encoding='utf-8') as fichier :
        data = json.load(fichier)
    dico_gps = {}
    dico_rues = {}    
    for segment in data["features"]:
        co_gps_rue = list(segment["geometry"]["coordinates"])
        rue = segment["properties"]["codefuv"]
        troncon = segment["properties"]["codetroncon"]
        for i in range(len(co_gps_rue)):
            co_gps_rue[i][0] = round(co_gps_rue[i][0], 12)
            co_gps_rue[i][1] = round(co_gps_rue[i][1], 12)
        
        if rue not in dico_rues.keys():
            dico_rues[rue] = {troncon: {"GPS" : co_gps_rue} }
        else:
            dico_rues[rue][troncon] = {"GPS" : co_gps_rue}
        
        for co_gps in co_gps_rue:
            tuple_gps = (co_gps[0],co_gps[1])
            if tuple_gps not in dico_gps.keys():
                dico_gps[tuple_gps]={}
            if rue not in dico_gps[tuple_gps].keys():
                dico_gps[tuple_gps][rue]=[]
            if troncon not in dico_gps[tuple_gps][rue]:
                dico_gps[tuple_gps][rue].append(troncon)
                
    # with open(f_chausses_geojson,encoding='utf-8') as fichier :
    #     data = json.load(fichier)
    # for segment in data["features"]:
    #     proprietes = segment["properties"]
    #     troncon = proprietes["codetroncon"]
    #     rue = proprietes["codefuv"]
    #     co_gps_rue = list(segment["geometry"]["coordinates"])
    #     for i in range(len(co_gps_rue)):
    #         co_gps_rue[i][0] = round(co_gps_rue[i][0],12)
    #         co_gps_rue[i][1] = round(co_gps_rue[i][1],12)        
        
    #     for co_gps in co_gps_rue:
    #         tuple_gps = (co_gps[0],co_gps[1])
    #         if tuple_gps not in dico_gps.keys():
    #             dico_gps[tuple_gps]={}
    #         if rue not in dico_gps[tuple_gps].keys():
    #             dico_gps[tuple_gps][rue]=[]
    #         if troncon not in dico_gps[tuple_gps][rue]:
    #             dico_gps[tuple_gps][rue].append(troncon)
        
    a_supprimer = []
    for tuple_gps in dico_gps:
        if len(dico_gps[tuple_gps]) < 2:
            for rue in dico_gps[tuple_gps]:
                if len(dico_gps[tuple_gps][rue]) < 2:
                    a_supprimer.append(tuple_gps)
    for tuple_gps in a_supprimer:
        dico_gps.pop(tuple_gps)
 
    rues_adj_gps = {}
    for noeud in dico_gps:
        liste_adj = []
        for rue in dico_gps[noeud]:
            for troncon in dico_gps[noeud][rue]:
                liste_adj.append((rue,troncon))
        for (rue,troncon) in liste_adj:
            if (rue,troncon) not in rues_adj_gps.keys() :
                if len(liste_adj) == 1 :
                    rues_adj_gps[(rue,troncon)] = []
                else:
                    rues_adj_gps[(rue,troncon)] = []
                    for i in liste_adj :
                        if i != (rue,troncon) :
                            rues_adj_gps[(rue,troncon)].append(i)
            else:
                for i in liste_adj :
                    if i != (rue,troncon) :
                        rues_adj_gps[(rue,troncon)].append(i)

    with open(f_noeuds_geojson,encoding='utf-8') as fichier :
        data = json.load(fichier)   
    rues_adjacentes = {}
    for carrefour in data["features"] :
        co_gps_car = list(carrefour["geometry"]["coordinates"])
        co_gps_car[0] = round(co_gps_car[0], 12)
        co_gps_car[1] = round(co_gps_car[1], 12)
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
    
    print(len(rues_adjacentes))
    print(len(rues_adj_gps))
    print()
    cherche_erreur(rues_adj_gps, rues_adjacentes)
    cherche_erreur(rues_adjacentes, rues_adj_gps)
    
def cherche_erreur(rues_adj_1, rues_adj_2):
    cles_diff = []
    adja_diff = []
    compteur_1_en_plus = 0
    compteur_2_en_plus = 0
    compteur_inversion = 0
    for (rue,troncon) in rues_adj_1:
        if (rue, troncon) not in rues_adj_2.keys():
            cles_diff.append((rue, troncon))
            #print((rue,troncon))
        elif len(rues_adj_1[(rue,troncon)]) != len(rues_adj_2[(rue,troncon)]):
            if len(rues_adj_1[(rue,troncon)]) > len(rues_adj_2[(rue,troncon)]):
                compteur_1_en_plus += 1
            else:
                compteur_2_en_plus += 1
            adja_diff.append(((rue,troncon),rues_adj_1[(rue,troncon)],rues_adj_2[(rue,troncon)]))
        else:
            different = False
            i = 0
            while i < len(rues_adj_1[(rue,troncon)]) and not different:
                if rues_adj_1[(rue,troncon)][i] not in rues_adj_2[(rue,troncon)]:
                    different = True
                i += 1
            if different:
                adja_diff.append(((rue,troncon),rues_adj_1[(rue,troncon)],rues_adj_2[(rue,troncon)]))
                compteur_inversion += 1
    # print(cles_diff)
    # for (rue, troncon) in cles_diff:
    #     print(rues_adj_1[(rue, troncon)])
    # for (((rue,troncon),adj_1,adj_2)) in adja_diff:
    #     print(((rue,troncon),adj_1,adj_2))
    #     print()
    print(len(cles_diff))      
    print(len(adja_diff),"  =  ",compteur_1_en_plus,"  +  ",compteur_2_en_plus,"  +  ",compteur_inversion)
    # print()


charger_donnees() 