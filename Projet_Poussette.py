#!/usr/bin/python
# -*- encoding: utf8 -*-

import tkinter as tk
import math
from tkinter import ttk
from tkinter.ttk import Separator
from tkinter import messagebox
import Load_Files

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from shapely.geometry import LineString,Point
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MainWindow():
    def __init__(self) :
        # on initialise d'abord la fenetre principale sur un affichage de chargement, le temps que les donnees se chargent
        self.root = tk.Tk()
        self.root.geometry("300x200")
        self.loading_label_1 = tk.Label(self.root, text = "Chargement des données", font = "Calibri 16")
        self.loading_label_1.pack(anchor = tk.CENTER)
        self.loading_label_2 = tk.Label(self.root, text = "Veuillez patienter", font = "Calibri 13")
        self.loading_label_2.pack(anchor = tk.CENTER)
        self.root.title("Lyonyroule")
        # la fonction load_all_datas est lancée au bout de 100ms après le démarage (cf. ligne 679 (plus à jour))
        # la fonction initWidget est appelée à la fin de la fonction load_all_datas
        
        #itineraire fictif pour test fenetre trajet
        #self.itineraire = [('22416', 'T54924'),('37324', 'T54925'),('37324', 'T54926'),('36078', 'T23765')]
        #self.itineraire = [('33788','T27222'),('33787','T27233'),('33787','T35503'),('33785','T35505'),('33786','T27243'),('33793','T27247'),('33792','T27266'),('33796','T27274'),('33796','T27275'),('33794','T27269')]
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
        self.root.geometry("1000x600")
        
         # creation de la figure matplotlib 
        self.fig,self.ax = plt.subplots(figsize=(8,8))
        #mise en place du fond de carte
        image = mpimg.imread(r"C:/Users/timhu/Documents/1_Scolaire/INSA_2A/Informatique/Projet/Donnees_projet/fond_carte1.png")
        height, width, channels = image.shape
        self.ax.imshow(image,extent = [4.56, 5.2, 45.500, 46.03])

        # data_commune.boundary.plot(ax=self.ax,color="black",linewidth=1.0)


        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)  # A tk.DrawingArea.
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.Y)


        separator_canvas = Separator(self.root,orient=tk.VERTICAL)
        separator_canvas.pack(side=tk.LEFT,fill=tk.Y)

        #frame qui contient les widget en mode choix itinaire
        self.frame_princ = tk.Frame(self.root)

        self.frame_dest = tk.Frame(self.frame_princ,padx=5,pady=5)

        self.liste_depart = []
        self.var_entry_start = tk.StringVar(value = "Départ")
        self.start_selection = ttk.Combobox(self.frame_dest, textvariable=self.var_entry_start, values = self.liste_depart, width = 80, foreground = "black")
        self.start_selection.bind("<KeyRelease-space>",self.get_entry_start)
        self.start_selection.bind("<Button-1>",self.effacer_start)
        self.start_selection.bind("<KeyRelease-Return>", self.down_start)
        self.start_selection.bind("<<ComboboxSelected>>", self.choose_start)
        self.start_selection.pack(side=tk.TOP, anchor = tk.N, fill=tk.X)
        
        self.liste_arrivee = []
        self.var_entry_end = tk.StringVar(value = "Arrivée")
        self.end_selection = ttk.Combobox(self.frame_dest, textvariable=self.var_entry_end, values = self.liste_arrivee , foreground = "black")
        self.end_selection.bind("<KeyRelease-space>",self.get_entry_end)
        self.end_selection.bind("<Button-1>",self.effacer_end)
        self.end_selection.bind("<KeyRelease-Return>", self.down_end)
        self.end_selection.bind("<<ComboboxSelected>>", self.choose_end)
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
        self.check_button_poussette.pack(side=tk.TOP,fill=tk.X)

        self.choice_bike = tk.IntVar()
        self.check_button_bike = tk.Checkbutton(self.frame_opt,
                                                bg='gray', fg = 'black', anchor = 'w',
                                                text = "          Vélo", onvalue=True,
                                                offvalue = False, variable = self.choice_bike)
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

        self.var_prop_trajet = tk.StringVar(value=f"Votre Trajet\n {self.var_entry_start.get()} vers {self.var_entry_end.get()}")
        self.label_trajet_prop = tk.Label(self.frame_trajet,textvariable=self.var_prop_trajet,padx=5,pady=5)
        self.label_trajet_prop.pack(side=tk.TOP,fill=tk.X)

        self.button_change_iti = tk.Button(self.frame_trajet,text="Modifier votre itineraire",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_change_iti.pack(side=tk.TOP,fill=tk.X)
        self.button_change_iti.bind("<Button-1>",self.bouton_change_iti)

        
        self.button_stop_iti = tk.Button(self.frame_trajet,text="Arreter l'itineraire en cours",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_stop_iti.pack(side=tk.BOTTOM,fill=tk.X)
        self.button_stop_iti.bind("<Button-1>",self.stop_iti)
        
        self.button_start_iti = tk.Button(self.frame_trajet,text="Commencer votre itinéraire",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_start_iti.pack(side=tk.BOTTOM,fill=tk.X)
        self.button_start_iti.bind("<Button-1>",self.open_window_trajet)

        self.frame_trajet.pack_forget()

    def loop(self):
        self.root.mainloop()

    def get_entry_start(self, event):
        if event.widget.get() != self.saisie_user_start and event.widget.get() != "":
            self.saisie_user_start = event.widget.get()
            self.liste_depart = Load_Files.give_troncon_address(self.saisie_user_start, self.dico_adresses_num, self.dico_adresses_rues, self.l_communes)
            # rajouter option si len(self.liste_depart) == 1 (choose_start ou down_start)
            self.start_selection.configure(values = self.liste_depart)
        self.start_selection.configure(foreground = "red")
    
    def down_start(self, event):
        if event.widget.get() != self.saisie_user_start and event.widget.get() != "":
            self.saisie_user_start = event.widget.get()
            self.liste_depart = Load_Files.give_troncon_address(self.saisie_user_start, self.dico_adresses_num, self.dico_adresses_rues, self.l_communes)
            self.start_selection.configure(values = self.liste_depart)
        self.start_selection.event_generate('<Down>',when="tail")
    
    def choose_start(self, event):
        self.start_selection.configure(foreground = "green")
        choix = event.widget.get().split(" ")
        a_suppr = []
        for i in range(len(choix)):
            if choix[i] == "" or choix[i] == " ":
                a_suppr.append(i)
        a_suppr.reverse()
        for i in a_suppr:
            choix.pop(i)
        if len(choix) == 2 and choix[-1] == "centre":
            print("centre")
            self.depart = ("centre","centre")
        else : 
            numero = choix.pop(0)
            commune = choix.pop(-1)
            rue = ""
            for i in range(len(choix)):
                rue += choix[i]
                if i < len(choix)-1:
                        rue += " "
            co_gps = self.dico_adresses_num[numero][rue][commune]
            self.depart = Load_Files.give_troncon_nearest_gps(co_gps, self.dico_rues)
        
        print()
        print(self.depart)
        print()
    
    def effacer_start(self,event):
        if self.start_selection.get() == "Départ":
            self.start_selection.set("")
            
    def get_entry_end(self, event):
        if event.widget.get() != self.saisie_user_end and event.widget.get() != "":
            self.saisie_user_end = event.widget.get()
            self.liste_arrivee = Load_Files.give_troncon_address(self.saisie_user_end, self.dico_adresses_num, self.dico_adresses_rues, self.l_communes)
            # rajouter option si len(self.liste_end) == 1 (choose_end ou down_end)
            self.end_selection.configure(values = self.liste_arrivee)
        self.end_selection.configure(foreground = "red")
    
    def down_end(self, event):
        if event.widget.get() != self.saisie_user_end and event.widget.get() != "":
            self.saisie_user_end = event.widget.get()
            self.liste_arrivee = Load_Files.give_troncon_address(self.saisie_user_end, self.dico_adresses_num, self.dico_adresses_rues, self.l_communes)
            self.end_selection.configure(values = self.liste_arrivee)
        self.end_selection.event_generate('<Down>',when="tail")
    
    def choose_end(self, event):
        self.end_selection.configure(foreground = "green")
        choix = event.widget.get().split(" ")
        a_suppr = []
        for i in range(len(choix)):
            if choix[i] == "" or choix[i] == " ":
                a_suppr.append(i)
        a_suppr.reverse()
        for i in a_suppr:
            choix.pop(i)
        if len(choix) == 2 and choix[-1] == "centre":
            print("centre")
            self.arrivee = ("centre","centre")
        else : 
            numero = choix.pop(0)
            commune = choix.pop(-1)
            rue = ""
            for i in range(len(choix)):
                rue += choix[i]
                if i < len(choix)-1:
                        rue += " "
            co_gps = self.dico_adresses_num[numero][rue][commune]
            self.arrivee = Load_Files.give_troncon_nearest_gps(co_gps, self.dico_rues)
        
        print()
        print(self.arrivee)
        print()
    
    def effacer_end(self,event):
        if self.end_selection.get() == "Arrivée":
            self.end_selection.set("")

    def bouton_param_av(self,event):
        print("Vous avez cliquez sur le boutons des parametres avancé")
        print(f"Ville de départ {self.var_entry_start.get()}")
        print(f"Ville d'arrivee {self.var_entry_end.get()}")
        print(f"Choix Poussette {self.choice_poussette.get()}")

        self.dialog_params_av = TopLevelParams(self.root)

    def start_research(self,event):
        """Fonction callback du bouton de calcul de l'itineraire, il lance la recherche de l'itineraire
        Args:
            event (dict): the tk event object return after the user event
        """
        if self.depart != (None,None) and self.arrivee != (None,None):
            self.itineraire, self.dist_trajet = Load_Files.a_star(self.depart,self.arrivee,self.carrefour_adjacences, self.dico_rues)
            print(self.dico_rues[self.itineraire[0][0]][self.itineraire[0][1]]['GPS'])
            #on cache la frame principale et affiche la frame itineraire
            self.frame_princ.pack_forget()
            self.var_prop_trajet.set(f"Votre Trajet\n {self.var_entry_start.get()} vers {self.var_entry_end.get()}")
            self.frame_trajet.pack(fill=tk.Y)
            # on appelle la fonction qui affiche la carte principale
            self.show_large_map()
            
    def show_large_map(self):
        co_trajet = []
        for fuv_rue in self.itineraire :
            co_gps_liste = self.dico_rues[fuv_rue[0]][fuv_rue[1]]['GPS']
            for co_gps in co_gps_liste :
                co_trajet.append(Point(co_gps[0],co_gps[1]))            

        geo_trajet_data = gpd.GeoDataFrame(geometry=[LineString(co_trajet)])

        #mise a jour de la carte 
        geo_trajet_data.plot(ax=self.ax)
        self.canvas.draw()

    def bouton_change_iti(self,event):
        msg_user = messagebox.askyesno("Changer d'itineraire ?","Voulez vous vraiment changer d'itinéraire ?\n Celui-ci sera perdu")
        if msg_user == True :
            #Affiche de nouveau le frame principal
            self.frame_trajet.pack_forget()
            self.frame_princ.pack(fill=tk.Y)
        
    def open_window_trajet(self,event):
        """Fonction callback du bouton commencer le trajet, ouvre la fenetre du trajet carrefour par carrefour
        Args:
            event (dict): the tk event object return after the user event 
        """
        TopLevelParcour(self.root, self.dico_rues, self.carrefour_adjacences, self.itineraire)

    def stop_iti(self,event):
        """Fonction callback du bouton arreter le trajet, ferme la fenetre topLevel trajet si ouverte et revient à la frame principale
        Args:
            event (dict): the tk event object return after the user event
        """
        self.frame_trajet.pack_forget()
        self.frame_princ.pack(fill=tk.Y)


    def load_all_datas(self):
        self.carrefour_adjacences,self.dico_rues, self.dico_adresses_num, self.dico_adresses_rues, self.l_communes = Load_Files.charger_donnees()
        #une fois le chargement de donnees effectue, on met a jour l'affichage pour afficher le menu d'acceuil
        self.initWidget() 


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
    def __init__(self, mainwindow, dico_rues, rues_adjacentes, itineraire):
        self.mainwindow = mainwindow
        self.dico_rues = dico_rues
        self.rues_adjacentes = rues_adjacentes
        self.itineraire = itineraire
        self.etape = 0
        
        self.liste_echelles = [0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000]
        
        self.toplevel_parcour = tk.Toplevel(self.mainwindow)
        self.toplevel_parcour.resizable(height = False, width = False) 
        self.toplevel_parcour.title = "Trajet"
        
        self.f_par_width = 400
        self.f_par_height = 500
        self.toplevel_parcour.geometry(f"{self.f_par_width}x{self.f_par_height}")

        self.init_widget()
        self.show_iti(self.itineraire[0],self.itineraire[1])

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
        dico_fuv_tr_adj, lat_noeud = self.compute_cross(fuv_tr_pre, fuv_tr_suiv)
        #calcul des points qui seront visible et qu'il faut donc prendreen compte pour l'orientation 
        dist_min = self.calcul_dist_min(dico_fuv_tr_adj)
        i = 1
        while i < len(dico_fuv_tr_adj["precedent"][fuv_tr_pre]) - 1 and self.distance(dico_fuv_tr_adj["precedent"][fuv_tr_pre], 0, i) < dist_min:
            i += 1
        #Calcul de l'angle entre le segment precedent (premier et dernier point GPS)
        # et l'horizontale (axe x)
        x_noeud = dico_fuv_tr_adj["precedent"][fuv_tr_pre][0][0]
        y_noeud = dico_fuv_tr_adj["precedent"][fuv_tr_pre][0][1]
        x_precedent = dico_fuv_tr_adj["precedent"][fuv_tr_pre][i][0]
        y_precedent = dico_fuv_tr_adj["precedent"][fuv_tr_pre][i][1]
        alpha_pre = self.calcul_angle(x_noeud, y_noeud, x_precedent, y_precedent)
        #Rotation du repere pour avoir le segment precedent en bas de l'ecran, vertical
        dico_fuv_tr_rot = self.rotation_repere(alpha_pre, dico_fuv_tr_adj)
        #Determination de l'extrémité d'un segment adjacent la plus proche du noeud
        # selon la norme infini (cf. cours de maths)
        # permet d'avoir la vision la plus large possible sans voir d'autres noeuds
        norme_min = self.calcul_norme_min(dico_fuv_tr_rot)
        xy_noeud = dico_fuv_tr_rot["precedent"][fuv_tr_pre][0]
        #Mise à l'echelle des co en fonction de la distance min
        dico_fuv_tr_carte = self.xy_cartesien(norme_min, dico_fuv_tr_rot, xy_noeud)
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
        self.instructions(dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv)
        
        
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
        
    def instructions(self, dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv):
        i = 1
        while i < len(dico_fuv_tr_carte["suivant"][fuv_tr_suiv]) - 1 and self.distance(dico_fuv_tr_carte["suivant"][fuv_tr_suiv], 0, i) < 200*math.sqrt(2)/2:
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
        if self.calcul_angle(x_suivant, y_suivant, x_noeud, y_noeud) < 3*math.pi/8:
            texte_instruction += "à gauche "
        elif self.calcul_angle(x_suivant, y_suivant, x_noeud, y_noeud) > 5*math.pi/8:
            texte_instruction += "à droite "
        else:
            texte_instruction += "tout droit "
        texte_instruction += "sur "
        if self.dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]].get("Nom","") != "":
            texte_instruction += self.dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]]["Nom"]
        elif self.dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]].get("Denomination_route","") != "":
            texte_instruction += self.dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]]["Denomination_route"]
        else:
            texte_instruction += "route sans nom"
        self.label_instruction.configure(text = texte_instruction)
        
    def compute_cross(self, fuv_tr_pre, fuv_tr_suiv):
        #On recup les infos sur les segments precedent et suivant
        info_pre = self.dico_rues[fuv_tr_pre[0]][fuv_tr_pre[1]]
        info_suiv = self.dico_rues[fuv_tr_suiv[0]][fuv_tr_suiv[1]]
        dico_fuv_tr_gps = {"precedent":{},"suivant":{},"adjacents":{}}
        co_gps_noeud = []
        co_gps_pre = info_pre['GPS'].copy()
        co_gps_suiv = info_suiv['GPS'].copy()
        #on identifie quel cote des segments est lié au noeud
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
        for fuv_tr in self.rues_adjacentes[fuv_tr_pre]:
            info_adj = self.dico_rues[fuv_tr[0]][fuv_tr[1]]
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
                        dico_fuv_tr_xy[categorie][troncon] = [self.xy_lat_long(co_gps[1],co_gps[0],co_gps_noeud[-1])]
                    else:
                        dico_fuv_tr_xy[categorie][troncon].append(self.xy_lat_long(co_gps[1],co_gps[0],co_gps_noeud[-1]))
        return dico_fuv_tr_xy, co_gps_noeud[-1]

    def xy_lat_long(self, latitude, longitude, latitude_ref):
        #on fait en sorte que la longitude soit comprise entre 0 et 360 et non entre -180 et 180
        longitude = longitude + 180
        #on la rapporte de 0 à 2000
        x = ((longitude*2000*math.cos(math.radians(latitude_ref)))/360)
        #idem mais la latitude est comprise entre 0 et 180
        latitude = latitude + 90
        hauteur = (latitude*1000)/180 
        y = 1000 - hauteur
        return [x, y]
    
    def calcul_angle(self, x1, y1, x2, y2):
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
    
    def rotation_repere(self, angle, dico_fuv_tr_adj):
        #on fait un nouveau dico, tjrs sur le meme model et en co cartésienne
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

    def xy_cartesien(self, dist_min, dico_fuv_tr_rot, xy_noeud):
        #on fait un nouveau dico, tjrs sur le meme model et en co cartésienne
        # mais cette fois ci l'echelle change pour que les co correspondent avec l'affichage dans le canvas
        dico_fuv_tr_carte = {"precedent":{},"suivant":{},"adjacents":{}}
        for categorie in dico_fuv_tr_rot:
            for troncon in dico_fuv_tr_rot[categorie]:
                for co_xy in dico_fuv_tr_rot[categorie][troncon]:
                    x_carte = (co_xy[0] - xy_noeud[0] + dist_min)*self.width_canvas/(2*dist_min)
                    y_carte = (co_xy[1] - xy_noeud[1] + dist_min)*self.height_canvas/(2*dist_min)
                    if troncon not in dico_fuv_tr_carte[categorie].keys():
                        dico_fuv_tr_carte[categorie][troncon] = [[x_carte, y_carte]]
                    else:
                        dico_fuv_tr_carte[categorie][troncon].append([x_carte, y_carte])
        return dico_fuv_tr_carte
    
    def calcul_norme_min(self, dico_fuv_tr_rot):
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
    
    def calcul_dist_min(self, dico_fuv_tr_adj):
        #Determination de l'extrémité d'un segment adjacent la plus proche du noeud
        # selon la norme 2 (cf. cours de maths)
        # permet de prevoir la vision qu'on aura et les points gps qui seront ou non surement dans la fenetre
        dist_min = math.inf
        for categorie in dico_fuv_tr_adj:
            for troncon in dico_fuv_tr_adj[categorie]:
                dist = self.distance(dico_fuv_tr_adj[categorie][troncon], 0, -1)
                if dist < dist_min and dist != 0 :
                    dist_min = dist
        return dist_min
    
    def distance(self, co_gps, index1, index2):
        # distance selon la norme 2 entre 2 points definis par leur index dans une liste de coordonnees
        return math.sqrt((co_gps[index2][0]-co_gps[index1][0])**2+(co_gps[index2][1]-co_gps[index1][1])**2)
        

if __name__ == "__main__":
    root = MainWindow()
    #on lance le chargement de donnees juste apres que l'affichage de la premiere fenetre se soit fait
    root.root.after(100,root.load_all_datas) 
    root.loop()