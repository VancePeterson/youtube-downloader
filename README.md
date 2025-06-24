🎥 YouTube Downloader GUI
A modern, dark-themed GUI application to download YouTube videos and audio using yt-dlp, with support for video previews, multiple formats (MP4, MP3, M4A), and a sleek Apple-style interface powered by customtkinter.

✨ Features
✅ Download videos as MP4 or audio as MP3

🖼️ Live preview of video thumbnail, title, uploader, and duration

📶 Real-time progress bar with status updates

🎨 Clean and modern dark-themed UI using customtkinter

🧠 Smart threading so the UI stays responsive during downloads

⚙️ Uses ffmpeg for merging and audio extraction

📸 UI Preview
![image](https://github.com/user-attachments/assets/cb17a067-449f-4999-ade2-8a7c16e55aab)





📦 Requirements
Install the required packages using pip:

bash
Copy
Edit
pip install yt-dlp imageio-ffmpeg pillow customtkinter
▶️ How to Run
Run the app using:

bash
Copy
Edit
python main.py
Once open:

Paste a valid YouTube URL.

Click "Load URL" to fetch video metadata.

Choose a format from the dropdown (MP4, MP3).

Hit "Download" to begin.

Downloads are saved to your system’s Downloads folder.

🔧 Under the Hood
Downloader engine: yt-dlp with format control and ffmpeg post-processing.

FFmpeg integration: Uses imageio-ffmpeg to locate ffmpeg executable.

Progress reporting: Parses yt-dlp hooks to update GUI in real-time.

Metadata fetching: Extracts title, thumbnail, uploader, and duration without downloading the file.

GUI Framework: customtkinter (a modern wrapper around tkinter) for a clean UI.

💡 Future Improvements
Download queue and history

Support for playlist downloads

Built-in ffmpeg bundling

Error reporting/logging window

⚠️ Disclaimer
This project is for educational use only. Download content only if you have the right to do so. Respect content creators and platform terms of service.

🛠️ License
MIT License © 2025

