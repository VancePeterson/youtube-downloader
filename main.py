import os
import time
import glob
import threading
from pathlib import Path
from urllib.request import urlopen
from io import BytesIO

import yt_dlp
import imageio_ffmpeg
from PIL import Image
import customtkinter as ctk
from tkinter import messagebox
from customtkinter import CTkImage

import re

# GUI download logic
def download_video(url, format_choice, status_label, progress_bar):
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
    downloads_path = str(Path.home() / "Downloads")

    format_map = {
        "Video (MP4)": {
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
            'postprocessor_args': ['-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k']
        },
        "Audio (M4A)": {
            'format': 'bestaudio',
            'merge_output_format': 'm4a',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
                'preferredquality': '192'
            }]
        },
        "Audio (MP3)": {
            'format': 'bestaudio',
            'merge_output_format': 'mp3',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }]
        }
    }

    opts = format_map.get(format_choice, format_map["Video (MP4)"])

    ydl_opts = {
        'ffmpeg_location': ffmpeg_path,
        'format': opts['format'],
        'outtmpl': os.path.join(downloads_path, '%(title)s.%(ext)s'),
        'no_mtime': True,
        'progress_hooks': [lambda d: update_progress(d, status_label, progress_bar)],
        'quiet': True,
    }

    if 'postprocessors' in opts:
        ydl_opts['postprocessors'] = opts['postprocessors']
    if 'postprocessor_args' in opts:
        ydl_opts['postprocessor_args'] = opts['postprocessor_args']
    if 'merge_output_format' in opts:
        ydl_opts['merge_output_format'] = opts['merge_output_format']

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        status_label.configure(text="✅ Download complete!", text_color="green")
        progress_bar.set(1)
    except Exception as e:
        status_label.configure(text="❌ Download failed", text_color="red")
        messagebox.showerror("Error", str(e))

# Strip ansi
def strip_ansi(text):
    return re.sub(r'\x1b\\[[0-9;]*m', '', text)

# Update progress bar
def update_progress(d, status_label, progress_bar):
    if d['status'] == 'downloading':
        percent_str = d.get('_percent_str', '0%')
        match = re.search(r'(\d{1,2}\.\d)%', percent_str)
        if match:
            percent = float(match.group(1)) / 100
            progress_bar.set(percent)
            status_label.configure(text=f"⬇️ {match.group(1)}%", text_color="orange")
        else:
            status_label.configure(text="⚠️ Unable to parse progress", text_color="red")

    elif d['status'] == 'finished':
        # Simulate merging progress
        status_label.configure(text="🛠️ Merging...", text_color="yellow")
        for i in range(10):
            time.sleep(0.1)
            progress_bar.set(0.9 + 0.01 * i)
        status_label.configure(text="✅ Download complete!", text_color="green")
        progress_bar.set(1.0)

# Fetch metadata and preview
def fetch_preview(url, title_label, thumb_label, meta_label):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        title_label.configure(text=info.get("title", ""))
        meta_label.configure(text=f"{info.get('uploader', '')} • {round(info.get('duration', 0)/60, 1)} min")

        thumb_url = info.get("thumbnail")
        if thumb_url:
            raw_data = urlopen(thumb_url).read()
            img = Image.open(BytesIO(raw_data)).resize((320, 180))
            thumb = CTkImage(light_image=img, size=(320, 180))
            thumb_label.configure(image=thumb)
            thumb_label.image = thumb
    except Exception as e:
        messagebox.showerror("Preview Error", f"Could not load preview.\n{e}")

# Start threaded download
def start_download(entry, format_var, status_label, progress_bar):
    url = entry.get().strip()
    if not url:
        messagebox.showwarning("Missing URL", "Please enter a YouTube URL.")
        return
    progress_bar.set(0)
    threading.Thread(target=download_video, args=(url, format_var.get(), status_label, progress_bar), daemon=True).start()

# Main UI
def main_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = ctk.CTk()
    app.title("YouTube Downloader")
    app.geometry("520x580")
    app.resizable(False, False)

    apple_font_title = ctk.CTkFont(family="Helvetica Neue", size=22, weight="bold")
    apple_font_body = ctk.CTkFont(family="Helvetica Neue", size=14)
    apple_font_small = ctk.CTkFont(family="Helvetica Neue", size=12)

    ctk.CTkLabel(app, text="YouTube Downloader", font=apple_font_title).pack(pady=12)

    url_entry = ctk.CTkEntry(app, width=460, placeholder_text="Paste YouTube URL here", font=apple_font_body)
    url_entry.pack(pady=10)

    # Preview Elements
    thumb_label = ctk.CTkLabel(app, text="")
    thumb_label.pack()

    title_label = ctk.CTkLabel(app, text="", font=apple_font_body, wraplength=480)
    title_label.pack(pady=5)

    meta_label = ctk.CTkLabel(app, text="", font=apple_font_small)
    meta_label.pack()

    preview_btn = ctk.CTkButton(app, text="Load URL", font=apple_font_body, command=lambda: fetch_preview(url_entry.get(), title_label, thumb_label, meta_label))
    preview_btn.pack(pady=5)

    format_var = ctk.StringVar(value="Video (MP4)")
    format_menu = ctk.CTkOptionMenu(app, values=["Video (MP4)", "Audio (MP3)"], variable=format_var, font=apple_font_body)
    format_menu.pack(pady=10)

    download_btn = ctk.CTkButton(app, text="Download", font=apple_font_body, command=lambda: start_download(url_entry, format_var, status_label, progress_bar))
    download_btn.pack(pady=10)

    progress_bar = ctk.CTkProgressBar(app, width=460)
    progress_bar.set(0)
    progress_bar.pack(pady=5)

    status_label = ctk.CTkLabel(app, text="", font=apple_font_body)
    status_label.pack(pady=5)

    app.mainloop()

if __name__ == "__main__":
    main_gui()
