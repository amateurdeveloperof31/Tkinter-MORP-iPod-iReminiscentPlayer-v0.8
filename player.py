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
from musicbrainz_api import MusicBrainzAPI # Music Brainz API
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
    "blue": {
        "buttons": "#91948d",
        "buttons_bg": "#e8e8e1",
        "screen_bg": "#f4fdfd"
    }
}

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

        # Main Canvas
        self.main_canvas = Canvas(self.windows, width=width, height=height)
        self.main_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.main_skin_image = ImageResizer("images/skins/blue.png", 186)
        self.main_skin_imager = Label(self.main_canvas, image=self.main_skin_image.image)
        self.main_skin_imager.place(relx=0.5, rely=0.5, anchor="center")

        # Selected Folder Name
        self.labeler = Label(self.main_canvas, bg="#f4fdfd", text="Songs playing in Folder", font=("Arial", 8, "normal"),
                             width=20)
        self.labeler.place(relx=0.5, rely=0.082, anchor=CENTER)

        self.folder_label = Label(self.main_canvas, bg="#f4fdfd", text=folder_path_label, font=("Arial", 8, "bold"),
                                  width=20)
        self.folder_label.place(relx=0.5, rely=0.135, anchor=CENTER)

        # Song Name and Artist
        self.song_name_label = Label(self.main_canvas, bg="#f4fdfd", text=song_title, font=("arial", 10, "bold"))
        self.song_name_label.place(relx=0.5, rely=0.3, anchor=CENTER)
        self.song_artist_label = Label(self.main_canvas, bg="#f4fdfd", text=song_artist, font=("arial", 8, "normal"))
        self.song_artist_label.place(relx=0.5, rely=0.35, anchor=CENTER)

        # Song Duration and Progressbar
        self.current_duration_label = Label(self.main_canvas, bg="#f4fdfd", text="00:00", font=("arial", 8, "normal"))
        self.current_duration_label.place(relx=0.47, rely=0.25, anchor=E)

        self.duration_divider_label = Label(self.main_canvas, bg="#f4fdfd", text="/", font=("arial", 8, "normal"))
        self.duration_divider_label.place(relx=0.498, rely=0.25, anchor=CENTER)

        # self.song_progress_bar = CTkSlider(self.main_canvas, orientation=HORIZONTAL,
        #                                          progress_color=slider_color, fg_color="white",
        #                                          width=185, button_color=slider_color)
        # self.song_progress_bar.bind("<ButtonRelease-1>", self.manual_slider_positioning)
        # self.song_progress_bar.place(relx=0.5, rely=0.82, anchor=CENTER)

        self.total_duration_label = Label(self.main_canvas, bg="#f4fdfd", text="00:00", font=("arial", 8, "normal"))
        self.total_duration_label.place(relx=0.53, rely=0.25, anchor=W)

        # Music Controls
        select_music_folder_image = ImageResizer("images/menu.png", 30)
        self.select_music_folder_button = Button(self.main_canvas, bg="#edede7", text="Menu", image=select_music_folder_image.image,
                                           command=self.select_song_folder,
                                           highlightthickness=0, borderwidth=0, activebackground="#edede7")
        self.select_music_folder_button.place(relx=0.5, rely=0.53, anchor=CENTER)

        previous_song_image = ImageResizer("images/direction-p.png", 12)
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

        next_song_image = ImageResizer("images/direction-n.png", 12)
        self.next_song_button = Button(self.main_canvas, bg="#e8e8e1", image=next_song_image.image,
                                       highlightthickness=0, borderwidth=0, activebackground="#e8e8e1")
        self.next_song_button.place(relx=0.81, rely=0.67, anchor=CENTER)
        self.next_song_button.bind("<ButtonPress-1>", lambda event: self.slider_pressed("forward"))
        self.next_song_button.bind("<ButtonRelease-1>", lambda event: self.handle_release("forward"))

        # Loading the Save File
        self.load_settings_file()

        # Saving Before Closing Window
        self.windows.protocol("WM_DELETE_WINDOW", self.close_program_event)

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
            with open('settings/mmp_settings.json', 'w') as settings_file:
                settings_file.write(json.dumps(settings))
            self.load_settings_file()

# ------------------------------------------------- Load Settings ------------------------------------------------------
    def load_settings_file(self):
        global folder_path, current_song_name
        try:
            with open("settings/mmp_settings.json", "r") as settings_file:
                settings_data = settings_file.read()
        except FileNotFoundError:
            settings = {
                "folder_path": None,
                "current_song_name": None,
                "current_song_time": None
            }
            with open('settings/mmp_settings.json', 'w') as settings_file:
                settings_file.write(json.dumps(settings, indent=4))
        else:
            settings_dict = json.loads(settings_data)
            folder_path = settings_dict['folder_path']
            if os.path.isdir(folder_path):
                try:
                    current_song_name = settings_dict['current_song_name']
                    self.song_time = settings_dict['current_song_time']
                except json.decoder.JSONDecodeError:
                    current_song_name = None
                    self.song_time = None
            else:
                current_song_name = None
                self.song_time = None

            self.load_playlist()

# ------------------------------------------------- Load Playlist ------------------------------------------------------
    def load_playlist(self):
        global folder_path, current_song_name, folder_path_label, play_queue, song_number, current_song_extension, play_queue_extensions
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

# ------------------------------------------------ Song Thumbnails -----------------------------------------------------
    def get_song_thumbnail(self, tags, song_namer, song_artiste):
        sasa_joined = f"{song_namer} {song_artiste}"
        image_file_name = ''.join(letter for letter in sasa_joined if letter.isalnum())
        image_location = f"images/album_art/{image_file_name}"
        try:
            image_location = f"{image_location}.png"
            # pil_image = Image.open(image_location)
            # album_art_image = ImageTk.PhotoImage(pil_image)
            album_art_image = ImageResizer(image_location, 200)
        except (TclError, FileNotFoundError) as e:
            print(f'File Location Error:{e}')
            try:
                pict = tags.get("APIC:").data
            except AttributeError as e:
                print(f'Song Tag Error:{e}\n Default Album Art!!')
                image_location = "images/default_album_art.png"
                album_art_image = ImageResizer(image_location, 200)
                return album_art_image, image_location
            else:
                im = Image.open(BytesIO(pict))
                new_image = im.resize((300, 300))
                sasa_joined = f"{song_namer} {song_artiste}"
                image_file_name = ''.join(letter for letter in sasa_joined if letter.isalnum())
                image_location = f"images/album_art/{image_file_name}.png"
                new_image.save(image_location)
                album_art_image = ImageResizer(image_location, 200)
        return album_art_image, image_location

# ---------------------------------------------- Download Album Art ----------------------------------------------------
    def download_album_art(self):
        song_namer = self.song_namer
        song_artiste = self.song_artiste

        try:
            api = MusicBrainzAPI()
            response = api.search_releases(f'release:{song_namer} AND artist:{song_artiste}')
            album_art_url = response["images"][0]["thumbnails"]["small"]

        except (requests.exceptions.ConnectionError, requests.exceptions.HTTPError,
                requests.exceptions.MissingSchema, TypeError, KeyError):
            image_location = "images/default_album_art.png"
            self.album_art_image = ImageResizer(image_location, 200)

        else:
            sasa_joined = f"{song_namer} {song_artiste}"
            image_file_name = ''.join(letter for letter in sasa_joined if letter.isalnum())
            image_location = f"images/album_art/{image_file_name}.png"
            try:
                img_data = requests.get(album_art_url).content
            except requests.exceptions.MissingSchema as e:
                print(e)
                image_location = "images/default_album_art.png"
                self.album_art_image = ImageResizer(image_location, 200)
            else:
                with open(image_location, 'wb') as handler:
                    handler.write(img_data)
                imgee = Image.open(image_location)
                self.album_art_image = ImageTk.PhotoImage(imgee)
                try:
                    image_location = f"{image_location}"
                    pil_image = Image.open(image_location)
                    self.album_art_image = ImageTk.PhotoImage(pil_image)
                except (TclError, FileNotFoundError, AttributeError) as e:
                    print(f'Song Tag Error:{e}\n Default Album Art!!')
                    image_location = "images/default_album_art.png"
                    self.album_art_image = ImageResizer(image_location, 200)

        self.update_music_info()

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
        print(self.song_time)
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
            'current_song_time': current_song_time
        }
        with open("settings/mmp_settings.json", "r") as settings_file:
            settings_data = json.load(settings_file)
            settings_data.update(current_position)
        with open("settings/mmp_settings.json", "w") as settings_file:
            json.dump(settings_data, settings_file, indent=4)
        self.windows.destroy()

# ------------------------------------------------------- Run ----------------------------------------------------------
if __name__ == "__main__":
    app = IReminiscentPlayer()
