import os
import sys
import csv
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.image as mpimg
from matplotlib.ticker import MultipleLocator
import tkinter as tk
from tkinter import filedialog
from itertools import accumulate
from tkinter import messagebox

def initialisation(): # fenêtre des paramètres en entrée
    def folder_path():
        global folder
        folder = filedialog.askdirectory(initialdir='/Users/silio/Desktop/Projet Tut/Manip3/Traces avec nom vidéo')
        label_dossier.config(text=folder or "Aucun dossier sélectionné")

    def submit():
        global freq, vitesse_son, vitesse
        try:
            freq = float(entry_1.get())
            vitesse_son = float(entry_2.get())
            vitesse = var.get()
            root.quit()
        except ValueError:
            erreur_label.config(text="Entrée invalide.")

    root = tk.Tk()
    root.title("Initialisation")

    explications=("Ceci est un programme de tracé animé de raw data obtenues à partir de la fonction record d'OpenWave. \n""En utilisant une rampe de courant symmétrique, sans offset sur CH2, le logiciel calcule automatiquement l'échelle temporelle réelle entre les frames et l'affiche en légende. Un curseur permet également de naviguer valeur par valeur, et retrouve l'échelle spatiale sur une même frame à partir de la vitesse des ultrasons dans le milieu.")
    tk.Label(root, text=explications, wraplength=400, justify="left").pack(pady=10)
    instruction=("Fréquence de la rampe (Hz). 0 si aucune rampe")
    tk.Label(root, text=instruction,wraplength=400,).pack()
    entry_1 = tk.Entry(root)
    entry_1.pack(pady=10)
    erreur_label = tk.Label(root, fg="red")
    erreur_label.pack()

    instruction2=("Vitesse des ultrasons dans le milieu (m/s), entrez 0 pour que le curseur fournisse uniquement l'échelle temporelle")
    tk.Label(root, text=instruction2,wraplength=400,).pack()
    entry_2 = tk.Entry(root)
    entry_2.pack(pady=10)
    erreur_label = tk.Label(root, fg="red")
    erreur_label.pack()

    tk.Label(root, text="Vitesse de lecture: ").pack()
    var = tk.StringVar(value=50)
    for text, val in [("Lent", 500), ("Normal", 50), ("Rapide", 5)]:
        tk.Radiobutton(root, text=text, variable=var, value=val).pack()

    tk.Label(root, text="").pack()

    tk.Label(root, text="Dossier contenant les .csv:").pack()
    tk.Button(root, text="Choisir", command=folder_path).pack(pady=10)
    label_dossier = tk.Label(root, text="Aucun dossier sélectionné", fg="blue")

    tk.Button(root, text="Lancer AnimPlot", command=submit).pack(pady=10)
    tk.Label(root, text="Commandes: \n""Epace: pause/play \n""Flèches gauche/droit: frame précédente/suivante \n""A/Z: déplacement rapide du curseur \n""Flèches haut/bas: déplacement lent du curseur \n""Escape: relancer le programme").pack(pady=10)
    root.mainloop()

    return freq, vitesse_son, vitesse, folder

def extract_header(folder_path, file_path):
    path=os.path.join(folder_path, file_path)
    with open(path, newline='', encoding='utf-8') as f:
        reader = list(csv.reader(f))
        return float(reader[19][1]), float(reader[1][1]), float(reader[12][1]), str(reader[6][1]), str(reader[14][1]), float(reader[15][1])

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
    global csv_files, folder_path, file_path, CH2
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
    if CH2==True:
        demiper=np.divide(1,2*freq)
        ecart=ecart*demiper/(demiamp)
    temps=list(accumulate(ecart))
    return ecart,temps

def spatial_scale(t):
    return t*vitesse_son/2

def toggle_pause(event): #play/pause avec espace
    global is_paused
    if event.key == " ":
        is_paused = not is_paused 

def manual_navigation(event):  
    global current_frame, index

    if is_paused:  # On navigue seulement en pause
        if event.key == "right":
            current_frame = (current_frame + 1) % len(csv_files)
        elif event.key == "left":
            current_frame = (current_frame - 1) % len(csv_files)
        elif event.key == "up" and index < 9999:
            index += 1
        elif event.key == "down" and index > 0:
            index -= 1
        elif event.key == "z" and index < 9900:
            index += 100
        elif event.key == "a" and index > 0:
            index -= 100

        update1(current_frame)
        fig1.canvas.draw_idle()  


def restart():
    os.execl(sys.executable, sys.executable, *sys.argv)

def init():
    line1.set_data([], [])
    return line1,


def update1(frame): #fonction qui s'occupe de l'animation
    global image_display, current_frame, ecart, filtre,temps, vscale, time_axis_fixed, vunit, hunit, CH2, index,espace, vson

    file_path = os.path.join(folder_path, csv_files[current_frame])

    waveform_data = extract_waveform1(file_path)
    if CH2 == True:
        waveform_data2 = extract_waveform2(file_path)
    y=vscale*waveform_data/25
    cursor_line.set_offsets([[time_axis_fixed[index], y[index]]])
    line1.set_data(time_axis_fixed, y)
    if vson==True:
        cursor_line.set_label(f"  Position curseur: {'{:.7e}'.format(espace[index]).rstrip('0').rstrip('.')}m")
    else:
        cursor_line.set_label(f"  Position curseur: {'{:.7e}'.format(time_axis_fixed[index]).rstrip('0').rstrip('.')}s")
    ax1.set_title(f"Fichier : {csv_files[current_frame]}", color='white')    #on pose le titre comme étant le numéro du fichier
    if CH2 == True:
        line1.set_label(f"Ecart frame précédente: {ecart[current_frame]:.6f}s       Temps écoulé: {temps[current_frame]:.6f}s") #on pose la légende comme étant le delta t correspondant
    ax1.legend(handletextpad=0, handlelength=0,markerscale=0,loc='upper center', bbox_to_anchor=(0.5, -0.07),
          fancybox=True, shadow=True, ncol=5)
    return line1

def frame_generator():
    global current_frame
    while True:
        if not is_paused:
            current_frame = (current_frame + 1) % len(csv_files)
        yield current_frame

frequence, vitesse_son, vitesse, folder_path=initialisation()
CH2= True
vson= True
if freq==0:
    CH2= False
if vitesse_son==0:
    vson= False
csv_files = sorted([f for f in os.listdir(folder_path) if f.endswith(".CSV")]) #on identifie tous les fichiers CSV dans le dossier

if not csv_files: #on vérifie si il y a des traces 
    messagebox.showerror("Erreur", "Aucune trace trouvée !")
    restart()

sampling_period, nb_points, vscale, vunit, hunit, hscale = extract_header(folder_path, csv_files[0])
time_axis_fixed = np.arange(0, nb_points * sampling_period, sampling_period)

fig1, ax1 = plt.subplots(figsize=(10, 5), facecolor='black')
ax1.set_facecolor('black')
line1, = ax1.plot([], [], linewidth=1, zorder=1, color='#E9EC4D')
fig1.canvas.manager.set_window_title("AnimPlot v1.0")
ax1.set_xlabel(f"Temps ({hunit})", color='white')
ax1.set_ylabel(f"Amplitude ({vunit})", color='white')

ax1.set_xlim(0, time_axis_fixed[-1])
ax1.set_ylim(-6*vscale, 6*vscale)

ax1.spines['bottom'].set_color('black')  
ax1.spines['top'].set_color('black')  
ax1.spines['left'].set_color('black') 
ax1.spines['right'].set_color('black')  

ax1.xaxis.set_major_locator(MultipleLocator(hscale))  
ax1.yaxis.set_major_locator(MultipleLocator(vscale))

ax1.tick_params(axis='x', colors='white') 
ax1.tick_params(axis='y', colors='white')
ax1.grid(True, color='white', linestyle=((0, (1, 10))), linewidth=0.5, aa=True)
for spine in ax1.spines.values():
    spine.set_color('white')  
    spine.set_linewidth(1)
index = 0
cursor_line = ax1.scatter([], [], color='#70F0EE',  marker='+', s=1000, zorder=2)

is_paused = False #initialisation état pause et frame
current_frame = 0

fig1.canvas.mpl_connect("key_press_event", toggle_pause)
fig1.canvas.mpl_connect("key_press_event", manual_navigation)


espace=spatial_scale(time_axis_fixed)
ecart,temps=delta_temps(frequence)

ani = animation.FuncAnimation(fig1, update1, frames=frame_generator, init_func=init, interval=vitesse, blit=False,save_count=len(csv_files))
plt.show()