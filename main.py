import os
import re
import time
import glob
import base64
import threading
import tkinter
from pathlib import Path
from urllib.request import urlopen
from io import BytesIO

import yt_dlp
import imageio_ffmpeg
from PIL import Image
import customtkinter as ctk
from tkinter import messagebox


def is_valid_youtube_url(url: str) -> bool:
    pattern = re.compile(r"^(https?://)?(www\.)?(youtube\.com|youtu\.be)/")
    return bool(pattern.match(url))


# GUI download logic
def download_video(url, format_choice, status_label, progress_bar, download_btn):
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
    finally:
        download_btn.configure(state="normal", text="Download")

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
            status_label.configure(text=f"{match.group(1)}%", text_color="orange")
        else:
            status_label.configure(text="Unable to parse progress", text_color="red")

    elif d['status'] == 'finished':
        # Simulate merging progress
        status_label.configure(text="Merging...", text_color="yellow")
        for i in range(10):
            time.sleep(0.1)
            progress_bar.set(0.9 + 0.01 * i)
        status_label.configure(text="Download complete!", text_color="green")
        progress_bar.set(1.0)

# Fetch metadata and preview
def fetch_preview(url, title_label, thumb_label, meta_label, preview_btn, app):
    try:
        ydl_opts = {'quiet': True, 'skip_download': True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

        title = info.get("title", "")
        uploader = info.get('uploader', '')
        duration = round(info.get('duration', 0)/60, 1)
        thumb_url = info.get("thumbnail")

        # Fetch and process image in background thread, convert to base64 PNG
        img_data = None
        if thumb_url:
            raw_data = urlopen(thumb_url).read()
            img = Image.open(BytesIO(raw_data)).resize((320, 180))
            # Convert to PNG bytes for tkinter.PhotoImage
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            img_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        def update_ui():
            title_label.configure(text=title)
            meta_label.configure(text=f"{uploader} • {duration} min")

            if img_data:
                # Use tkinter's native PhotoImage with base64 data
                photo = tkinter.PhotoImage(data=img_data)
                thumb_label.configure(image=photo)
                thumb_label.image = photo
            preview_btn.configure(state="normal", text="Load URL")

        app.after(0, update_ui)
    except Exception as e:
        app.after(0, lambda: messagebox.showerror("Preview Error", f"Could not load preview.\n{e}"))
        app.after(0, lambda: preview_btn.configure(state="normal", text="Load URL"))

# Start threaded download
def start_download(entry, format_var, status_label, progress_bar, download_btn):
    url = entry.get().strip()
    if not url:
        messagebox.showwarning("Missing URL", "Please enter a YouTube URL.")
        return
    if not is_valid_youtube_url(url):
        messagebox.showerror("Invalid URL", "Please enter a valid YouTube URL.")
        return
    # Show and reset progress bar
    progress_bar.set(0)
    progress_bar.pack(pady=5)
    status_label.configure(text="")
    status_label.pack(pady=5)
    download_btn.configure(state="disabled", text="Downloading...")
    threading.Thread(
        target=download_video,
        args=(url, format_var.get(), status_label, progress_bar, download_btn),
        daemon=True,
    ).start()


def start_fetch_preview(entry, title_label, thumb_label, meta_label, preview_btn, app, progress_bar, status_label):
    url = entry.get().strip()
    if not url:
        messagebox.showwarning("Missing URL", "Please enter a YouTube URL.")
        return
    if not is_valid_youtube_url(url):
        messagebox.showerror("Invalid URL", "Please enter a valid YouTube URL.")
        return
    # Hide progress bar when loading new URL
    progress_bar.pack_forget()
    status_label.pack_forget()
    preview_btn.configure(state="disabled", text="Loading...")
    threading.Thread(
        target=fetch_preview,
        args=(url, title_label, thumb_label, meta_label, preview_btn, app),
        daemon=True,
    ).start()

# Main UI
def main_gui():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = ctk.CTk()
    app.title("YouTube Downloader")
    app.geometry("520x580")
    app.resizable(False, False)

    # Set window icon
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    if os.path.exists(icon_path):
        app.iconbitmap(icon_path)

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

    preview_btn = ctk.CTkButton(app, text="Load URL", font=apple_font_body)
    preview_btn.pack(pady=5)

    format_var = ctk.StringVar(value="Audio (MP3)")
    format_menu = ctk.CTkOptionMenu(app, values=["Audio (MP3)", "Video (MP4)"], variable=format_var, font=apple_font_body)
    format_menu.pack(pady=10)

    progress_bar = ctk.CTkProgressBar(app, width=460)
    progress_bar.set(0)

    status_label = ctk.CTkLabel(app, text="", font=apple_font_body)

    download_btn = ctk.CTkButton(app, text="Download", font=apple_font_body)
    download_btn.pack(pady=10)

    # Progress bar and status hidden initially
    # They will be shown when download starts

    preview_btn.configure(command=lambda btn=preview_btn: start_fetch_preview(url_entry, title_label, thumb_label, meta_label, btn, app, progress_bar, status_label))
    download_btn.configure(command=lambda btn=download_btn: start_download(url_entry, format_var, status_label, progress_bar, btn))

    app.mainloop()

if __name__ == "__main__":
    main_gui()
