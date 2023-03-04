import tkinter as tk


class MainWindow():
    def __init__(self) :
        self.root = tk.Tk()
        self.root.geometry("600x600")

        self.initWidget()


    def initWidget(self):
        self.label_test = tk.Label(self.root,text="Bonjour je suis un test")
        self.label_test.pack()

    def loop(self):
        self.root.mainloop()





if __name__ == "__main__":
    root = MainWindow()
    root.loop()
