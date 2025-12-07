# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A desktop GUI application for downloading YouTube videos and audio using yt-dlp with a customtkinter interface.

## Commands

```bash
# Install dependencies (uses uv package manager)
uv sync

# Run the application
python main.py

# Build standalone executable (PyInstaller)
pyinstaller main.spec
```

## Architecture

This is a single-file application (`main.py`) with the following structure:

- **GUI Framework**: customtkinter (dark theme, 520x580 fixed window)
- **Download Engine**: yt-dlp with ffmpeg post-processing via imageio-ffmpeg
- **Threading**: Downloads and metadata fetching run in daemon threads to keep UI responsive
- **Output Location**: Downloads save to user's Downloads folder

### Key Functions

- `download_video()`: Handles yt-dlp download with format options (MP4, MP3, M4A)
- `fetch_preview()`: Extracts metadata (title, thumbnail, uploader, duration) without downloading
- `update_progress()`: Parses yt-dlp progress hooks to update the progress bar
- `main_gui()`: Builds the UI layout and wires up event handlers

### Format Configuration

Format options are defined in the `format_map` dictionary within `download_video()`. Each format specifies yt-dlp options including format string, merge format, and postprocessor settings.
