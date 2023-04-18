# -*- coding: utf-8 -*-
"""
Created on Mon Apr 17 18:16:30 2023

@author: timhu
"""
# arrondi initial à 12 chiffres après la virgule
# resultats pour differents arrondi avec le fichier chaussées:
    # 11 - 0 différence
    # 10 - 26 différences
    # 9 - 191 différences
    # 8 - 206 différences
    # 7 - 207 différences
    # 6 - 208 différences
    # 5 - 213 différences
    # 4 - cela n'a plus de sens
    
# --------------------------------- sans le fichier chaussées:
    # 11 - 0 différence
    # 10 - 0 différence
    # 9 - 0 différence
    # 8 - 0 différence
    # 7 - 0 différence
    # 6 - 12 différences
    # 5 - 20 différences
        # ('34256', 'T31231')  ---->  [('34261', 'T30611')]
        # il s'agit d'une fausse erreur
    # 4 - cela n'a plus de sens
    
# Detail de la diff entre arrondi à 12 et à 5 sans chaussées:
    
# ('22542', 'T52706')  ---->  [('22542', 'T52710')]
# ('33721', 'T51758')  ---->  [('37062', 'T51760')]
# ('33721', 'T51759')  ---->  [('37062', 'T51760')]
# ('37062', 'T51760')  ---->  [('33721', 'T51758'), ('33721', 'T51759')]
# ('34261', 'T30611')  ---->  [('34256', 'T31231')]
# ('34256', 'T31231')  ---->  [('34261', 'T30611')]
# ('22542', 'T52710')  ---->  [('22542', 'T52706'), ('22542', 'T52707')]
# ('22542', 'T52707')  ---->  [('22542', 'T52710')]
# ('02786', 'T6733')  ---->  [('02786', 'T50310'), ('02786', 'T50311')]
# ('02786', 'T50310')  ---->  [('02786', 'T6733')]
# ('02786', 'T50311')  ---->  [('02786', 'T6733')]
# ('26166', 'T10752')  ---->  [('33143', 'T50167'), ('33143', 'T50166')]
# ('33143', 'T50167')  ---->  [('26166', 'T10752')]
# ('33143', 'T50166')  ---->  [('26166', 'T10752')]
# ('34042', 'T38685')  ---->  [('25180', 'T53325'), ('25180', 'T53326')]
# ('28348', 'T49577')  ---->  [('28348', 'T49579')]
# ('28348', 'T49579')  ---->  []
# ('28348', 'T49578')  ---->  [('28348', 'T49579')]
# ('25180', 'T53325')  ---->  [('34042', 'T38685')]
# ('25180', 'T53326')  ---->  [('34042', 'T38685')]
# 20

import json

def charger_donnees(arrondi_gps=12):
    f_troncons_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Troncons_trame_viaire.geojson"
    f_chausses_geojson = r"C:\Users\timhu\Documents\1_Scolaire\INSA_2A\Informatique\Projet\Donnees_projet\Chaussees_et_trottoirs.geojson"
    #f_troncons_geojson = "troncon_trame_viaire.geojson"
    #f_chausses_geojson = "chaussees_trotoirs.geojson"
   
    with open(f_troncons_geojson,encoding='utf-8') as fichier :
        data = json.load(fichier)
    dico_noeuds = {}
    for segment in data["features"]:
        co_gps_rue = list(segment["geometry"]["coordinates"])
        rue = segment["properties"]["codefuv"]
        troncon = segment["properties"]["codetroncon"]
        for i in range(len(co_gps_rue)):
            co_gps_rue[i][0] = round(co_gps_rue[i][0],arrondi_gps)
            co_gps_rue[i][1] = round(co_gps_rue[i][1],arrondi_gps)
        
        for co_gps in co_gps_rue:
            tuple_gps = (co_gps[0],co_gps[1])
            if tuple_gps not in dico_noeuds.keys():
                dico_noeuds[tuple_gps]={}
            if rue not in dico_noeuds[tuple_gps].keys():
                dico_noeuds[tuple_gps][rue]=[]
            if troncon not in dico_noeuds[tuple_gps][rue]:
                dico_noeuds[tuple_gps][rue].append(troncon)
    
                
    # with open(f_chausses_geojson,encoding='utf-8') as fichier :
    #     data = json.load(fichier)
    # for segment in data["features"]:
    #     proprietes = segment["properties"]
    #     troncon = proprietes["codetroncon"]
    #     rue = proprietes["codefuv"]
    #     co_gps_rue = list(segment["geometry"]["coordinates"])
    #     for i in range(len(co_gps_rue)):
    #         co_gps_rue[i][0] = round(co_gps_rue[i][0],arrondi_gps)
    #         co_gps_rue[i][1] = round(co_gps_rue[i][1],arrondi_gps)        
        
    #     for co_gps in co_gps_rue:
    #         tuple_gps = (co_gps[0],co_gps[1])
    #         if tuple_gps not in dico_noeuds.keys():
    #             dico_noeuds[tuple_gps]={}
    #         if rue not in dico_noeuds[tuple_gps].keys():
    #             dico_noeuds[tuple_gps][rue]=[]
    #         if troncon not in dico_noeuds[tuple_gps][rue]:
    #             dico_noeuds[tuple_gps][rue].append(troncon)
        
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

    #print(len(rues_adj_gps))
    decompte_adj = 0
    # liste_rues = [('36008', 'T45654'),('33947', 'T48018'),('19762', 'T10561')]
    for rue in rues_adj_gps:
        # if rue in liste_rues:
        #     print(rue, " ----> ", rues_adj_gps[rue])
        for adjacent in rues_adj_gps[rue]:
            decompte_adj += 1
    print(decompte_adj/2)
    return rues_adj_gps

rues_adj_sans = charger_donnees(12)
rues_adj_avec = charger_donnees(5)
print()

nb_erreurs = 0
for rue in rues_adj_avec:
    erreur = False
    liste_erreurs = []
    if rue not in rues_adj_sans:
        erreur = True
    else:
        for adjacent in rues_adj_avec[rue]:
            if adjacent not in rues_adj_sans[rue]:
                erreur = True
                liste_erreurs.append(adjacent)
    if erreur:
        nb_erreurs += 1
        print(rue, " ----> ", liste_erreurs)
        # print(rues_adj_sans[rue])
        # print(rues_adj_avec[rue])
        # print()
print(nb_erreurs)

