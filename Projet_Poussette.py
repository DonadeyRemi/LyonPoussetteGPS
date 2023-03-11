import tkinter as tk
from tkinter.ttk import Separator
import Load_Files


class MainWindow():
    def __init__(self) :
        # on commence en premier par charger les donnees, ce qui peut prendre en effet un peu de temps
        self.load_all_datas()

        # on initialise alors la fenetre
        self.root = tk.Tk()
        self.root.geometry("600x600")
        self.root.title("Lyonyroule")

        self.initWidget()


    def initWidget(self):
        self.canvas = tk.Canvas(self.root,bg="gray")
        self.canvas.pack(side = tk.LEFT,fill=tk.Y)

        separator_canvas = Separator(self.root,orient=tk.VERTICAL)
        separator_canvas.pack(side=tk.LEFT,fill=tk.Y)

        self.frame_dest = tk.Frame(self.root,padx=5,pady=5)

        self.var_entry_start = tk.StringVar(value="Départ")
        self.start_entry = tk.Entry(self.frame_dest,bg='gray',fg='black',textvariable=self.var_entry_start)
        self.start_entry.pack(side=tk.TOP,fill=tk.X)

        self.var_entry_end = tk.StringVar(value="Arrivée")
        self.end_entry = tk.Entry(self.frame_dest,bg="gray",fg='black',textvariable=self.var_entry_end)
        self.end_entry.pack(fill=tk.X)

        self.frame_dest.pack(side=tk.TOP,fill=tk.X)

        separator_dest = Separator(self.root,orient=tk.HORIZONTAL)
        separator_dest.pack(side=tk.TOP,fill=tk.X)

        self.frame_opt = tk.Frame(self.root,padx=5,pady=5)

        self.choice_poussette = tk.IntVar()
        self.check_button_poussette = tk.Checkbutton(self.frame_opt,bg='gray',fg='black',text="Poussette/Fauteil",onvalue=True,offvalue=False,variable=self.choice_poussette)
        self.check_button_poussette.pack(side=tk.TOP,fill=tk.X)

        self.choice_bike = tk.IntVar()
        self.check_button_bike = tk.Checkbutton(self.frame_opt,bg='gray',fg='black',text="Vélo",onvalue=True,offvalue=False,variable=self.choice_bike)
        self.check_button_bike.pack(side=tk.TOP,fill=tk.X)

        self.choice_voiture = tk.IntVar()
        self.check_button_voiture = tk.Checkbutton(self.frame_opt,bg='gray',fg='black',text="Voiture",onvalue=True,offvalue=False,variable=self.choice_voiture)
        self.check_button_voiture.pack(side=tk.TOP,fill=tk.X)

        self.choice_foot = tk.IntVar()
        self.check_button_foot = tk.Checkbutton(self.frame_opt,bg='gray',fg='black',text="Pied",onvalue=True,offvalue=False,variable=self.choice_foot)
        self.check_button_foot.pack(side=tk.TOP,fill=tk.X)

        self.frame_opt.pack(side=tk.TOP,fill=tk.X)

        self.button_opt_av = tk.Button(self.root,text="Paramètres avancés",bg='gray',fg='black',padx=5,pady=5,relief='flat')
        self.button_opt_av.pack(side=tk.BOTTOM,fill=tk.X)
        self.button_opt_av.bind('<Button-1>',self.bouton_param_av)



    def loop(self):
        self.root.mainloop()

    def bouton_param_av(self,event):
        print("Vous avez cliquez sur le boutons des parametres avancé")
        print(f"Ville de départ {self.var_entry_start.get()}")
        print(f"Ville d'arrivee {self.var_entry_end.get()}")
        print(f"Choix Poussette {self.choice_poussette.get()}")

        dialog_params_av = TopLevelParams(self.root)


    def load_all_datas(self):
        self.carrefour_adjacences = Load_Files.load_data_nodes()



class TopLevelParams():
    def __init__(self,mainwindow):
        self.toplevel_params = tk.Toplevel(mainwindow)
        self.toplevel_params.config(height=100,width=400)
        
        self.init_widget()
        self.toplevel_params.mainloop()
        
    def init_widget(self):
        self.var_width_road = tk.DoubleVar(value=5.0)
        self.slidder_width_road = tk.Scale(self.toplevel_params,from_=0,to=20,variable=self.var_width_road,tickinterval=5,resolution=0.5,label="Seuil largeur de la chaussée",orient=tk.HORIZONTAL)
        self.slidder_width_road.pack(fill=tk.X)

        self.var_slope_max = tk.DoubleVar(value=4.0)
        self.slidder_slope_max = tk.Scale(self.toplevel_params,label="Pente maximale",from_=0,to=12,resolution=0.1,tickinterval=1.0,orient=tk.HORIZONTAL,variable=self.var_slope_max)
        self.slidder_slope_max.pack(fill=tk.X)


if __name__ == "__main__":
    root = MainWindow()
    root.loop()
