#!/usr/bin/python
# -*- encoding: utf8 -*-

import tkinter as tk
import math
from tkinter import ttk
from tkinter.ttk import Separator
from tkinter import messagebox
from tkscrolledframe import ScrolledFrame
import Load_Files

import tkintermapview

class MainWindow():
    def __init__(self) :
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
        ############################ Fenetre trajet ##########################
        self.toplevel_parcour = None
        self.etape = 0
        self.liste_echelles = [0.3, 1, 3, 10, 30, 100, 300, 1000, 3000, 10000]
        self.maker_noeud = None
        ########################## Fenetre parametres #########################
        self.toplevel_params = None

    ########################### Fenetre principale #########################
    def initWidget_load(self):
        
        self.root.geometry("300x200")
        self.loading_label_1 = tk.Label(self.root, text = "Chargement des données", font = "Calibri 16")
        self.loading_label_1.pack()
        self.loading_label_2 = tk.Label(self.root, text = "Veuillez patienter", font = "Calibri 13")
        self.loading_label_2.pack()
        self.progress_bar = ttk.Progressbar(self.root, orient = tk.HORIZONTAL, length = 100, mode = 'determinate')
        self.progress_bar.pack()
        self.root.title("Lyonyroule")

    def initWidget_main(self):
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

        self.choice_transport = tk.IntVar()
        self.check_button_poussette = tk.Radiobutton(self.frame_opt,
                                                             bg = 'gray', fg = 'black', anchor = 'w',
                                                             text = "  Poussette/Fauteil",
                                                             value=0,
                                                             variable = self.choice_transport) 
        self.check_button_poussette.pack(side=tk.TOP,fill=tk.X)

        self.check_button_bike = tk.Radiobutton(self.frame_opt,
                                                bg='gray', fg = 'black', anchor = 'w',
                                                text = "          Vélo", value=1 , variable = self.choice_transport)
        self.check_button_bike.pack(side=tk.TOP,fill=tk.X)

        self.check_button_voiture = tk.Radiobutton(self.frame_opt,
                                                   bg = 'gray',fg = 'black', text = "        Voiture",
                                                    anchor = 'w',
                                                   value=2, variable = self.choice_transport)
        self.check_button_voiture.pack(side=tk.TOP,fill=tk.X)

        self.check_button_foot = tk.Radiobutton(self.frame_opt,
                                                bg='gray', fg = 'black', anchor = 'w',
                                                text="          Pied", value = 3, variable = self.choice_transport)
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

        self.var_prop_trajet = tk.StringVar(value=f"Votre Trajet\n {self.var_entry_start.get()} vers {self.var_entry_end.get()}")
        self.label_trajet_prop = tk.Label(self.frame_trajet,textvariable=self.var_prop_trajet,padx=5,pady=5)
        self.label_trajet_prop.pack(side=tk.TOP,fill=tk.X)

        self.button_change_iti = tk.Button(self.frame_trajet,text="Modifier votre itineraire",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_change_iti.pack(side=tk.TOP,fill=tk.X)
        self.button_change_iti.bind("<Button-1>",self.bouton_change_iti)

        
        # self.button_stop_iti = tk.Button(self.frame_trajet,text="Arreter l'itineraire en cours",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        # self.button_stop_iti.pack(side=tk.BOTTOM,fill=tk.X)
        # self.button_stop_iti.bind("<Button-1>",self.stop_iti)
        
        self.button_start_iti = tk.Button(self.frame_trajet,text="Commencer votre itinéraire",bg='gray',fg='black',relief='flat',padx=5,pady=5)
        self.button_start_iti.pack(side=tk.BOTTOM,fill=tk.X)
        self.button_start_iti.bind("<Button-1>",self.open_window_trajet)
        
        self.frame_detail_etapes = ScrolledFrame(self.root, width = 150)
        self.frame_detail_etapes.pack()
        self.inner_frame_etapes = self.frame_detail_etapes.display_widget(tk.Frame)
        self.text_detail = tk.Label(self.inner_frame_etapes, anchor="center", justify="center", text="Détail de l'itinéraire :\n")
        self.text_detail.pack(side=tk.TOP, fill = tk.X)    

        self.frame_trajet.pack_forget()
        self.frame_detail_etapes.pack_forget()

    def loop(self):
        self.root.mainloop()

    def get_entry_start(self, event):
        if event.widget.get() != self.saisie_user_start and event.widget.get() != "":
            self.saisie_user_start = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = Load_Files.gestion_saisie(self.saisie_user_start, list(self.dico_adresses_communes.keys()))
            self.liste_depart = Load_Files.give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.start_selection.configure(values = self.liste_depart)
        self.start_selection.configure(foreground = "red")
        self.depart = [None,None]
        if len(self.liste_depart) == 1 and len(event.widget.get()) > 1:
            self.start_selection.event_generate('<Down>',when="tail")
    
    def down_start(self, event):
        if event.widget.get() != self.saisie_user_start and event.widget.get() != "":
            self.saisie_user_start = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = Load_Files.gestion_saisie(self.saisie_user_start, list(self.dico_adresses_communes.keys()))
            self.liste_depart = Load_Files.give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
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
            numero, rue, commune, com_possibles, latitude, longitude = Load_Files.gestion_saisie(self.saisie_user_end, list(self.dico_adresses_communes.keys()))
            self.liste_arrivee = Load_Files.give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
            self.end_selection.configure(values = self.liste_arrivee)
        self.end_selection.configure(foreground = "red")
        self.arrivee = [None,None]
        if len(self.liste_arrivee) == 1 and len(event.widget.get()) > 1:
            self.end_selection.event_generate('<Down>',when="tail")
    
    def down_end(self, event):
        if event.widget.get() != self.saisie_user_end and event.widget.get() != "":
            self.saisie_user_end = event.widget.get()
            numero, rue, commune, com_possibles, latitude, longitude = Load_Files.gestion_saisie(self.saisie_user_end, list(self.dico_adresses_communes.keys()))
            self.liste_arrivee = Load_Files.give_troncon_address(numero, rue, commune, com_possibles, latitude, longitude, self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes)
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
        self.arrivee = co_gps
        
        print()
        print(f"FUV+TRONCON arrivée : {self.arrivee}")
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
        

    def start_research(self,event):
        """Fonction callback du bouton de calcul de l'itineraire, il lance la recherche de l'itineraire
        Args:
            event (dict): the tk event object return after the user event
        """
        if self.choice_transport.get() == 1 :
            #il a choisi la poussette velo
            self.depart_fuv = Load_Files.give_troncon_nearest_gps(self.depart,self.dico_rues,self.choice_transport.get())
            self.arrivee_fuv = Load_Files.give_troncon_nearest_gps(self.arrivee,self.dico_rues,self.choice_transport.get())
            if self.depart_fuv != (None,None) and self.arrivee_fuv != (None,None) and self.depart_fuv != self.arrivee_fuv:
                if (self.toplevel_params != None) :
                    self.toplevel_params.destroy()
                self.itineraire, self.dist_trajet = Load_Files.a_star(self.depart_fuv,self.arrivee_fuv,self.carrefour_adjacences_velo, self.dico_rues)
                if len(self.itineraire) > 1 :
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
                        text_detail_etapes = str(i+1) + " : " + Load_Files.consigne_noeud(self.itineraire[i], self.itineraire[i+1], self.dico_rues, self.carrefour_adjacences_velo)
                        button_etape = tk.Button(self.inner_frame_etapes,text=text_detail_etapes,bg='gray',fg='black', command = lambda idx=i: self.open_window_trajet_middle(idx))
                        button_etape.pack(side = tk.TOP, fill = tk.X)
                        self.l_button_etape.append(button_etape)

                else :
                    messagebox.showinfo("Itinéraire Non trouvé", "Aucun itinéraires n'existent avec les paramètres selectionnés.")
            else :
                messagebox.showinfo("Itinéraire incomplet", "Adresse(s) de départ et/ou d'arrivée non renseignée(s) ou non reconnue(s). \nVeuillez compléter les champs manquants.")

        elif self.choice_transport.get() == 2 :
            #il a choisi la poussette la voiture
            self.depart_fuv = Load_Files.give_troncon_nearest_gps(self.depart,self.dico_rues,self.choice_transport.get())
            self.arrivee_fuv = Load_Files.give_troncon_nearest_gps(self.arrivee,self.dico_rues,self.choice_transport.get())
            if self.depart_fuv != (None,None) and self.arrivee_fuv != (None,None) and self.depart_fuv != self.arrivee_fuv:
                if (self.toplevel_params != None) :
                    self.toplevel_params.destroy()
                self.itineraire, self.dist_trajet = Load_Files.a_star(self.depart_fuv,self.arrivee_fuv,self.carrefour_adjacences_voiture, self.dico_rues)
                if len(self.itineraire) > 1 :
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
                        text_detail_etapes = str(i+1) + " : " + Load_Files.consigne_noeud(self.itineraire[i], self.itineraire[i+1], self.dico_rues, self.carrefour_adjacences_voiture)
                        button_etape = tk.Button(self.inner_frame_etapes,text=text_detail_etapes,bg='gray',fg='black', command = lambda idx=i: self.open_window_trajet_middle(idx))
                        button_etape.pack(side = tk.TOP, fill = tk.X)
                        self.l_button_etape.append(button_etape)

                else :
                    messagebox.showinfo("Itinéraire Non trouvé", "Aucun itinéraires n'existent avec les paramètres selectionnés.")
            else :
                messagebox.showinfo("Itinéraire incomplet", "Adresse(s) de départ et/ou d'arrivée non renseignée(s) ou non reconnue(s). \nVeuillez compléter les champs manquants.")

        elif self.choice_transport.get() == 3 :
            #il a choisi la poussette le pied
            self.depart_fuv = Load_Files.give_troncon_nearest_gps(self.depart,self.dico_rues,self.choice_transport.get())
            self.arrivee_fuv = Load_Files.give_troncon_nearest_gps(self.arrivee,self.dico_rues,self.choice_transport.get())
            if self.depart_fuv != (None,None) and self.arrivee_fuv != (None,None) and self.depart_fuv != self.arrivee_fuv:
                if (self.toplevel_params != None) :
                    self.toplevel_params.destroy()
                self.itineraire, self.dist_trajet = Load_Files.a_star(self.depart_fuv,self.arrivee_fuv,self.carrefour_adjacences_pied, self.dico_rues)
                if len(self.itineraire) > 1 :
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
                        text_detail_etapes = str(i+1) + " : " + Load_Files.consigne_noeud(self.itineraire[i], self.itineraire[i+1], self.dico_rues, self.carrefour_adjacences_pied)
                        button_etape = tk.Button(self.inner_frame_etapes,text=text_detail_etapes,bg='gray',fg='black', command = lambda idx=i: self.open_window_trajet_middle(idx))
                        button_etape.pack(side = tk.TOP, fill = tk.X)
                        self.l_button_etape.append(button_etape)
                else :
                    messagebox.showinfo("Itinéraire Non trouvé", "Aucun itinéraires n'existent avec les paramètres selectionnés.")
            else :
                messagebox.showinfo("Itinéraire incomplet", "Adresse(s) de départ et/ou d'arrivée non renseignée(s) ou non reconnue(s). \nVeuillez compléter les champs manquants.")

        else :
            self.depart_fuv = Load_Files.give_troncon_nearest_gps(self.depart,self.dico_rues,self.choice_transport.get())
            self.arrivee_fuv = Load_Files.give_troncon_nearest_gps(self.arrivee,self.dico_rues,self.choice_transport.get())
            if self.depart_fuv != (None,None) and self.arrivee_fuv != (None,None) and self.depart_fuv != self.arrivee_fuv:
                if (self.toplevel_params != None) :
                    self.toplevel_params.destroy()
                self.itineraire, self.dist_trajet = Load_Files.a_star(self.depart_fuv,self.arrivee_fuv,self.carrefour_adjacences_poussette, self.dico_rues)
                if len(self.itineraire) > 1 :
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
                        text_detail_etapes = str(i+1) + " : " + Load_Files.consigne_noeud(self.itineraire[i], self.itineraire[i+1], self.dico_rues, self.carrefour_adjacences_poussette)
                        button_etape = tk.Button(self.inner_frame_etapes,text=text_detail_etapes,bg='gray',fg='black', command = lambda idx=i: self.open_window_trajet_middle(idx))
                        button_etape.pack(side = tk.TOP, fill = tk.X)
                        self.l_button_etape.append(button_etape)

                else :
                    messagebox.showinfo("Itinéraire Non trouvé", "Aucun itinéraires n'existent avec les paramètres selectionnés.")
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
            if (self.toplevel_parcour != None) :
                self.toplevel_parcour.destroy()
            #Affiche de nouveau le frame principal
            self.frame_trajet.pack_forget()
            self.frame_detail_etapes.pack_forget()
            self.frame_princ.pack(fill=tk.Y)

            # on change l'affichage sur la grande carte
            
            self.map_widget.delete_all_path()
            self.map_widget.delete_all_marker()
            self.map_widget.set_position(45.76177569754233, 4.8358160526802685)  #on centre sur Lyon
            self.map_widget.set_zoom(11)
            
        
    def open_window_trajet(self,event):
        """Fonction callback du bouton commencer le trajet, ouvre la fenetre du trajet carrefour par carrefour
        Args:
            event (dict): the tk event object return after the user event 
        """
        self.etape = 0
        if (self.toplevel_parcour != None) :
            self.toplevel_parcour.destroy()
        self.toplevel_parcour = tk.Toplevel(self.root)
        self.init_widget_parcour()
        self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])
        
    def open_window_trajet_middle(self, idx):
        """Fonction callback du bouton commencer le trajet, ouvre la fenetre du trajet carrefour par carrefour
        Args:
        event (dict): the tk event object return after the user event 
        """
        self.etape = idx
        if (self.toplevel_parcour != None) :
            self.toplevel_parcour.destroy()
        self.toplevel_parcour = tk.Toplevel(self.root)
        self.init_widget_parcour()
        self.show_iti(self.itineraire[self.etape],self.itineraire[self.etape+1])

    def load_all_datas(self):
        self.dico_noeuds, self.dico_rues = Load_Files.charger_donnees_troncon()
        self.progress_bar['value'] = 11
        self.root.update_idletasks()
        self.dico_noeuds, self.dico_rues = Load_Files.charger_donnees_chausses(self.dico_noeuds, self.dico_rues)
        self.progress_bar['value'] = 22
        self.root.update_idletasks()
        self.dico_noeuds = Load_Files.correction_dico_noeuds(self.dico_noeuds)
        self.progress_bar['value'] = 33
        self.root.update_idletasks()
        self.carrefour_adjacences_poussette = Load_Files.charger_donnees_adj_poussette(self.dico_noeuds,self.dico_rues)
        self.progress_bar['value'] = 44
        self.root.update_idletasks()
        self.carrefour_adjacences_velo = Load_Files.charger_donnees_adj_velo(self.dico_noeuds,self.dico_rues)
        self.progress_bar['value'] = 55
        self.root.update_idletasks()
        self.carrefour_adjacences_voiture = Load_Files.charger_donnees_adj_voiture(self.dico_noeuds,self.dico_rues)
        self.progress_bar['value'] = 66
        self.root.update_idletasks()
        self.carrefour_adjacences_pied = Load_Files.charger_donnees_adj_pied(self.dico_noeuds,self.dico_rues)
        self.progress_bar['value'] = 77
        self.root.update_idletasks()
        self.dico_adresses_num, self.dico_adresses_rues, self.dico_adresses_communes = Load_Files.charger_donnees_adresses()
        self.progress_bar['value'] = 88
        self.root.update_idletasks()
        self.dico_adresses_communes = Load_Files.charger_donnees_centre(self.dico_adresses_communes)
        self.progress_bar['value'] = 100
        self.root.update_idletasks()
        #une fois le chargement de donnees effectue, on met a jour l'affichage pour afficher le menu d'acceuil
        self.root.after(500,self.initWidget_main)    

    ############################ Fenetre trajet ##########################

    def init_widget_parcour(self):

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
        if self.maker_noeud != None : 
            self.maker_noeud.delete()
        if self.choice_transport.get() == 1 :
            dico_fuv_tr_adj, lat_noeud,long_noeud = Load_Files.compute_cross(fuv_tr_pre, fuv_tr_suiv, self.dico_rues, self.carrefour_adjacences_velo)
        elif self.choice_transport.get() == 2 :
            dico_fuv_tr_adj, lat_noeud,long_noeud = Load_Files.compute_cross(fuv_tr_pre, fuv_tr_suiv, self.dico_rues, self.carrefour_adjacences_voiture)
        elif self.choice_transport.get() == 3 :
            dico_fuv_tr_adj, lat_noeud,long_noeud = Load_Files.compute_cross(fuv_tr_pre, fuv_tr_suiv, self.dico_rues, self.carrefour_adjacences_pied)
        else :
            dico_fuv_tr_adj, lat_noeud,long_noeud = Load_Files.compute_cross(fuv_tr_pre, fuv_tr_suiv, self.dico_rues, self.carrefour_adjacences_velo) # valeur par defaut
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