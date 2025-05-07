# ------------------------------------------------------- Imports ------------------------------------------------------
from tkinter import * # Tkinter
from tkinter import ttk, filedialog, messagebox # Tkinter
from mutagen import File as MutagenFile # Mutagen File
from mutagen.id3 import ID3 # Mutagen Tags
from mutagen.mp3 import MP3 # Mutagen Tags
from mutagen.flac import FLAC # Mutagen Tags
from mutagen.mp4 import MP4 # Mutagen Tags
import json # JSON
import os # OS
from pathlib import Path
from math import ceil # Math
from custom_resizer import CustomResizer # Custom Image Resizer
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide" # PyGame Prompt Hide
import pygame.mixer as mixer # Mixer
from musicbrainz_api import MusicBrainzAPI # MusicBrainz API
import requests # Requests
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

        self.skins = {
            "black": { "main_color": "#333333", "text": "white", "buttons": "#ffffff", "main_button_color": "#e14354",
                "playback_color": "#d13746", "play_pause_color": "#c02a38", 'screen_color': '#ADD8E6' },
            "blue": {"main_color": "#0096c1", "text": "white", "buttons": "#91948d", "main_button_color": "#eeeee8",
                "playback_color": "#e8e8e1", "play_pause_color": "#e2e2da", 'screen_color': '#ADD8E6' },
            "cyan": { "main_color": "#69bdbe", "text": "white", "buttons": "#91948d", "main_button_color": "#eeede8",
                "playback_color": "#e7e7e0", "play_pause_color": "#e2e2da", 'screen_color': '#ADD8E6' },
            "green": { "main_color": "#8bc932", "text": "white", "buttons": "#91948d", "main_button_color": "#edece7",
                "playback_color": "#e8e8e1", "play_pause_color": "#e2e2da", 'screen_color': '#ADD8E6' },
            "grey": { "main_color": "#6b6a6d", "text": "white", "buttons": "#ffffff", "main_button_color": "#242424",
                "playback_color": "#242424", "play_pause_color": "#242424", 'screen_color': '#ADD8E6' },
            "magenta": { "main_color": "#e54556", "text": "white", "buttons": "#ffffff", "main_button_color": "#242424",
                "playback_color": "#242424", "play_pause_color": "#242424", 'screen_color': '#ADD8E6' },
            "pink": { "main_color": "#d3248c", "text": "white", "buttons": "#91948d", "main_button_color": "#eeeee8",
                "playback_color": "#e8e7e1", "play_pause_color": "#e2e2da", 'screen_color': '#ADD8E6' },
            "red": { "main_color": "#e54557", "text": "white", "buttons": "#91948d", "main_button_color": "#eeede8",
                "playback_color": "#e7e6e0", "play_pause_color": "#e2e2db", 'screen_color': '#ADD8E6' },
            "white": { "main_color": "#deddd9", "text": "white", "buttons": "#91948d", "main_button_color": "#eeeee8",
                "playback_color": "#e7e6e0", "play_pause_color": "#e1e1da", 'screen_color': '#ADD8E6' }
        }

        # Initialize Mixer
        mixer.init()
        self.main_folder_path = None
        self.play_state = 0 # Play State: {0: First Time - Paused, 1: Loaded - Paused, 2: Play, 3: Paused}
        self.resume_time = None
        self.current_skin = 'blue'
        self.playback_control_color = "direction-p"
        self.album_art_image = CustomResizer(mode='resize_image', image_location="./assets/images/default_album_art.png",
                                            image_wd=50)
        self.skins_screen_bg = "#f4fdfd"

        # Main Canvas
        self.main_canvas = Canvas(self.windows, width=width, height=height)
        self.main_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)

        self.main_skin_image = CustomResizer(mode='resize_image', image_location=f"assets/images/skins/{self.current_skin}.png",
                                            image_wd=186)
        self.main_skin_imager = Label(self.main_canvas, image=self.main_skin_image.image)
        self.main_skin_imager.place(relx=0.5, rely=0.5, anchor="center")

        self.now_playing_label = Label(self.main_canvas, text="Now Playing", font=('arial', 7, 'normal'), anchor=CENTER,
                                       background='#ADD8E6')
        self.now_playing_label.place(relx=0.5, rely=0.0785, anchor=CENTER, relwidth=0.9)

        self.now_playing_logo = Label(self.main_canvas, text="▶️", font=('arial', 7, 'normal'), foreground='#0065BD',
                                      background='#ADD8E6')
        self.now_playing_logo.place(relx=0.12, rely=0.0785, anchor=CENTER)

        self.album_art_label = Label(self.main_canvas, image=self.album_art_image.image)
        self.album_art_label.place(relx=0.25, rely=0.2, anchor=CENTER)

        # Song Name and Artist
        self.song_name_label = Label(self.main_canvas, bg=self.skins_screen_bg, font=("arial", 8, "bold"))
        self.song_name_label.place(relx=0.4, rely=0.17, anchor=W)
        self.song_artist_label = Label(self.main_canvas, bg=self.skins_screen_bg, font=("arial", 7, "normal"))
        self.song_artist_label.place(relx=0.4, rely=0.22, anchor=W)

        # Song Duration and Progressbar
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Horizontal.TProgressbar", thickness=3, troughcolor='#ADD8E6', bordercolor='#ADD8E6',
                        background='#0099FF', lightcolor='#0099FF', darkcolor='#0099FF')
        self.song_progressbar = ttk.Progressbar(self.main_canvas, style="Horizontal.TProgressbar", length=160,
                                                mode="determinate", orient=HORIZONTAL, value=0)
        self.song_progressbar.place(relx=0.507, rely=0.34, anchor=CENTER)
        self.current_duration_label = Label(self.main_canvas, bg=self.skins_screen_bg, text="00:00",
                                            font=("arial", 6, "normal"))
        self.current_duration_label.place(relx=0.2, rely=0.37, anchor=E)

        self.total_duration_label = Label(self.main_canvas, bg=self.skins_screen_bg, text="00:00",
                                          font=("arial", 6, "normal"))
        self.total_duration_label.place(relx=0.8, rely=0.37, anchor=W)

        # Buttons
        # Music Controls
        select_music_folder_image = CustomResizer('resize_image', image_location="assets/images/menu.png",
        image_wd=28)
        self.select_music_folder_button = Button(self.main_canvas, bg=self.skins[self.current_skin]["main_button_color"],
                                                activebackground = self.skins[self.current_skin]["main_button_color"],
                                                 image=select_music_folder_image.image, borderwidth=0,
                                                command=self.select_song_folder, highlightthickness=0)
        self.select_music_folder_button.place(relx=0.5, rely=0.53, anchor=CENTER)

        previous_song_image = CustomResizer('resize_image', image_location=f"assets/images/{self.playback_control_color}.png",
                                           image_wd=12)
        self.previous_song_button = Button(self.main_canvas, bg="#e8e8e1", image=previous_song_image.image,
                                           highlightthickness=0, borderwidth=0, activebackground="#e8e8e1")
        self.previous_song_button.place(relx=0.21, rely=0.67, anchor=CENTER)
        self.previous_song_button.bind("<ButtonPress-1>", lambda event: self.slider_pressed("backward"))
        self.previous_song_button.bind("<ButtonRelease-1>", lambda event: self.handle_release("backward"))

        self.play_song_image = CustomResizer('resize_image', image_location="assets/images/play.png", image_wd=12)
        self.pause_song_image = CustomResizer('resize_image', "assets/images/pause.png", 12)
        self.play_song_button = Button(self.main_canvas, bg="#e8e8e1", image=self.play_song_image.image, command=self.play_song,
                                       highlightthickness=0, borderwidth=0, activebackground="#e8e8e1")
        self.play_song_button.place(relx=0.5, rely=0.81, anchor=CENTER)

        next_song_image = CustomResizer('resize_image',f"assets/images/{self.playback_control_color}.png",
                                       12, True)
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
            return messagebox.showerror("Error!!", "No songs in the selected folder.")
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

                        album_art_image = self.get_song_thumbnail(tags, track_name, track_artist)
                        album_art_image = album_art_image.image

                        track_details = {
                            'track_name': track_name,
                            'track_path': str(path),
                            'track_artist': track_artist,
                            'track_album': track_album,
                            'track_extension': track_extension,
                            'track_length': track_length,
                            'album_art_image': album_art_image
                        }
                        self.main_playlist.append(track_details)
                except Exception as e:
                    return messagebox.showerror("Error!!", f"Error: {str(e)}", parent=self)

        self.main_playlist = sorted(self.main_playlist, key=lambda x: x['track_name'])

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
        self.play_song_button.configure(image=self.play_song_image.image)
        song_path = self.current_track_info['track_path']
        current_song_length = self.current_track_info['track_length']
        song_mins = int(current_song_length / 60)
        song_secs = int(current_song_length % 60)
        minutes = seconds = 0
        self.current_duration_label.configure(text="{:02d}:{:02d}".format(minutes, seconds))
        self.total_duration_label.configure(text="{:02d}:{:02d}".format(song_mins, song_secs))
        self.song_progressbar.config(maximum=current_song_length)
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

# ----------------------------------------------- Song Thumbnails ------------------------------------------------------
    def get_song_thumbnail(self, tags, song_namer, song_artiste):
        sasa_joined = f"{song_namer} {song_artiste}"
        image_file_name = ''.join(letter for letter in sasa_joined if letter.isalnum())
        image_location = f"./assets/images/album_art/{image_file_name}.png"
        try:
            album_art_image = CustomResizer('resize_image', image_location=image_location, image_wd=50)
        except (TclError, FileNotFoundError) as e:
            print(f'File Not Found Locally:{e}')
            try:
                pict = tags.get("APIC:").data
            except AttributeError as e:
                print(f'Song Tag Error:{e}\n Downloading Album Art!!')
                album_art_image = self.download_album_art(song_namer, song_artiste)
            else:
                print(f'Selecting Album Art from Tag')
                CustomResizer('save_tag_pic', image_location=image_location, pict=pict)
                album_art_image = CustomResizer('resize_image', image_location=image_location, image_wd=40)
        return album_art_image

# ---------------------------------------------- Download Album Art-----------------------------------------------------
    def download_album_art(self, song_namer, song_artiste):
        try:
            api = MusicBrainzAPI()
            response = api.search_releases(f'release:{song_namer} AND artist:{song_artiste}')
            album_art_url = response["images"][0]["thumbnails"]["small"]
            sasa_joined = f"{song_namer} {song_artiste}"
            image_file_name = ''.join(letter for letter in sasa_joined if letter.isalnum())
            image_location = f"./assets/images/album_art/{image_file_name}.png"
            img_data = requests.get(album_art_url).content
            with open(image_location, 'wb') as handler:
                handler.write(img_data)
            print(image_location)
        except Exception as e:
            print(f'Error downloading image: {e}')
            image_location = "./assets/images/default_album_art.png"

        album_art_image = CustomResizer('resize_image', image_location=image_location, image_wd=50)
        return album_art_image

# -------------------------------------------------- Music Info --------------------------------------------------------
    def update_music_info(self):
        song_title = CustomResizer(mode='resize_word', word=self.current_track_info['track_name'], font_name='arial',
                                  font_size=8).word
        song_artist = CustomResizer(mode='resize_word', word=self.current_track_info['track_artist'], font_name='arial',
                                  font_size=8).word
        self.song_name_label.configure(text=song_title)
        self.song_artist_label.configure(text=song_artist)
        self.album_art_label.config(image=self.current_track_info['album_art_image'])

# ------------------------------------------------ Song Progress -------------------------------------------------------
    def update_progressbar(self):
        global status
        current_song_length = self.current_track_info['track_length']
        if self.resume_time:
            current_time = round((mixer.music.get_pos() / 1000) + self.resume_time)
        else:
            current_time = round(mixer.music.get_pos() / 1000)
        self.song_progressbar.config(value=current_time)
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
        if seek_d == "forward":
            self.current_time = self.current_time + 1
        else:
            self.current_time = self.current_time - 1
        minutes, seconds = divmod(self.current_time, 60)
        self.current_duration_label.configure(text=f"{minutes:02d}:{seconds:02d}")

        if ceil(self.current_time) == ceil(self.current_track_info['track_length']) - 1:
            self.next_song()
        elif ceil(self.current_time) < 1:
            self.resume_time = 0
            self.play_song()

        self.resume_time = self.current_time

        self.after_id = self.windows.after(100, lambda: self.slider_pressed_loop(seek_d))

# --------------------------------------------------- Seek Stop --------------------------------------------------------
    def slider_released(self, event=None):
        global current_song_length

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
            'current_track_title': self.current_track_info['track_name'],
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
        self.main_skin_image = CustomResizer('resize_image', f"assets/images/skins/{selected_skin}.png", 186)
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

        self.select_music_folder_image = CustomResizer('resize_image', f"assets/images/{self.menu_color}.png",
                                                      28)
        self.select_music_folder_button.config(image=self.select_music_folder_image.image,
                                               bg=self.skins[selected_skin]["main_button_color"],
                                               activebackground=self.skins[selected_skin]["main_button_color"])

        self.previous_song_image = CustomResizer('resize_image',
                                        f"assets/images/{self.playback_control_color}.png", 12)
        self.previous_song_button.config(image=self.previous_song_image.image, bg=self.skins[selected_skin]["playback_color"],
                                         activebackground=self.skins[selected_skin]["playback_color"])

        self.play_song_image = CustomResizer('resize_image', f"assets/images/{self.play_control_color}.png",
                                            12)
        self.pause_song_image = CustomResizer('resize_image', f"assets/images/{self.pause_control_color}.png",
                                             12)
        self.play_song_button.config(image=self.play_song_image.image, bg=self.skins[selected_skin]["play_pause_color"],
                                         activebackground=self.skins[selected_skin]["play_pause_color"])

        self.next_song_image = CustomResizer('resize_image', f"assets/images/{self.playback_control_color}.png",
                                            12, True)
        self.next_song_button.config(image=self.next_song_image.image, bg=self.skins[selected_skin]["playback_color"],
                                         activebackground=self.skins[selected_skin]["playback_color"])

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
        self.skins = self.main_app.skins

        self.color_label = Label(self, text=self.selected_color.upper(), bg='white', font=("arial", 12, "bold"))
        self.color_label.place(relx=0.5, rely=0.08, anchor=CENTER)

        self.skin_image = CustomResizer('resize_image', f"assets/images/skins/{self.main_app.current_skin}.png",
                                       100)
        self.skin_imager = Label(self, image=self.skin_image.image)
        self.skin_imager.place(relx=0.5, rely=0.5, anchor=CENTER)

        self.next_image = CustomResizer('resize_image', image_location=f"assets/images/prev-img.png",
                                       image_wd=25, flipper=TRUE)
        self.next_imager = Button(self, image=self.next_image.image, bg='white', activebackground='white',
                                  borderwidth=0, command= lambda: self.skin_controls('forward'))
        self.next_imager.place(relx=0.88, rely=0.5, anchor=CENTER)

        self.prev_image = CustomResizer('resize_image', f"assets/images/prev-img.png", 25)
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
        all_skin_colors = list(self.skins.keys())
        index = all_skin_colors.index(self.selected_color)
        if direc == 'forward':
            index = min(index + 1, len(all_skin_colors) - 1)
        else:
            index = max(index - 1, 0)

        self.selected_color = all_skin_colors[index]

        self.skin_image = CustomResizer('resize_image', f"assets/images/skins/{self.selected_color}.png",
                                       100)
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