# ------------------------------------------------------- Imports ------------------------------------------------------
from dataclasses import dataclass # Dataclasses
from tkinter import * # Tkinter
from tkinter import filedialog, messagebox # Tkinter
from mutagen import File as MutagenFile # Mutagen File
from io import BytesIO # Bytes IO
from mutagen.id3 import ID3 # Mutagen Tags
from mutagen.mp3 import MP3, HeaderNotFoundError # Mutagen Tags
from mutagen.flac import FLAC # Mutagen Tags
from mutagen.mp4 import MP4 # Mutagen Tags
import json # JSON
import os # OS
from pathlib import Path
from math import ceil # Math
import time # Time
from image_resizer import ImageResizer # Custom Image Resizer
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # PyGame Prompt Hide
import pygame.mixer as mixer # Mixer
# -------------------------------------------------- Global Variables --------------------------------------------------
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

status = None

# --------------------------------------------------- Main Class -------------------------------------------------------
class IReminiscentPlayer:
    def __init__(self):

        # Windows UI
        self.windows = Tk()
        self.windows.title("IPlayerClassic")
        width, height = 185, 400
        self.windows.geometry(f"{width}x{height}")
        self.windows.resizable(False, False)
        window_icon = PhotoImage(file="assets/images/window_icon.png")
        self.windows.iconphoto(False, window_icon)

        # Initialize Mixer
        mixer.init()
        self.main_folder_path = None
        self.play_state = 0 # Play State: {0: First Time - Paused, 1: Loaded - Paused, 2: Play, 3: Paused}
        self.resume_time = None
        self.current_skin = 'blue'
        self.playback_control_color = "direction-p"
        self.folder_path_label = "Select a Folder from Menu."
        self.skins_screen_bg = "#f4fdfd"

        # Main Canvas
        self.main_canvas = Canvas(self.windows, width=width, height=height)
        self.main_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.main_skin_image = ImageResizer(f"assets/images/skins/{self.current_skin}.png", 186)
        self.main_skin_imager = Label(self.main_canvas, image=self.main_skin_image.image)
        self.main_skin_imager.place(relx=0.5, rely=0.5, anchor="center")

        # Labels
        # Selected Folder Name
        self.labeler = Label(self.main_canvas, bg=self.skins_screen_bg, text="Songs playing in Folder", width=20,
                             font=("Arial", 8, "normal"))
        self.labeler.place(relx=0.5, rely=0.082, anchor=CENTER)

        self.folder_label = Label(self.main_canvas, bg=self.skins_screen_bg, text=self.folder_path_label, width=20,
                                  font=("Arial", 8, "bold"))
        self.folder_label.place(relx=0.5, rely=0.135, anchor=CENTER)

        # Song Name and Artist
        self.song_name_label = Label(self.main_canvas, bg=self.skins_screen_bg, font=("arial", 10, "bold"))
        self.song_name_label.place(relx=0.5, rely=0.3, anchor=CENTER)
        self.song_artist_label = Label(self.main_canvas, bg=self.skins_screen_bg,
                                       font=("arial", 8, "normal"))
        self.song_artist_label.place(relx=0.5, rely=0.35, anchor=CENTER)

        # Song Duration and Progressbar
        self.current_duration_label = Label(self.main_canvas, bg=self.skins_screen_bg, text="00:00",
                                            font=("arial", 8, "normal"))
        self.current_duration_label.place(relx=0.47, rely=0.25, anchor=E)

        self.duration_divider_label = Label(self.main_canvas, bg=self.skins_screen_bg, text="/", font=("arial", 8, "normal"))
        self.duration_divider_label.place(relx=0.498, rely=0.25, anchor=CENTER)

        self.total_duration_label = Label(self.main_canvas, bg="#f4fdfd", text="00:00", font=("arial", 8, "normal"))
        self.total_duration_label.place(relx=0.53, rely=0.25, anchor=W)

        # Buttons
        # Music Controls
        select_music_folder_image = ImageResizer("assets/images/menu.png", 28)
        self.select_music_folder_button = Button(self.main_canvas, bg=skins[self.current_skin]["main_button_color"],
                                                activebackground = skins[self.current_skin]["main_button_color"],
                                                 image=select_music_folder_image.image, borderwidth=0,
                                                command=self.select_song_folder, highlightthickness=0)
        self.select_music_folder_button.place(relx=0.5, rely=0.53, anchor=CENTER)

        previous_song_image = ImageResizer(f"assets/images/{self.playback_control_color}.png", 12)
        self.previous_song_button = Button(self.main_canvas, bg="#e8e8e1", image=previous_song_image.image,
                                           highlightthickness=0, borderwidth=0, activebackground="#e8e8e1")
        self.previous_song_button.place(relx=0.21, rely=0.67, anchor=CENTER)
        self.previous_song_button.bind("<ButtonPress-1>", lambda event: self.slider_pressed("backward"))
        self.previous_song_button.bind("<ButtonRelease-1>", lambda event: self.handle_release("backward"))

        self.play_song_image = ImageResizer("assets/images/play.png", 12)
        self.pause_song_image = ImageResizer("assets/images/pause.png", 12)
        self.play_song_button = Button(self.main_canvas, bg="#e8e8e1", image=self.play_song_image.image, command=self.play_song,
                                       highlightthickness=0, borderwidth=0, activebackground="#e8e8e1")
        self.play_song_button.place(relx=0.5, rely=0.81, anchor=CENTER)

        next_song_image = ImageResizer(f"assets/images/{self.playback_control_color}.png", 12, True)
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
# ------------------------------------------------ Load Settings -------------------------------------------------------
    def load_settings_file(self):
        settings_filepath = "assets/config/irp_settings.json"

        try:
            with open(settings_filepath, 'r') as settings_file:
                settings_data = settings_file.read()
            settings_dict = json.loads(settings_data)

            self.main_folder_path = settings_dict['main_folder_path']
            self.current_track_title = settings_dict['current_track_title']
            self.resume_time = settings_dict['resume_time']
            self.current_skin = settings_dict['current_skin']

        except (FileNotFoundError, json.decoder.JSONDecodeError, KeyError) as e:
            messagebox.showerror("Error!!", f"Error: {e}. New file has been created.")
            settings = {
                "main_folder_path": None,
                "current_track_title": None,
                "resume_time": None,
                "current_skin": "blue"
            }
            with open(settings_filepath, 'w') as settings_file:
                settings_file.write(json.dumps(settings, indent=4))

        self.update_skin(self.current_skin)
        self.load_playlist()

# ------------------------------------------------ Load Playlist -------------------------------------------------------
    def load_playlist(self):
        if not self.main_folder_path or not Path(self.main_folder_path).is_dir:
            self.folder_path_label = "Select a Folder."
            return self.folder_path_label
        else:
            self.main_playlist = []
            self.current_track_info = {}
            self.current_track_number = None
            for path in Path(self.main_folder_path).rglob('*'):
                try:
                    if path.is_file() and path.suffix.lower() in [".mp3" or ".wav" or ".flac"]:
                        track_extension = path.suffix[1:].upper()
                        if track_extension == "M4A":
                            track_extension = "MP4"
                        tags = globals()[track_extension](path)
                        track_length = tags.info.length

                        if path.suffix.lower() == (".flac"):
                            track_name = str(tags.get('TITLE')[0])
                            track_artist = str(tags.get('ARTIST')[0])
                            track_album = str(tags.get('ALBUM')[0])
                        else:
                            track_name = str(tags.get('TIT2'))
                            track_artist = str(tags.get('TPE1'))
                            track_album = str(tags.get('TALB'))

                        track_details = {
                                'track_name': track_name,
                                'track_path': str(path),
                                'track_artist': track_artist,
                                'track_album': track_album,
                                'track_extension': track_extension,
                                'track_length': track_length
                        }
                        self.main_playlist.append(track_details)
                except Exception as e:
                    return messagebox.showerror("Error!!", f"Error: {str(e)}", parent=self)

        self.main_playlist = sorted(self.main_playlist, key=lambda x: x['track_name'])

        folder_path_label = os.path.basename(self.main_folder_path)
        self.folder_label.configure(text=folder_path_label.upper())
        if self.current_track_title:
            for index, song_detail in enumerate(self.main_playlist):
                if song_detail['track_name'] == self.current_track_title:
                    self.current_track_info = song_detail
                    self.current_track_number = index
        else:
            self.current_track_number = 0
            self.current_track_info = self.main_playlist[self.current_track_number]
            self.current_track_title = self.current_track_info['track_name']

        self.load_song()

# --------------------------------------------------- Load Song --------------------------------------------------------
    def load_song(self):
        global status
        if status:
            self.windows.after_cancel(status)
        self.play_song_button.configure(image=self.play_song_image.image)
        song_path = self.current_track_info['track_path']
        current_song_length = self.current_track_info['track_length']
        song_mins = int(current_song_length / 60)
        song_secs = int(current_song_length % 60)
        minutes = seconds = 0
        self.current_duration_label.configure(text="{:02d}:{:02d}".format(minutes, seconds))
        self.total_duration_label.configure(text="{:02d}:{:02d}".format(song_mins, song_secs))
        mixer.music.load(song_path)
        if self.play_state != 0:
            self.play_state = 1

        self.update_music_info()
        self.play_song()

# -------------------------------------------------- Play Song ---------------------------------------------------------
    def play_song(self):
        if self.play_state == 0:
            self.play_state = 1
            self.update_progressbar()
        elif self.play_state == 1:
            self.play_state = 2
            mixer.music.play()
            if self.resume_time:
                mixer.music.rewind()
                mixer.music.set_pos(self.resume_time)
            self.play_song_button.configure(image=self.pause_song_image.image)
            self.update_progressbar()
        elif self.play_state == 2:
            self.play_state = 3
            self.play_song_button.configure(image=self.play_song_image.image)
            mixer.music.pause()
        else:
            self.play_state = 2
            self.play_song_button.configure(image=self.pause_song_image.image)
            mixer.music.unpause()
            self.update_progressbar()

# -------------------------------------------------- Next Song ---------------------------------------------------------
    def next_song(self):
        self.resume_time = None
        if self.current_track_number < len(self.main_playlist)-1:
            self.current_track_number += 1
            self.current_track_info = self.main_playlist[self.current_track_number]
            self.load_song()

# ------------------------------------------------ Previous Song -------------------------------------------------------
    def previous_song(self):
        self.resume_time = None
        if self.current_track_number > 0:
            self.current_track_number -= 1
            self.current_track_info = self.main_playlist[self.current_track_number]
            self.load_song()

# ---------------------------------------------- Select Song Folder ----------------------------------------------------
    def select_song_folder(self):
        folder_path = filedialog.askdirectory()

        if folder_path:
            self.main_folder_path = folder_path
            current_skin = self.current_skin
            settings = {
                "main_folder_path": self.main_folder_path,
                "current_track_title": None,
                "resume_time": None,
                "current_skin": current_skin
            }
            with open('assets/config/irp_settings.json', 'w') as settings_file:
                settings_file.write(json.dumps(settings))
            self.load_settings_file()

# -------------------------------------------------- Music Info --------------------------------------------------------
    def update_music_info(self):
        self.song_name_label.configure(text=self.current_track_info['track_name'])
        self.song_artist_label.configure(text=self.current_track_info['track_artist'])

# ------------------------------------------------ Song Progress -------------------------------------------------------
    def update_progressbar(self):
        global status
        current_song_length = self.current_track_info['track_length']
        if self.resume_time:
            current_time = round((mixer.music.get_pos() / 1000) + self.resume_time)
        else:
            current_time = round(mixer.music.get_pos() / 1000)
        minutes, seconds = divmod(round(current_time), 60)
        self.current_duration_label.configure(text="{:02d}:{:02d}".format(minutes, seconds))
        if self.play_state == 2:
            if current_time < round(current_song_length) - 1:
                status = self.windows.after(1000, lambda: self.update_progressbar())
            else:
                if self.current_track_number < len(self.main_playlist) - 1:
                    self.next_song()
                else:
                    self.resume_time = 0
                    self.current_track_number = 0
                    self.current_track_title = None
                    self.play_state = 0
                    mixer.music.stop()
                    self.current_duration_label.configure(text="00:00")
                    self.load_playlist()

# --------------------------------------------- Check Button Pressed ---------------------------------------------------
    def slider_pressed(self, seek_d, event=None):
        self.seek_mode = False
        self.seek_timer = self.windows.after(300, lambda: self.start_seeking(seek_d))

# -------------------------------------------------- Start Seek --------------------------------------------------------
    def start_seeking(self, seek_d):
        mixer.music.pause()
        self.current_time = round((mixer.music.get_pos() / 1000) + (self.resume_time or 0))
        self.seek_mode = True
        self.slider_pressed_loop(seek_d)

# --------------------------------------------------- Seek Loop --------------------------------------------------------
    def slider_pressed_loop(self, seek_d):
        current_song_length = self.current_track_info['track_length']
        if seek_d == "forward":
            self.current_time = self.current_time + 1
        else:
            self.current_time = self.current_time - 1
        minutes, seconds = divmod(self.current_time, 60)
        self.current_duration_label.configure(text=f"{minutes:02d}:{seconds:02d}")

        if ceil(self.current_time) == ceil(current_song_length) - 1:
            self.next_song()
        elif ceil(self.current_time) < 1:
            self.resume_time = 0
            self.play_song()

        self.resume_time = self.current_time

        self.after_id = self.windows.after(100, lambda: self.slider_pressed_loop(seek_d))

# --------------------------------------------------- Seek Stop --------------------------------------------------------
    def slider_released(self, event=None):

        if hasattr(self, 'seek_timer'):
            self.windows.after_cancel(self.seek_timer)
            del self.seek_timer

        if getattr(self, 'seek_mode', False) and hasattr(self, 'after_id'):
            self.windows.after_cancel(self.after_id)
            del self.after_id

        self.play_state = 1
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
        if self.resume_time:
            current_song_time = max(0, ((mixer.music.get_pos() / 1000) + self.resume_time))
        else:
            current_song_time = max(0, (mixer.music.get_pos() / 1000))
        current_settings = {
            "main_folder_path": self.main_folder_path,
            'current_track_title': self.current_track_title,
            'resume_time': current_song_time,
            'current_skin': self.current_skin
        }
        with open("assets/config/irp_settings.json", "w") as settings_file:
            settings_file.write(json.dumps(current_settings))
        self.windows.destroy()

# ----------------------------------------------- Open Skin Selector ---------------------------------------------------
    def open_skin_selector(self):
        skin_selector = Skin_Selector(self.windows, self)

# ----------------------------------------------- Open Skin Selector ---------------------------------------------------
    def update_skin(self, selected_skin):
        self.main_skin_image = ImageResizer(f"assets/images/skins/{selected_skin}.png", 186)
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

        self.select_music_folder_image = ImageResizer(f"assets/images/{self.menu_color}.png", 28)
        self.select_music_folder_button.config(image=self.select_music_folder_image.image,
                                               bg=skins[selected_skin]["main_button_color"],
                                               activebackground=skins[selected_skin]["main_button_color"])

        self.previous_song_image = ImageResizer(f"assets/images/{self.playback_control_color}.png", 12)
        self.previous_song_button.config(image=self.previous_song_image.image, bg=skins[selected_skin]["playback_color"],
                                         activebackground=skins[selected_skin]["playback_color"])

        self.play_song_image = ImageResizer(f"assets/images/{self.play_control_color}.png", 12)
        self.pause_song_image = ImageResizer(f"assets/images/{self.pause_control_color}.png", 12)
        self.play_song_button.config(image=self.play_song_image.image, bg=skins[selected_skin]["play_pause_color"],
                                         activebackground=skins[selected_skin]["play_pause_color"])

        self.next_song_image = ImageResizer(f"assets/images/{self.playback_control_color}.png", 12, True)
        self.next_song_button.config(image=self.next_song_image.image, bg=skins[selected_skin]["playback_color"],
                                         activebackground=skins[selected_skin]["playback_color"])

# ----------------------------------------------- Mute/Unmute Song -----------------------------------------------------
    def mute_unmute(self):
        global muted, song_volume
        if muted == 0:
            muted = 1
            mixer.music.set_volume(song_volume)
        else:
            muted = 0
            mixer.music.set_volume(0.0)

# -------------------------------------------------- Skin Selector -----------------------------------------------------
class Skin_Selector(Toplevel):
    def __init__(self, main_window, main_app):
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
        self.selected_color = self.main_app.current_skin

        self.color_label = Label(self, text=self.selected_color.upper(), bg='white', font=("arial", 12, "bold"))
        self.color_label.place(relx=0.5, rely=0.08, anchor=CENTER)

        self.skin_image = ImageResizer(f"assets/images/skins/{self.main_app.current_skin}.png", 100)
        self.skin_imager = Label(self, image=self.skin_image.image)
        self.skin_imager.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.next_image = ImageResizer(f"assets/images/prev-img.png", 25, TRUE)
        self.next_imager = Button(self, image=self.next_image.image, bg='white', activebackground='white',
                                  borderwidth=0, command= lambda: self.skin_controls('forward'))
        self.next_imager.place(relx=0.88, rely=0.5, anchor=CENTER)

        self.prev_image = ImageResizer(f"assets/images/prev-img.png", 25)
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

        self.skin_image = ImageResizer(f"assets/images/skins/{self.selected_color}.png", 100)
        self.skin_imager.config(image=self.skin_image.image)

        self.color_label.config(text=self.selected_color.upper())

# --------------------------------------------------- Apply Skin -------------------------------------------------------
    def apply_skin(self):
        self.main_app.update_skin(self.selected_color)
        self.main_app.current_skin = self.selected_color
        if self.main_app.play_state == 2:
            self.main_app.play_song_button.config(image=self.main_app.pause_song_image.image)
        else:
            self.main_app.play_song_button.config(image=self.main_app.play_song_image.image)

        self.destroy()

# ------------------------------------------------------- Run ----------------------------------------------------------
if __name__ == "__main__":
    app = IReminiscentPlayer()
