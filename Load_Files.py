import json

def load_data_nodes():
    #ouverture du fihcier des noeuds de la trame viaire
    with open("noeud_trame_viaire.geojson",'r') as fichier :
        data = json.load(fichier)

    print(data["features"][1]["properties"])
    carrefour_adjacence = {}
    for carrefour in data["features"] :
        if len(carrefour["properties"]['codefuvcarrefour']) > 0 :
            liste_car_ad = carrefour["properties"]['codefuvcarrefour'].split("+")
            liste_car_ad = list(map(int, liste_car_ad))
            for car in liste_car_ad :
                if car not in carrefour_adjacence.keys() :
                    if len(liste_car_ad) == 1 :
                        carrefour_adjacence[car] = []

                    else :
                        liste_car_2 = [i for i in liste_car_ad if i != car]
                        carrefour_adjacence[car] = liste_car_2

                else : 
                    for i in liste_car_ad :
                        if i != car :
                            carrefour_adjacence[car].append(i)

    # obtient le dictionnaire d'adjacence des carrefour à chaque carrefour est associe le carrefour auxquel il peut donner -> graphe non oriente
    print(carrefour_adjacence)
    return carrefour_adjacence