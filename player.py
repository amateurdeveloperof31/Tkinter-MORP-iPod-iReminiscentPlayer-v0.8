# ------------------------------------------------------- Imports ------------------------------------------------------
from tkinter import * # Tkinter
from tkinter import filedialog, ttk # Tkinter
from io import BytesIO # Bytes IO
from mutagen.id3 import ID3 # Mutagen Tags
from mutagen.mp3 import MP3, HeaderNotFoundError # Mutagen Tags
from mutagen.flac import FLAC # Mutagen Tags
from mutagen.mp4 import MP4 # Mutagen Tags
from PIL import Image, ImageTk # Pillow
import json # JSON
import os # OS
from os.path import exists # Filepath
from math import ceil # Math
import requests # Requests
import time # Time
from datetime import datetime # Date/Time
from customtkinter import * # Custom Tkinter
from image_resizer import ImageResizer # Custom Image Resizer
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # PyGame Prompt Hide
import pygame.mixer as mixer # Mixer
# --------------------------------------------------- Global Variables -------------------------------------------------
main_background = "#2F4F7F"
alternate_background = "#1B3645"
slider_color = "#34A8FF"
playlist_frame_color = "#34A8FF"
current_song_color = "#fff523"
main_text = "#FFFFFF"  # White
secondary_text = "#B3B8CF"  # Light Gray-Blue
highlight = "#03A9F4"  # Bright Blue

skins = {
    "black": {
        "main_color": "#333333",
        "text": "white",
        "buttons": "#ffffff",
        "main_button_color": "#e14354",
        "playback_color": "#d13746",
        "play_pause_color": "#c02a38"
    },
    "blue": {
        "main_color": "#0096c1",
        "text": "white",
        "buttons": "#91948d",
        "main_button_color": "#eeeee8",
        "playback_color": "#e8e8e1",
        "play_pause_color": "#e2e2da"
    },
    "cyan": {
        "main_color": "#69bdbe",
        "text": "white",
        "buttons": "#91948d",
        "main_button_color": "#eeede8",
        "playback_color": "#e7e7e0",
        "play_pause_color": "#e2e2da"
    },
    "green": {
        "main_color": "#8bc932",
        "text": "white",
        "buttons": "#91948d",
        "main_button_color": "#edece7",
        "playback_color": "#e8e8e1",
        "play_pause_color": "#e2e2da"
    },
    "grey": {
        "main_color": "#6b6a6d",
        "text": "white",
        "buttons": "#ffffff",
        "main_button_color": "#242424",
        "playback_color": "#242424",
        "play_pause_color": "#242424"
    },
    "magenta": {
        "main_color": "#e54556",
        "text": "white",
        "buttons": "#ffffff",
        "main_button_color": "#242424",
        "playback_color": "#242424",
        "play_pause_color": "#242424"
    },
    "pink": {
        "main_color": "#d3248c",
        "text": "white",
        "buttons": "#91948d",
        "main_button_color": "#eeeee8",
        "playback_color": "#e8e7e1",
        "play_pause_color": "#e2e2da"
    },
    "red": {
        "main_color": "#e54557",
        "text": "white",
        "buttons": "#91948d",
        "main_button_color": "#eeede8",
        "playback_color": "#e7e6e0",
        "play_pause_color": "#e2e2db"
    },
    "white": {
        "main_color": "#deddd9",
        "text": "white",
        "buttons": "#91948d",
        "main_button_color": "#eeeee8",
        "playback_color": "#e7e6e0",
        "play_pause_color": "#e1e1da"
    }
}

skins_screen_bg = "#f4fdfd"

# Play State: {0: First Time - Paused, 1: Loaded - Paused, 2: Play, 3: Paused}
play_state = 0

folder_path_label = "No Folders Selected. Select a Folder First."

song_title = ""
song_artist = ""
song_album = ""

song_number = 0
current_song_length = 0

folder_path = None
current_song_name = None

play_queue = []
play_queue_extensions = []

sorted_song_names = []

current_song_extension = 0

playlist_song_label_names = []

status = None
# ----------------------------------------------------Main Class--------------------------------------------------------
class IReminiscentPlayer:
    def __init__(self):
        self.windows = Tk()
        self.windows.title("IPlayerClassic")
        width, height = 185, 400
        self.windows.minsize(width, height)
        self.windows.maxsize(width, height)
        self.windows.resizable(False, False)
        window_icon = PhotoImage(file="images/window_icon.png")
        self.windows.iconphoto(False, window_icon)
        self.windows.configure(bg=main_background)

        # Initialize Mixer
        mixer.init()

        self.current_time = 0
        self.song_time = None

        self.current_skin = "blue"
        self.playback_control_color = "direction-p"

        # Main Canvas
        self.main_canvas = Canvas(self.windows, width=width, height=height)
        self.main_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.main_skin_image = ImageResizer(f"images/skins/{self.current_skin}.png", 186)
        self.main_skin_imager = Label(self.main_canvas, image=self.main_skin_image.image)
        self.main_skin_imager.place(relx=0.5, rely=0.5, anchor="center")

        # Selected Folder Name
        self.labeler = Label(self.main_canvas, bg=skins_screen_bg, text="Songs playing in Folder", width=20,
                             font=("Arial", 8, "normal"))
        self.labeler.place(relx=0.5, rely=0.082, anchor=CENTER)

        self.folder_label = Label(self.main_canvas, bg=skins_screen_bg, text=folder_path_label, width=20,
                                  font=("Arial", 8, "bold"))
        self.folder_label.place(relx=0.5, rely=0.135, anchor=CENTER)

        # Song Name and Artist
        self.song_name_label = Label(self.main_canvas, bg=skins_screen_bg, text=song_title, font=("arial", 10, "bold"))
        self.song_name_label.place(relx=0.5, rely=0.3, anchor=CENTER)
        self.song_artist_label = Label(self.main_canvas, bg=skins_screen_bg, text=song_artist,
                                       font=("arial", 8, "normal"))
        self.song_artist_label.place(relx=0.5, rely=0.35, anchor=CENTER)

        # Song Duration and Progressbar
        self.current_duration_label = Label(self.main_canvas, bg=skins_screen_bg, text="00:00",
                                            font=("arial", 8, "normal"))
        self.current_duration_label.place(relx=0.47, rely=0.25, anchor=E)

        self.duration_divider_label = Label(self.main_canvas, bg=skins_screen_bg, text="/", font=("arial", 8, "normal"))
        self.duration_divider_label.place(relx=0.498, rely=0.25, anchor=CENTER)

        self.total_duration_label = Label(self.main_canvas, bg="#f4fdfd", text="00:00", font=("arial", 8, "normal"))
        self.total_duration_label.place(relx=0.53, rely=0.25, anchor=W)

        # Music Controls
        select_music_folder_image = ImageResizer("images/menu.png", 28)
        self.select_music_folder_button = Button(self.main_canvas, bg=skins[self.current_skin]["main_button_color"],
                                                activebackground = skins[self.current_skin]["main_button_color"],
                                                 image=select_music_folder_image.image, borderwidth=0,
                                                command=self.select_song_folder, highlightthickness=0)
        self.select_music_folder_button.place(relx=0.5, rely=0.53, anchor=CENTER)

        previous_song_image = ImageResizer(f"images/{self.playback_control_color}.png", 12)
        self.previous_song_button = Button(self.main_canvas, bg="#e8e8e1", image=previous_song_image.image,
                                           highlightthickness=0, borderwidth=0, activebackground="#e8e8e1")
        self.previous_song_button.place(relx=0.21, rely=0.67, anchor=CENTER)
        self.previous_song_button.bind("<ButtonPress-1>", lambda event: self.slider_pressed("backward"))
        self.previous_song_button.bind("<ButtonRelease-1>", lambda event: self.handle_release("backward"))

        self.play_song_image = ImageResizer("images/play.png", 12)
        self.pause_song_image = ImageResizer("images/pause.png", 12)
        self.play_song_button = Button(self.main_canvas, bg="#e8e8e1", image=self.play_song_image.image, command=self.play_song,
                                       highlightthickness=0, borderwidth=0, activebackground="#e8e8e1")
        self.play_song_button.place(relx=0.5, rely=0.81, anchor=CENTER)

        next_song_image = ImageResizer(f"images/{self.playback_control_color}.png", 12, True)
        self.next_song_button = Button(self.main_canvas, bg="#e8e8e1", image=next_song_image.image,
                                       highlightthickness=0, borderwidth=0, activebackground="#e8e8e1")
        self.next_song_button.place(relx=0.81, rely=0.67, anchor=CENTER)
        self.next_song_button.bind("<ButtonPress-1>", lambda event: self.slider_pressed("forward"))
        self.next_song_button.bind("<ButtonRelease-1>", lambda event: self.handle_release("forward"))

        # Loading Save File
        self.load_settings_file()

        # Saving Settings
        self.windows.protocol("WM_DELETE_WINDOW", self.close_program_event)

        # Skin Selector
        self.skin_selector_button = Button(self.main_canvas, bg="#e8e8e1", text="Select Skin",
                                           highlightthickness=0, borderwidth=0, activebackground="#e8e8e1",
                                           command=self.open_skin_selector)
        self.skin_selector_button.place(relx=0.8, rely=0.95, anchor=CENTER)

        # Window Mainloop
        self.windows.mainloop()
# --------------------------------------------------- Methods ----------------------------------------------------------
# ----------------------------------------------- Mute/Unmute Song -----------------------------------------------------
    def mute_unmute(self):
        global muted, song_volume
        if muted == 0:
            muted = 1
            mixer.music.set_volume(song_volume)
        else:
            muted = 0
            mixer.music.set_volume(0.0)

# -------------------------------------------------- Play Song ---------------------------------------------------------
    def play_song(self):
        global play_state
        if play_state == 0:
            self.update_progressbar()
            play_state = 1
        elif play_state == 1:
            play_state = 2
            if self.song_time:
                mixer.music.play()
                mixer.music.rewind()
                mixer.music.set_pos(self.song_time)
            else:
                mixer.music.play()
            self.play_song_button.configure(image=self.pause_song_image.image)
            self.update_progressbar()
        elif play_state == 2:
            play_state = 3
            self.play_song_button.configure(image=self.play_song_image.image)
            mixer.music.pause()
        else:
            play_state = 2
            self.play_song_button.configure(image=self.pause_song_image.image)
            mixer.music.unpause()
            self.update_progressbar()

# -------------------------------------------------- Next Song ---------------------------------------------------------
    def next_song(self):
        global play_queue, current_song_name, current_song_extension, song_number
        self.song_time = None
        if song_number < len(play_queue)-1:
            song_number += 1
            current_song_name = play_queue[song_number]
            current_song_extension = play_queue_extensions[song_number]
            self.load_song()

# ------------------------------------------------ Previous Song -------------------------------------------------------
    def previous_song(self):
        global play_queue, current_song_name, current_song_extension, song_number
        self.song_time = None
        if song_number > 0:
            song_number -= 1
            current_song_name = play_queue[song_number]
            current_song_extension = play_queue_extensions[song_number]
            self.load_song()

# --------------------------------------------- Select from Playlist ---------------------------------------------------
    def on_double_click(self, label_number, label_name, playlist_song_list_frame):
        global current_song_name, current_song_extension, song_number, play_queue
        song_number = label_number
        current_song_name = play_queue[song_number]
        current_song_extension = play_queue_extensions[song_number]
        self.song_time = None
        self.load_song()

# ---------------------------------------------- Select Song Folder ----------------------------------------------------
    def select_song_folder(self):
        global folder_path, current_song_name, song_number
        folder_path = filedialog.askdirectory()
        if folder_path:
            current_song_name = None
            self.song_time = None
            song_number = 0
            settings = {
                "folder_path": folder_path,
                "current_song_name": current_song_name,
                "current_song_time": self.song_time
            }
            with open('settings/irp_settings.json', 'w') as settings_file:
                settings_file.write(json.dumps(settings))
            self.load_settings_file()

# ------------------------------------------------- Load Settings ------------------------------------------------------
    def load_settings_file(self):
        global folder_path, current_song_name
        try:
            with open("settings/irp_settings.json", "r") as settings_file:
                settings_data = settings_file.read()
        except FileNotFoundError:
            settings = {
                "folder_path": None,
                "current_song_name": None,
                "current_song_time": None,
                "current_skin": "blue"
            }
            with open('settings/irp_settings.json', 'w') as settings_file:
                settings_file.write(json.dumps(settings, indent=4))
        else:
            settings_dict = json.loads(settings_data)
            folder_path = settings_dict['folder_path']
            if os.path.isdir(folder_path):
                try:
                    current_song_name = settings_dict['current_song_name']
                    self.song_time = settings_dict['current_song_time']
                    self.current_skin = settings_dict['current_skin']
                except json.decoder.JSONDecodeError:
                    current_song_name = None
                    self.song_time = None
                    self.current_skin = "blue"
            else:
                current_song_name = None
                self.song_time = None
                self.current_skin = "blue"

            self.load_playlist()

# ------------------------------------------------- Load Playlist ------------------------------------------------------
    def load_playlist(self):
        global folder_path, current_song_name, folder_path_label, play_queue, song_number, current_song_extension, play_queue_extensions

        self.update_skin(self.current_skin)

        if not folder_path or os.path.isdir(folder_path) == False:
            folder_path_label = "Select a Folder."
        else:
            playlist_song_label_names.clear()
            sorted_song_names.clear()

            play_queue *= 0
            play_queue_extensions *= 0

            for path, subdirs, files in os.walk(folder_path):
                for filenames in files:
                    if filenames.endswith("mp3") or filenames.endswith("wav") or filenames.endswith("flac"):

                        file_extension = os.path.splitext(filenames)
                        file_extension = file_extension[1].replace('.', '').upper()

                        try:
                            tags = globals()[file_extension](os.path.join(path, filenames))

                        except HeaderNotFoundError:
                            song_namer = os.path.splitext(filenames)
                            song_namer = song_namer[0]
                            song_title = song_namer
                        else:
                            if filenames.endswith("flac"):
                                song_title = tags.get('TITLE')[0]
                            else:
                                song_title = tags.get('TIT2')
                        if song_title == None:
                            song_title = filenames
                        sorted_song_names.append(str(song_title))
                        sorted_song_names.sort(key=str.lower)
                        indexer = sorted_song_names.index(song_title)

                        play_queue.insert(indexer, os.path.join(path, filenames))
                        play_queue_extensions.insert(indexer, file_extension)

            folder_path_label = os.path.basename(folder_path)
            self.folder_label.configure(text=folder_path_label.upper())
            if not current_song_name or current_song_name == "":
                current_song_name = play_queue[song_number]
                current_song_extension = play_queue_extensions[song_number]
            else:
                song_number = play_queue.index(current_song_name)
                current_song_extension = play_queue_extensions[song_number]

            self.load_song()

# --------------------------------------------------- Load Song --------------------------------------------------------
    def load_song(self):
        global folder_path, current_song_name, song_title, song_artist, song_album, play_state, song_number, current_song_length, status, current_song_extension
        if status:
            self.windows.after_cancel(status)
        self.play_song_button.configure(image=self.play_song_image.image)
        song_path = f"{current_song_name}"
        if current_song_extension == "M4A":
            current_song_extension = "MP4"
        current_song_length = globals()[current_song_extension](song_path).info.length
        song_mins = int(current_song_length / 60)
        song_secs = int(current_song_length % 60)
        minutes = seconds = 0
        # self.song_progress_bar.configure(to=current_song_length)
        self.current_duration_label.configure(text="{:02d}:{:02d}".format(minutes, seconds))
        self.total_duration_label.configure(text="{:02d}:{:02d}".format(song_mins, song_secs))
        mixer.music.load(song_path)
        if play_state != 0:
            play_state = 1
        tags = globals()[current_song_extension](song_path)

        if current_song_extension == "FLAC":
            song_title = str(tags.get('TITLE')[0])
            song_artist = str(tags.get('ARTIST')[0])
            song_album = str(tags.get('ALBUM')[0])
            album_artist = str(tags.get('ALBUMARTIST')[0])
        else:
            song_title = str(tags.get('TIT2'))
            song_artist = str(tags.get('TPE1'))
            song_album = str(tags.get('TALB'))
            album_artist = str(tags.get('TPE2'))

            if album_artist == None or album_artist == "":
                album_artist = song_artist

        self.song_namer = song_title
        self.song_artiste = song_artist

        self.update_music_info()
        self.play_song()

# -------------------------------------------------- Music Info --------------------------------------------------------
    def update_music_info(self):
        self.song_name_label.configure(text=self.song_namer)
        self.song_artist_label.configure(text=self.song_artiste)

# ------------------------------------------------ Song Progress -------------------------------------------------------
    def update_progressbar(self):
        global status, play_state, current_song_length, song_number, current_song_name
        if self.song_time:
            current_time = round((mixer.music.get_pos() / 1000) + self.song_time)
        else:
            current_time = round(mixer.music.get_pos() / 1000)
        # self.song_progress_bar.set(round(current_time))
        minutes, seconds = divmod(round(current_time), 60)
        self.current_duration_label.configure(text="{:02d}:{:02d}".format(minutes, seconds))
        if play_state == 2:
            if current_time < round(current_song_length) - 1:
                status = self.windows.after(1000, lambda: self.update_progressbar())
            else:
                if song_number < len(play_queue) - 1:
                    self.next_song()
                else:
                    self.song_time = 0
                    song_number = 0
                    current_song_name = 0
                    play_state = 0
                    mixer.music.stop()
                    # self.song_progress_bar.set(0)
                    self.current_duration_label.configure(text="00:00")
                    self.load_playlist()

# --------------------------------------------- Check Button Pressed ---------------------------------------------------
    def slider_pressed(self, seek_d, event=None):
        self.seek_mode = False
        self.seek_timer = self.windows.after(300, lambda: self.start_seeking(seek_d))

# -------------------------------------------------- Start Seek --------------------------------------------------------
    def start_seeking(self, seek_d):
        mixer.music.pause()
        self.current_time = round((mixer.music.get_pos() / 1000) + (self.song_time or 0))
        self.seek_mode = True
        self.slider_pressed_loop(seek_d)

# --------------------------------------------------- Seek Loop --------------------------------------------------------
    def slider_pressed_loop(self, seek_d):
        if seek_d == "forward":
            self.current_time = self.current_time + 1
        else:
            self.current_time = self.current_time - 1
        minutes, seconds = divmod(self.current_time, 60)
        self.current_duration_label.configure(text=f"{minutes:02d}:{seconds:02d}")

        if ceil(self.current_time) == ceil(current_song_length) - 1:
            self.next_song()
        elif ceil(self.current_time) < 1:
            self.song_time = 0
            self.play_song()

        self.song_time = self.current_time

        self.after_id = self.windows.after(100, lambda: self.slider_pressed_loop(seek_d))

# --------------------------------------------------- Seek Stop --------------------------------------------------------
    def slider_released(self, event=None):
        global play_state, current_song_length

        if hasattr(self, 'seek_timer'):
            self.windows.after_cancel(self.seek_timer)
            del self.seek_timer

        if getattr(self, 'seek_mode', False) and hasattr(self, 'after_id'):
            self.windows.after_cancel(self.after_id)
            del self.after_id

        play_state = 1
        self.play_song()

# ------------------------------------------------- Handle Release -----------------------------------------------------
    def handle_release(self, seek_d, event=None):
        if getattr(self, 'seek_mode', False):
            if hasattr(self, 'after_id'):
                self.windows.after_cancel(self.after_id)
                del self.after_id
            self.slider_released()
        else:
            if hasattr(self, 'seek_timer'):
                self.windows.after_cancel(self.seek_timer)
                del self.seek_timer
            if seek_d == "forward":
                self.next_song()
            else:
                self.previous_song()

# ---------------------------------------------------- On Close --------------------------------------------------------
    def close_program_event(self):
        global current_song_name
        current_song_time = (mixer.music.get_pos() / 1000)
        if self.song_time:
            current_song_time += self.song_time
        if current_song_time < 0:
            current_song_time = 0
        current_position = {
            'current_song_name': current_song_name,
            'current_song_time': current_song_time,
            'current_skin': self.current_skin
        }
        with open("settings/irp_settings.json", "r") as settings_file:
            settings_data = json.load(settings_file)
            settings_data.update(current_position)
        with open("settings/irp_settings.json", "w") as settings_file:
            json.dump(settings_data, settings_file, indent=4)
        self.windows.destroy()

# ----------------------------------------------- Open Skin Selector ---------------------------------------------------
    def open_skin_selector(self):
        skin_selector = Skin_Selector(self.windows, self, self.current_skin)

# ----------------------------------------------- Open Skin Selector ---------------------------------------------------
    def update_skin(self, selected_skin):
        self.main_skin_image = ImageResizer(f"images/skins/{selected_skin}.png", 186)
        self.main_skin_imager.config(image=self.main_skin_image.image)

        if selected_skin in ["blue", "cyan", "green", "pink", "red", "white"]:
            self.playback_control_color = "direction-p"
            self.play_control_color = "play"
            self.pause_control_color = "pause"
            self.menu_color = "menu"
        else:
            self.playback_control_color = "alt-direction-p"
            self.play_control_color = "alt-play"
            self.pause_control_color = "alt-pause"
            self.menu_color = "alt-menu"

        self.select_music_folder_image = ImageResizer(f"images/{self.menu_color}.png", 28)
        self.select_music_folder_button.config(image=self.select_music_folder_image.image,
                                               bg=skins[selected_skin]["main_button_color"],
                                               activebackground=skins[selected_skin]["main_button_color"])

        self.previous_song_image = ImageResizer(f"images/{self.playback_control_color}.png", 12)
        self.previous_song_button.config(image=self.previous_song_image.image, bg=skins[selected_skin]["playback_color"],
                                         activebackground=skins[selected_skin]["playback_color"])

        self.play_song_image = ImageResizer(f"images/{self.play_control_color}.png", 12)
        self.pause_song_image = ImageResizer(f"images/{self.pause_control_color}.png", 12)
        self.play_song_button.config(image=self.play_song_image.image, bg=skins[selected_skin]["play_pause_color"],
                                         activebackground=skins[selected_skin]["play_pause_color"])

        self.next_song_image = ImageResizer(f"images/{self.playback_control_color}.png", 12, True)
        self.next_song_button.config(image=self.next_song_image.image, bg=skins[selected_skin]["playback_color"],
                                         activebackground=skins[selected_skin]["playback_color"])

# -------------------------------------------------- Skin Selector -----------------------------------------------------
class Skin_Selector(Toplevel):
    def __init__(self, main_window, main_app, skin_color):
        global skins
        super().__init__()

        self.title("Select Player Skin")
        self.resizable(False, False)
        self.config(bg='white')

        x = int(main_window.winfo_x() + (main_window.winfo_width() / 2) - (300 / 2))
        y = main_window.winfo_y()
        self.geometry(f"200x300+{x}+{y + 50}")

        self.transient(main_window)
        self.grab_set()
        self.focus_set()

        self.main_window = main_window
        self.main_app = main_app
        self.selected_color = skin_color

        self.color_label = Label(self, text=self.selected_color.upper(), bg='white', font=("arial", 12, "bold"))
        self.color_label.place(relx=0.5, rely=0.08, anchor=CENTER)

        self.skin_image = ImageResizer(f"images/skins/{skin_color}.png", 100)
        self.skin_imager = Label(self, image=self.skin_image.image)
        self.skin_imager.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.next_image = ImageResizer(f"images/prev-img.png", 25, TRUE)
        self.next_imager = Button(self, image=self.next_image.image, bg='white', activebackground='white',
                                  borderwidth=0, command= lambda: self.skin_controls('forward'))
        self.next_imager.place(relx=0.88, rely=0.5, anchor=CENTER)

        self.prev_image = ImageResizer(f"images/prev-img.png", 25)
        self.prev_imager = Button(self, image=self.prev_image.image, bg='white', activebackground='white',
                                  borderwidth=0, command= lambda: self.skin_controls('backward'))
        self.prev_imager.place(relx=0.12, rely=0.5, anchor=CENTER)

        self.apply_button = Button(self, bg='white', text="✅", activebackground='white', height=2,
                                  borderwidth=0, command=self.apply_skin)
        self.apply_button.place(relx=0.45, rely=0.95, anchor=E)

        self.cancel_button = Button(self, text="❌", bg='white', activebackground='white', height=2,
                                   borderwidth=0)
        self.cancel_button.place(relx=0.55, rely=0.95, anchor=W)

# -------------------------------------------------- Skin Carousel -----------------------------------------------------
    def skin_controls(self, direc):
        all_skin_colors = list(skins.keys())
        index = all_skin_colors.index(self.selected_color)
        if direc == 'forward':
            index = min(index + 1, len(all_skin_colors) - 1)
        else:
            index = max(index - 1, 0)

        self.selected_color = all_skin_colors[index]

        self.skin_image = ImageResizer(f"images/skins/{self.selected_color}.png", 100)
        self.skin_imager.config(image=self.skin_image.image)

        self.color_label.config(text=self.selected_color.upper())

# --------------------------------------------------- Apply Skin -------------------------------------------------------
    def apply_skin(self):
        self.main_app.update_skin(self.selected_color)
        self.main_app.current_skin = self.selected_color
        self.destroy()

# ------------------------------------------------------- Run ----------------------------------------------------------
if __name__ == "__main__":
    app = IReminiscentPlayer()
