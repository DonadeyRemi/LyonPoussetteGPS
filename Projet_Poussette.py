#!/usr/bin/python
# -*- encoding: utf8 -*-

import tkinter as tk
import math
import time
from tkinter import ttk
from tkinter.ttk import Separator
from tkinter import messagebox
from tkscrolledframe import ScrolledFrame
import Load_Files

import tkintermapview

class MainWindow():
    """Classe associée à l'interface graphique
    """
    def __init__(self) :
        """Constructeur de la classe
        """
        ########################### Fenetre principale #########################
        # on initialise d'abord la fenetre principale sur un affichage de chargement, le temps que les donnees se chargent
        self.root = tk.Tk()
        self.initWidget_load()
        # la fonction load_all_datas est lancée au bout de 100ms après le démarage (cf. ligne 679 (plus à jour))
        self.fen_trajet = []
        self.itineraire = []
        self.depart = [None,None]
        self.arrivee = [None,None]
        self.dist_trajet = 0
        self.saisie_user_start = ""
        self.saisie_user_end = ""
        self.start_select_state = False
        self.end_select_state = False
        ############################ Fenetre trajet ##########################
        self.toplevel_parcour = None
        self.etape = 0
        self.liste_echelles = [0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000]
        self.maker_noeud = None
        self.timer_id = None

    ########################### Fenetre principale #########################
    def initWidget_load(self):
        """Initialise les différents widgets, la taille et le titre de la fenêtre de chargement
        """
        
        self.root.geometry("300x200")
        self.loading_label_1 = tk.Label(self.root, text = "Chargement des données", font = "Calibri 16")
        self.loading_label_1.pack()
        self.loading_label_2 = tk.Label(self.root, text = "Veuillez patienter", font = "Calibri 13")
        self.loading_label_2.pack()
        self.progress_bar = ttk.Progressbar(self.root, orient = tk.HORIZONTAL, length = 100, value=2, mode = 'determinate')
        self.progress_bar.pack()
        self.root.title("Lyonyroule")

    def initWidget_main(self):
        """Intialise les widgets des différentes frames de l'interface graphique,
        même celles qui seront affichées après (par un evénement utilisateur)
        """
        self.loading_label_1.destroy()
        self.loading_label_2.destroy()
        self.progress_bar.destroy()
        self.root.geometry("1200x600")
        
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

        self.liste_depart = []
        self.var_entry_start = tk.StringVar(value = "Départ")
        self.start_selection = ttk.Combobox(self.frame_dest, textvariable=self.var_entry_start, values = self.liste_depart, width = 80, foreground = "black")
        self.start_selection.bind("<KeyRelease>",self.get_entry_start)
        self.start_selection.bind("<Button-1>",self.effacer_start)
        self.start_selection.bind("<KeyRelease-Return>", self.down_start)
        self.start_selection.bind("<<ComboboxSelected>>", self.choose_start)
        self.start_selection.bind("<FocusOut>",self.ecrire_start)
        self.start_selection.pack(side=tk.TOP, anchor = tk.N, fill=tk.X)
        
        self.liste_arrivee = []
        self.var_entry_end = tk.StringVar(value = "Arrivée")
        self.end_selection = ttk.Combobox(self.frame_dest, textvariable=self.var_entry_end, values = self.liste_arrivee , foreground = "black")
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

        self.choice_vehicule = tk.IntVar()
        self.check_button_poussette = tk.Radiobutton(self.frame_opt,
                                                             bg = 'gray', fg = 'black', anchor = 'w',
                                                             text = "  Poussette/Fauteil",
                                                             value=0,
                                                             variable = self.choice_vehicule,command = self.recup_fuv_troncon) 
        self.check_button_poussette.pack(side=tk.TOP,fill=tk.X)

        self.check_button_bike = tk.Radiobutton(self.frame_opt,
                                                bg='gray', fg = 'black', anchor = 'w',
                                                text = "          Vélo", value=1, variable = self.choice_vehicule,command = self.recup_fuv_troncon)
        self.check_button_bike.pack(side=tk.TOP,fill=tk.X)

        self.check_button_voiture = tk.Radiobutton(self.frame_opt,
                                                   bg = 'gray',fg = 'black', text = "        Voiture",
                                                   anchor = 'w',
                                                   value=2, variable = self.choice_vehicule,command = self.recup_fuv_troncon)
        self.check_button_voiture.pack(side=tk.TOP,fill=tk.X)

        self.check_button_foot = tk.Radiobutton(self.frame_opt,
                                                bg='gray', fg = 'black', anchor = 'w',
                                                text="          Pied", value=3, variable = self.choice_vehicule,command = self.recup_fuv_troncon)
        self.check_button_foot.pack(side=tk.TOP,fill=tk.X)

        self.frame_opt.pack(side=tk.TOP,fill=tk.X)

        self.button_research = tk.Button(self.frame_princ,text="Lancer la recherche",bg='gray',fg='black',relief='flat')
        self.button_research.pack(side=tk.BOTTOM,fill=tk.X)
        self.button_research.bind('<Button-1>',self.start_research)

        separator_bt = Separator(self.frame_princ,orient=tk.HORIZONTAL)
        separator_bt.pack(side=tk.TOP,fill=tk.X)

        self.frame_princ.pack(fill=tk.Y)

        #frame qui contient les widgets en mode trajet
        self.frame_trajet = tk.Frame(self.root)

        self.var_prop_trajet = tk.StringVar(value=f"Votre Trajet\n {self.var_entry_start.get()} \n vers \n {self.var_entry_end.get()}")
        self.label_trajet_prop = tk.Label(self.frame_trajet,textvariable=self.var_prop_trajet,padx=5,pady=5)
        self.label_trajet_prop.pack(side=tk.TOP,fill=tk.X)

        self.button_change_iti = tk.Button(self.frame_trajet,text="Modifier votre itineraire",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_change_iti.pack(side=tk.TOP,fill=tk.X)
        self.button_change_iti.bind("<Button-1>",self.bouton_change_iti)
        
        self.button_start_iti = tk.Button(self.frame_trajet,text="Commencer votre itinéraire",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_start_iti.pack(side=tk.TOP,fill=tk.X)
        self.button_start_iti.bind("<Button-1>",self.open_window_trajet)
        
        self.button_automatique = tk.Button(self.frame_trajet, text="Lecture automatique",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_automatique.pack(side=tk.TOP,fill=tk.X)
        self.button_automatique.bind("<Button-1>",self.lancement_auto)

        self.vitesse = tk.DoubleVar()
        self.scale_vitesse = tk.Scale(self.frame_trajet, orient='horizontal', from_= 10, to=100, showvalue = 0, resolution=2, tickinterval=10, length=200, variable = self.vitesse, font=("Calibri", 8), label = "Vitesse lecture auto (%)", command = self.maj_auto)
        self.scale_vitesse.pack(side=tk.TOP,fill=tk.X)
        
        #sous-frame qui contient les widgets des étapes du trajet
        self.frame_detail_etapes = ScrolledFrame(self.root, width = 150)
        self.frame_detail_etapes.pack()
        self.frame_detail_etapes.bind_scroll_wheel(self.root)
        
        self.inner_frame_etapes = self.frame_detail_etapes.display_widget(tk.Frame)
        self.label_detail_etapes = tk.Label(self.inner_frame_etapes, anchor="center", justify="center", text="Détail de l'itinéraire :\n")
        self.label_detail_etapes.pack(side=tk.TOP, fill = tk.X)  

        self.frame_trajet.pack_forget()
        self.frame_detail_etapes.pack_forget()

    def loop(self):
        """Boucle principale de l'application
        """
        self.root.mainloop()
        
    def load_all_datas(self):
        """Effectue le chargement des données, met à jour la barre de chargement
        puis appelle l'affichage principal
        (fonction déclenchée après l'affichage de la fenêtre de chargement)
        """
        self.dico_noeuds, self.dico_rues = Load_Files.charger_donnees_troncon()
        self.progress_bar['value'] = 19
        self.root.update_idletasks()
        self.dico_noeuds, self.dico_rues = Load_Files.charger_donnees_chausses(self.dico_noeuds, self.dico_rues)
        self.progress_bar['value'] = 37
        self.root.update_idletasks()
        self.dico_noeuds = Load_Files.correction_dico_noeuds(self.dico_noeuds)
        self.progress_bar['value'] = 44
        self.root.update_idletasks()
        self.carrefour_adjacences = Load_Files.charger_donnees_adj(self.dico_noeuds)
        self.progress_bar['value'] = 51
        self.root.update_idletasks()
        self.carrefour_adjacences_poussette = Load_Files.charger_donnees_adj_poussette(self.dico_noeuds,self.dico_rues)
        self.progress_bar['value'] = 58
        self.root.update_idletasks()
        self.carrefour_adjacences_velo = Load_Files.charger_donnees_adj_velo(self.dico_noeuds,self.dico_rues)
        self.progress_bar['value'] = 65
        self.root.update_idletasks()
        self.carrefour_adjacences_voiture = Load_Files.charger_donnees_adj_voiture(self.dico_noeuds,self.dico_rues)
        self.progress_bar['value'] = 73
        self.root.update_idletasks()
        self.carrefour_adjacences_pied = Load_Files.charger_donnees_adj_pied(self.dico_noeuds,self.dico_rues)
        self.progress_bar['value'] = 80
        self.root.update_idletasks()
        self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes = Load_Files.charger_donnees_adresses()
        self.progress_bar['value'] = 96
        self.root.update_idletasks()
        self.dico_adresses_communes = Load_Files.charger_donnees_centre(self.dico_adresses_communes)
        self.progress_bar['value'] = 100
        self.root.update_idletasks()
        #une fois le chargement de donnees effectue, on met a jour l'affichage pour afficher le menu d'acceuil
        self.root.after(500,self.initWidget_main) 

    def get_entry_start(self, event):
        """Fonction callback sur le champs d'entrée associé à l'adresse de départ
        (fonction déclenchée avec n'importe quelle touche du clavier dans la combobox de départ)
        Découpe la saisie en éléments d'adresse (numéro, rue, ...), identifie une liste d'adresses correspondantes,
        et met à jour les propositions de la combobox avec cette liste

        Args:
            event (tk event): l'evenement utilisateur
        """
        if event.widget.get() != self.saisie_user_start and event.widget.get() != "":
            self.saisie_user_start = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = Load_Files.gestion_saisie(self.saisie_user_start, list(self.dico_adresses_communes.keys()))
            self.liste_depart = Load_Files.give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.start_selection.configure(values = self.liste_depart)
        self.start_selection.configure(foreground = "red")
        self.start_select_state = False
        self.depart = [None,None]
        # si il y a une seule proposition => descendre la liste combobox
        if len(self.liste_depart) == 1 and len(event.widget.get()) > 1:
            self.start_selection.event_generate('<Down>',when="tail")
    
    def down_start(self, event):
        """Fonction callback sur le champs d'entrée associé à l'adresse de départ
        (fonction déclenchée avec la touche Return du clavier dans la combobox de départ)
        Met à jour la liste de propositions de la combobox de la même façon que get_entry_start(self, event)
        et descend la liste de la combobox

        Args:
            event (tk event): l'evenement utilisateur
        """
        if event.widget.get() != self.saisie_user_start and event.widget.get() != "":
            self.saisie_user_start = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = Load_Files.gestion_saisie(self.saisie_user_start, list(self.dico_adresses_communes.keys()))
            self.liste_depart = Load_Files.give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.start_selection.configure(values = self.liste_depart)
        self.start_selection.event_generate('<Down>',when="tail")
     
    def choose_start(self, event):
        """Fonction callback sur le champs d'entrée associé à l'adresse de départ
        (fonction déclenchée par la selection d'une proposition dans la liste de la combobox de départ)
        Redécoupe la valeur du champs de la combobox en éléments d'adresse (numéro, rue, ...)
        et identifie l'adresse correspondante pour trouver ses coordonnées GPS
        puis appelle l'identification du tuple (code_fuv,code_troncon) avec ces coordonnées GPS

        Args:
            event (tk event): evenement utilisateur
        """
        self.start_selection.configure(foreground = "green")
        self.start_select_state = True
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
            if len(choix) == 1:
                choix.pop(-1)
                commune = ""
                for i in range(len(choix)):
                    commune += choix[i]
                    if i < len(choix)-1:
                            commune += " "
                co_gps = self.dico_adresses_communes[commune]["centre"]["0"]
            else : 
                commune = saisie[1]
                numero = choix.pop(0)
                rue = ""
                for i in range(len(choix)):
                    rue += choix[i]
                    if i < len(choix)-1:
                            rue += " "
                co_gps = self.dico_adresses_num[numero][rue][commune]
        self.depart = co_gps

        self.root.after(100, self.recup_fuv_troncon)

    def effacer_start(self,event):
        """Fonction callback sur le champs d'entrée associé à l'adresse de départ
        (fonction déclenchée par le clic du bouton gauche sur la combobox de départ)
        Efface le texte indicatif "Départ" pour permettre la saisie de l'utilisateur

        Args:
            event (tk event): evenement utilisateur
        """
        if self.start_selection.get() == "Départ":
            self.start_selection.set("")
            
    def ecrire_start(self,event):
        """Fonction callback sur le champs d'entrée associé à l'adresse de départ
        (fonction déclenchée par la sortie du "focus" de la combobox de départ)
        Remet le texte indicatif "Départ" en l'absence de saisie utilisateur

        Args:
            event (tk event): evenement utilisateur
        """
        saisie = self.start_selection.get()
        saisie = saisie.strip(" ")
        if saisie == "":
            self.start_selection.set("Départ")
            self.start_selection.configure(foreground = "black")
            self.start_select_state = False
            
    def get_entry_end(self, event):
        """Fonction callback sur le champs d'entrée associé à l'adresse d'arrivée
        (fonction déclenchée avec n'importe quelle touche du clavier dans la combobox d'arrivée')
        Découpe la saisie en éléments d'adresse (numéro, rue, ...), identifie une liste d'adresses correspondantes,
        et met à jour les propositions de la combobox avec cette liste
        
        Args:
            event (tk event): l'evenement utilisateur
        """
        if event.widget.get() != self.saisie_user_end and event.widget.get() != "":
            self.saisie_user_end = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = Load_Files.gestion_saisie(self.saisie_user_end, list(self.dico_adresses_communes.keys()))
            self.liste_arrivee = Load_Files.give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.end_selection.configure(values = self.liste_arrivee)
        self.end_selection.configure(foreground = "red")
        self.end_select_state = False
        self.arrivee = [None,None]
        if len(self.liste_arrivee) == 1 and len(event.widget.get()) > 1:
            self.end_selection.event_generate('<Down>',when="tail")
    
    def down_end(self, event):
        """Fonction callback sur le champs d'entrée associé à l'adresse d'arrivée
        (fonction déclenchée avec la touche Return du clavier dans la combobox de d'arrivée)
        Met à jour la liste de propositions de la combobox de la même façon que get_entry_end(self, event)
        et descend la liste de la combobox
        
        Args:
            event (tk event): l'evenement utilisateur
        """
        if event.widget.get() != self.saisie_user_end and event.widget.get() != "":
            self.saisie_user_end = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = Load_Files.gestion_saisie(self.saisie_user_end, list(self.dico_adresses_communes.keys()))
            self.liste_arrivee = Load_Files.give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.end_selection.configure(values = self.liste_arrivee)
        self.end_selection.event_generate('<Down>',when="tail")
    
    def choose_end(self, event):
        """Fonction callback sur le champs d'entrée associé à l'adresse de départ
        (fonction déclenchée par la selection d'une proposition dans la liste de la combobox de départ)
        Redécoupe la valeur du champs de la combobox en éléments d'adresse (numéro, rue, ...)
        et identifie l'adresse correspondante pour trouver ses coordonnées GPS
        puis appelle l'identification du tuple (code_fuv,code_troncon) avec ces coordonnées GPS
        
        Args:
            event (tk event): evenement utilisateur
        """
        self.end_selection.configure(foreground = "green")
        self.end_select_state = True
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
        self.arrivee = co_gps

        self.root.after(100, self.recup_fuv_troncon)
    
    def effacer_end(self,event):
        """Fonction callback sur le champs d'entrée associé à l'adresse d'arrivée
        (fonction déclenchée par le clic du bouton gauche sur la combobox d'arrivée)
        Efface le texte indicatif "Arrivée" pour permettre la saisie de l'utilisateur
        
        Args:
            event (tk event): evenement utilisateur
        """
        if self.end_selection.get() == "Arrivée":
            self.end_selection.set("")
            
    def ecrire_end(self,event):
        """Fonction callback sur le champs d'entrée associé à l'adresse d'arrivée
        (fonction déclenchée par la sortie du "focus" de la combobox d'arrivée)
        Remet le texte indicatif "Arrivée" en l'absence de saisie utilisateur
        
        Args:
            event (tk event): evenement utilisateur
        """
        saisie = self.end_selection.get()
        saisie = saisie.strip(" ")
        if saisie == "":
            self.end_selection.set("Arrivée")
            self.end_selection.configure(foreground = "black")
            self.end_select_state = False

    def recup_fuv_troncon(self):
        """Identifie en fonction des coordonnées GPS le tuple (code_fuv,code_troncon) de départ et celui d'arrivée
        Ces tuples indentifient les troncons de manière unique
        """
        if self.start_select_state and self.end_select_state :
            self.depart_fuv, self.arrivee_fuv = Load_Files.give_troncon_nearest_gps(self.depart, self.arrivee, self.dico_rues, self.choice_vehicule.get())

    def start_research(self,event):
        """Fonction callback du bouton de calcul de l'itinéraire
        Lance la recherche de l'itinéraire en fonction du mode de recherche choisi par l'utilisateur
        et génère le changement de frame, le calcul et l'affichage des étapes,
        et l'affichage de l'itinéraire sur la carte si un trajet est trouvé
        Retourne à l'utilisateur un message d'erreur sinon
        
        Args:
            event (tk event): evenement utilisateur
        """
        crit_sens = False
        crit_vitesse = False
        if self.choice_vehicule.get() == 1 :
            #user a choisi velo
            self.carrefour_adjacences_choix = self.carrefour_adjacences_velo
            crit_sens = True

        elif self.choice_vehicule.get() == 2 :
            #user a choisi voiture
            self.carrefour_adjacences_choix = self.carrefour_adjacences_voiture
            crit_sens = True
            crit_vitesse = True

        elif self.choice_vehicule.get() == 3 :
            #user a choisi a pied
            self.carrefour_adjacences_choix = self.carrefour_adjacences_pied

        else :
            #l'utilisateur choisi poussette fauteil
            self.carrefour_adjacences_choix = self.carrefour_adjacences_poussette

        if self.depart_fuv != (None,None) and self.arrivee_fuv != (None,None) and self.depart_fuv != self.arrivee_fuv:
            self.itineraire, self.dist_trajet = Load_Files.a_star(self.depart_fuv,self.arrivee_fuv,self.carrefour_adjacences_choix, self.dico_rues, crit_sens, crit_vitesse)
            if len(self.itineraire) > 1:
                print(self.dico_rues[self.itineraire[0][0]][self.itineraire[0][1]]['GPS'])
                #on cache la frame principale et affiche la frame itineraire
                self.frame_princ.pack_forget()
                self.var_prop_trajet.set(f"Votre Trajet\n {self.var_entry_start.get()} \n vers \n {self.var_entry_end.get()}")
                self.frame_trajet.pack(fill=tk.Y)
                self.frame_detail_etapes.pack(fill=tk.BOTH)
                # on appelle la fonction qui affiche la carte principale
                self.show_large_map()
                self.l_button_etape = []
                for i in range(len(self.itineraire)-1):
                    text_detail_etapes = str(i+1) + " : " + Load_Files.consigne_noeud(self.itineraire[i], self.itineraire[i+1], self.dico_rues, self.carrefour_adjacences_choix)
                    button_etape = tk.Button(self.inner_frame_etapes,text=text_detail_etapes,bg='gray',fg='black', command = lambda idx=i: self.open_window_trajet_middle(idx))
                    button_etape.pack(side = tk.TOP, fill = tk.X)
                    self.l_button_etape.append(button_etape)
            else :
                messagebox.showinfo("Itinéraire Non trouvé", "Aucun itinéraires n'existent avec les paramètres selectionnés.")
        else :
            messagebox.showinfo("Itinéraire incomplet", "Adresse(s) de départ et/ou d'arrivée non renseignée(s) ou non reconnue(s). \nVeuillez compléter les champs manquants.")
    
    def show_large_map(self):
        """Affiche le trajet à affectuer et les marqueurs de départ et d'arrivée sur l'interface graphique
        """
        co_trajet = []
        for fuv_rue in self.itineraire :
            co_gps_liste = self.dico_rues[fuv_rue[0]][fuv_rue[1]]['GPS']
            if len(co_trajet) != 0 :
                if (co_gps_liste[-1][1],co_gps_liste[-1][0]) == co_trajet[-1]:
                    co_gps_liste.reverse()
                for co_gps in co_gps_liste :
                        co_trajet.append((co_gps[1],co_gps[0]))
            else :
                fuv_rue_suiv = self.itineraire[1]
                co_gps_liste_suiv = self.dico_rues[fuv_rue_suiv[0]][fuv_rue_suiv[1]]['GPS']
                if co_gps_liste[0] == co_gps_liste_suiv[0] or co_gps_liste[0] == co_gps_liste_suiv[-1]:
                    co_gps_liste.reverse()
                for co_gps in co_gps_liste :
                    co_trajet.append((co_gps[1],co_gps[0]))
        #ajout d'un marker au debut et fin
        self.map_widget.set_marker(co_trajet[0][0],co_trajet[0][1],text="Départ")
        self.map_widget.set_marker(co_trajet[-1][0],co_trajet[-1][1],text="Arrivée")
        self.map_widget.set_marker(self.depart[-1],self.depart[0],text="Adresse\nDépart")
        self.map_widget.set_marker(self.arrivee[-1],self.arrivee[0],text="Adresse\nArrivée")
        self.map_widget.set_path(co_trajet)

    def bouton_change_iti(self,event):
        """Fonction callback du bouton de changement d'itinéraire
        Demande confirmation à l'utilisateur et repasse à la frame d'acceuil dans le cas positif
        Supprime aussi dans ce cas les éléments associé au trajet en cours (tracé sur la carte, fenêtre trajet, ...)

        Args:
            event (tk event): l'evenement utilisateur
        """
        msg_user = messagebox.askyesno("Changer d'itineraire ?","Voulez vous vraiment changer d'itinéraire ?\n Celui-ci sera perdu")
        if msg_user == True :
            # on ferme la fenetre trajet si elle est ouverte
            if (self.toplevel_parcour != None) :
                self.toplevel_parcour.destroy()
                if self.button_automatique.config('bg')[-1] == 'green':
                    self.button_automatique.config(bg='gray')
                    self.root.after_cancel(self.timer_id)
            for button in self.l_button_etape:
                button.destroy()
            #Affiche de nouveau le frame principal
            self.frame_trajet.pack_forget()
            self.frame_detail_etapes.pack_forget()
            self.frame_princ.pack(fill=tk.Y)
            # on enleve le trajet actuel
            self.map_widget.delete_all_path()
            self.map_widget.delete_all_marker()
            self.map_widget.set_position(45.76177569754233, 4.8358160526802685)  #on centre sur Lyon
            self.map_widget.set_zoom(11)
        
    def open_window_trajet(self,event):
        """Fonction callback du bouton commencer le trajet
        Ouvre la fenetre trajet qui affiche l'itinéraire carrefour par carrefour
        Affiche le premier carrefour
        
        Args:
            event (tk event): l'evenement utilisateur 
        """
        self.etape = 0
        if (self.toplevel_parcour != None) :
            self.toplevel_parcour.destroy()
            if self.button_automatique.config('bg')[-1] == 'green':
                self.button_automatique.config(bg='gray')
                self.root.after_cancel(self.timer_id)
        self.toplevel_parcour = tk.Toplevel(self.root)
        self.init_widget_parcour()
        self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])
        
    def open_window_trajet_middle(self, idx):
        """Fonction pseudo-callback des boutons étapes de l'itinéraire
        Ouvre la fenetre trajet qui affiche l'itinéraire carrefour par carrefour
        Affiche le carrefour rattaché au bouton cliqué
        
        Args:
            idx (int): numéro de l'étape associé au bouton
        """
        self.etape = idx
        if (self.toplevel_parcour != None) :
            self.toplevel_parcour.destroy()
            if self.button_automatique.config('bg')[-1] == 'green':
                self.button_automatique.config(bg='gray')
                self.root.after_cancel(self.timer_id)
        self.toplevel_parcour = tk.Toplevel(self.root)
        self.init_widget_parcour()
        self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])
        
    def lancement_auto(self, event):
        """Fonction callback du bouton de lecture automatique
        Déclenche le défilement automatique des étapes du parcours (carrefours successifs) sur la fenêtre trajet

        Args:
            event (tk event): evenement utilisateur
        """
        if (self.toplevel_parcour != None) :
            self.toplevel_parcour.focus_set()
        if self.button_automatique.config('bg')[-1] == 'gray':
            self.button_automatique.config(bg='green')
            if (self.toplevel_parcour == None) :
                self.etape = 0
                self.toplevel_parcour = tk.Toplevel(self.root)
                self.init_widget_parcour()
                self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])
                self.temps_pause = int(1000/(self.vitesse.get()/100))
                self.time_mem = int(time.time()*1000)
                self.timer_id = self.root.after(self.temps_pause, self.automatique)
            else :
                self.timer_id = self.root.after(10, self.automatique)

        else:
            self.button_automatique.config(bg='gray')
            self.root.after_cancel(self.timer_id)


    def maj_auto(self, val_vitesse):
        """Fonction pseudo-callback du slider de selection de la vitesse de lecture
        Calcul le délai écoulé depuis l'affichage automatique de la dernière étape
        et passe à l'étape suivante si ce delai est plus long que celui lié à la nouvelle vitesse selectionnée par le slider

        Args:
            val_vitesse (float): valeur de la vitesse de lecture définie par l'utilisateur sur le slidder
        """
        if (self.toplevel_parcour != None) :
            self.toplevel_parcour.focus_set()
        if self.button_automatique.config('bg')[-1] == 'green':
            time_now = int(time.time()*1000)
            delai = time_now-self.time_mem
            self.temps_pause = int(1000/(int(val_vitesse)/100))
            if delai < self.temps_pause:
                self.root.after_cancel(self.timer_id)
                self.timer_id = self.root.after((self.temps_pause - delai), self.automatique)            
            else:
                self.root.after_cancel(self.timer_id)
                self.timer_id = self.root.after(10, self.automatique)

    def automatique(self):
        """Gère le défilement automatique des étapes du parcours (carrefours successifs) sur la fenêtre trajet
        Efface le carrefour dessiné et retrace automatiquement le carrefour suivant sur la fenêtre trajet
        puis s'appelle de nouveau après un delai lié à la vitesse définie par le slider
        """
        if self.etape + 2 < len(self.itineraire):
            self.etape += 1
            self.temps_pause = int(1000/(self.vitesse.get()/100))

            self.main_canvas.delete(self.ligne_suiv)
            self.main_canvas.delete(self.ligne_pre)
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
            self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])
            self.time_mem = int(time.time()*1000)
            self.root.after_cancel(self.timer_id)
            self.timer_id = self.root.after(self.temps_pause, self.automatique)
        else:
            self.root.after_cancel(self.timer_id)
            self.button_automatique.config(bg='gray')   

    ############################ Fenetre trajet ##########################

    def init_widget_parcour(self):
        """Intialise les widgets de la fenêtre trajet (affichage graphique)
        """

        self.toplevel_parcour.resizable(height = False, width = False) 
        self.toplevel_parcour.title = "Trajet"
        
        self.f_par_width = 400
        self.f_par_height = 500
        self.toplevel_parcour.geometry(f"{self.f_par_width}x{self.f_par_height}")
        
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
        """Fonction callback du bouton précédent
        Efface le carrefour dessiné et retrace le carrefour précédent sur la fenêtre trajet

        Args:
            event (tk event): evenement utilisateur
        """
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
        """Fonction callback du bouton suivant
        Efface le carrefour dessiné et retrace le carrefour suivant sur la fenêtre trajet
        et ferme la fenêtre trajet si on est au dela de la dernière étape

        Args:
            event (tk event): evenement utilisateur
        """
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
            self.maker_noeud.delete()
            if self.button_automatique.config('bg')[-1] == 'green':
                self.button_automatique.config(bg='gray')
                self.root.after_cancel(self.timer_id)

    def show_iti(self, fuv_tr_pre, fuv_tr_suiv):
        """Affiche dans la fenêtre trajet, l'itineraire à suivre au carrefour renseigné
        et centre l'affichage de la carte de la fenêtre principale sur ce carrefour

        Args:
            fuv_tr_pre (tuple): identifiant (fuv,troncon) du troncon précedent
            fuv_tr_suiv (tuple): identifiant (fuv,troncon) du troncon suivant
        """
        if self.maker_noeud != None : 
            self.maker_noeud.delete()
        #Recherche des segments adjacents, compilation de leurs co GPS dans un dictionnaire
        #puis passage en co cartesienne
        dico_fuv_tr_adj, lat_noeud, long_noeud = Load_Files.compute_cross(fuv_tr_pre, fuv_tr_suiv, self.dico_rues, self.carrefour_adjacences)
        #calcul des points qui seront visible et qu'il faut donc prendreen compte pour l'orientation 
        dist_min = Load_Files.calcul_dist_min(dico_fuv_tr_adj)
        i = 1
        while i < len(dico_fuv_tr_adj["precedent"][fuv_tr_pre]) - 1 and Load_Files.distance(dico_fuv_tr_adj["precedent"][fuv_tr_pre], 0, i) < dist_min:
            i += 1
        #Calcul de l'angle entre le segment precedent (premier et dernier point GPS)
        # et l'horizontale (axe x)
        x_noeud = dico_fuv_tr_adj["precedent"][fuv_tr_pre][0][0]
        y_noeud = dico_fuv_tr_adj["precedent"][fuv_tr_pre][0][1]
        x_precedent = dico_fuv_tr_adj["precedent"][fuv_tr_pre][i][0]
        y_precedent = dico_fuv_tr_adj["precedent"][fuv_tr_pre][i][1]
        alpha_pre = Load_Files.calcul_angle(x_noeud, y_noeud, x_precedent, y_precedent)
        #Rotation du repere pour avoir le segment precedent en bas de l'ecran, vertical
        dico_fuv_tr_rot = Load_Files.rotation_repere(alpha_pre, dico_fuv_tr_adj)
        #Determination de l'extrémité d'un segment adjacent la plus proche du noeud
        # selon la norme infini (cf. cours de maths)
        # permet d'avoir la vision la plus large possible sans voir d'autres noeuds
        norme_min = Load_Files.calcul_norme_min(dico_fuv_tr_rot)
        xy_noeud = dico_fuv_tr_rot["precedent"][fuv_tr_pre][0]
        #Mise à l'echelle des co en fonction de la distance min
        dico_fuv_tr_carte = Load_Files.xy_cartesien(norme_min, dico_fuv_tr_rot, xy_noeud, self.width_canvas, self.height_canvas)
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
        text_instruction = Load_Files.instructions(dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv, self.dico_rues)
        self.label_instruction.configure(text = str(self.etape + 1) + " : " + text_instruction)
        
        # mettre la position du carrefour actuel
        self.maker_noeud = self.map_widget.set_marker(lat_noeud,long_noeud,"Actuel")
        self.map_widget.set_position(lat_noeud,long_noeud)
        self.map_widget.set_zoom(17)
        
    def dessine_noeud(self, dico_fuv_tr_carte, fuv_tr_pre, fuv_tr_suiv, co_nord, cote_echelle, echelle_choisie):
        """Dessine l'intersection renseignée avec la route à suivre, les indications, une boussole et une echelle

        Args:
            dico_fuv_tr_carte (dict): le dictionnaire des code (fuv,troncon) avec leurs coordonnées mises dans le bon sens et dans le bon repère pour le dessin
            fuv_tr_pre (tuple): identifiant (fuv,troncon) du troncon precedent
            fuv_tr_suiv (tuple): identifiant (fuv,troncon) du troncon suivant
            co_nord (list): les coordonnées cartesienne (dans le bon sens et repère) de la direction du nord pour tracer la bousole
            cote_echelle (float): valeur permettant le tracé de la barre d'échelle, à la bonne échelle
            echelle_choisie (float): valeur de l'échelle à afficher
        """
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
