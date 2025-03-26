import os
import csv
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg
import tkinter as tk
from tkinter import filedialog
from itertools import accumulate
from tkinter import messagebox

def initialisation(): # fenêtre des paramètres en entrée
    def folder_path():
        global folder
        folder = filedialog.askdirectory()
        label_dossier.config(text=folder or "Aucun dossier sélectionné")

    def submit():
        global freq, vitesse
        try:
            freq = float(entry.get())
            vitesse = var.get()
            root.quit()
        except ValueError:
            erreur_label.config(text="Entrée invalide.")

    root = tk.Tk()
    root.title("Initialisation")

    explications=("Ceci est un programme de tracé animé de raw data obtenues à partir de la fonction record d'OpenWave.\n"
            "Sélectionner le dossier contenant la liste des traces (un dossier par acquisition), une fois l'animation démarée vous pouvez lire/mettre en pause avec la barre espace, puis naviguer entre les frames avec les flèches directionnelles.\n""En utilisant une rampe de courant symmétrique, sans offset sur CH2, le logiciel calcule automatiquement l'échelle temporelle et l'affiche en légende.")
    tk.Label(root, text=explications, wraplength=500, justify="left").pack(pady=10)
    instruction=("Indiquer, en Hz, la fréquence de la rampe de courant en CH2 pour retrouver l'échelle temporelle. Entrer 0 si il n'y a pas de rampe.")
    tk.Label(root, text=instruction,wraplength=500,).pack()
    entry = tk.Entry(root)
    entry.pack(pady=10)
    erreur_label = tk.Label(root, fg="red")
    erreur_label.pack()

    tk.Label(root, text="Choix de la vitesse de lecture ").pack()
    var = tk.StringVar(value=50)
    for text, val in [("Lent", 500), ("Normal", 50), ("Rapide", 5)]:
        tk.Radiobutton(root, text=text, variable=var, value=val).pack()

    tk.Label(root, text="").pack()

    tk.Label(root, text="Choix du dossier contenant les traces").pack()
    tk.Button(root, text="Choisir", command=folder_path).pack(pady=10)
    label_dossier = tk.Label(root, text="Aucun dossier sélectionné", fg="blue")

    tk.Button(root, text="Lancer AnimPlot", command=submit).pack(pady=10)

    root.mainloop()

    return freq, vitesse, folder

frequence, vitesse, folder_path=initialisation()

CH2= True
if freq==0:
    CH2= False
csv_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".CSV")]) #on identifie tous les fichiers CSV dans le dossier

if not csv_files: #on vérifie si il y a des traces 
    messagebox.showerror("Erreur", "Aucune trace trouvée !")
    exit()

def sampling_period(folder_path, file_path):
    path=os.path.join(folder_path, file_path)
    with open(path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        return float(reader[19][1])

def memory_length(folder_path, file_path):
    path=os.path.join(folder_path, file_path)
    with open(path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        return float(reader[1][1])

def vertical_scale(folder_path, file_path):
    path=os.path.join(folder_path, file_path)
    with open(path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        return float(reader[12][1])

def vunit(folder_path, file_path):
    path=os.path.join(folder_path, file_path)
    with open(path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        return str(reader[6][1])

def hunit(folder_path, file_path):
    path=os.path.join(folder_path, file_path)
    with open(path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        return str(reader[14][1])

def extract_waveform1(file_path): #on extrait les données de CH1
    waveform_data1 = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data_section = False
        for row in reader:
            if row and "Waveform Data" in row[0]:
                data_section = True
                continue
            if data_section and row:
                try:
                    waveform_data1.append(float(row[0]))
                except ValueError:
                    pass
    return np.array(waveform_data1)

def extract_waveform2(file_path): #on extrait la moyenne de la rampe en  CH2
    waveform_data2 = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        data_section = False
        for row in reader:
            try:
                if row and "Waveform Data" in row[2]:
                    data_section = True
                    continue
                if data_section and row:
                    try:
                        waveform_data2.append(float(row[2]))
                    except ValueError:
                        pass
            except IndexError:
                pass
    return np.mean(waveform_data2)  # Retourne la moyenne au lieu du tableau complet

def delta_temps(freq): #calcul de l'échelle temporelle
    global csv_files, folder_path, file_path
    meantot=np.empty(len(csv_files)) #on crée la liste des valeurs moyenne de la rampe

    for k in range(len(csv_files)):
        file_path = os.path.join(folder_path, csv_files[k])
        moy = extract_waveform2(file_path)
        meantot[k] = moy #on la  remplit avec la valeur moyenne à chaque instant
    meantot=meantot-np.min(meantot)#on applique un offset manuel pour ramener toutes les valeurs à des valeurs positives et éviter les erreurs de signe

    ecart=np.empty(len(meantot)) #on crée la liste des écarts temporels
    ecart[0]=0

    for k in range(1,len(meantot)):
        if 15>np.absolute(meantot[k]-meantot[k-1])>8:
            ecart[k]=np.absolute(meantot[k]-meantot[k-1]) #on la remplie
        else:
            if meantot[k]>65:
                ecart[k]=np.absolute((np.max(meantot)-meantot[k])+(np.max(meantot)-meantot[k-1])) #valeurs limite supérieurs
            else:
                ecart[k]=np.absolute(meantot[k]+meantot[k-1]) #valeurs limites inférieures 

    demiamp=np.max(meantot)
    demiper=np.divide(1,2*freq)
    ecart=ecart*demiper/(demiamp)
    temps=list(accumulate(ecart))
    return ecart,temps

vunit=vunit(folder_path, csv_files[0])
hunit=hunit(folder_path, csv_files[0])
sampling_period = sampling_period(folder_path, csv_files[0])
nb_points = memory_length(folder_path, csv_files[0])
vscale= vertical_scale(folder_path, csv_files[0])
time_axis_fixed = np.arange(0, nb_points * sampling_period, sampling_period)

fig1, ax1 = plt.subplots(figsize=(10, 5))
line1, = ax1.plot([], [], linewidth=1)
fig1.canvas.manager.set_window_title("AnimPlot v1.0")
ax1.set_xlabel(f"Temps ({hunit})")
ax1.set_ylabel(f"Amplitude ({vunit})")

ax1.set_xlim(0, time_axis_fixed[-1])
ax1.set_ylim(-4*vscale, 4*vscale)

is_paused = False #initialisation état pause et frame
current_frame = 0

def toggle_pause(event): #play/pause avec espace
    global is_paused
    if event.key == " ":
        is_paused = not is_paused 

def manual_navigation(event): #navigation avec les flèches
    global current_frame, is_paused
    if is_paused:
        if event.key == "right":
            current_frame = (current_frame + 1) % len(csv_files)
        elif event.key == "left":
            current_frame = (current_frame - 1) % len(csv_files) 
        update1(current_frame)
        fig1.canvas.draw()  

fig1.canvas.mpl_connect("key_press_event", toggle_pause)
fig1.canvas.mpl_connect("key_press_event", manual_navigation)

def init():
    line1.set_data([], [])
    return line1,

def update1(frame): #fonction qui s'occupe de l'animation
    global image_display, current_frame, ecart, filtre,temps, vscale, time_axis_fixed, vunit, hunit, CH2
    if not is_paused:
        current_frame = frame
    file_path = os.path.join(folder_path, csv_files[current_frame])

    waveform_data = extract_waveform1(file_path)
    if CH2 == True:
        waveform_data2 = extract_waveform2(file_path)

    line1.set_data(time_axis_fixed, vscale*waveform_data/25)
    ax1.set_title(f"Fichier : {csv_files[current_frame]}")    #on pose le titre comme étant le numéro du fichier
    if CH2 == True:
        line1.set_label(f"$\Delta$ t = {ecart[current_frame]:.4f}{hunit}, t = {temps[current_frame]:.4f}{hunit}") #on pose la légende comme étant le delta t correspondant
    ax1.legend()

    return line1

ecart,temps=delta_temps(frequence)
ani = animation.FuncAnimation(fig1, update1, frames=len(csv_files), init_func=init, interval=vitesse, blit=False)
plt.show()