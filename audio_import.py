# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "yt-dlp==2025.3.31",
# ]
# ///
import yt_dlp
import os
import sys

video_url = sys.argv[1]
video_artist = sys.argv[2].replace(' ', '')
video_title = sys.argv[3].replace(' ', '')

options = {
    'quiet': True, # Suppress the output.
    'no_warnings': True, # Suppress warnings.
    'outtmpl': f"{video_artist}-{video_title}.%(ext)s",
    'format': 'm4a/bestaudio/best',
    'ffmpeg_location':os.path.realpath('/usr/local/bin/ffmpeg'),
    'postprocessors': [
        {
            'key': 'FFmpegExtractAudio',  # Extract audio using ffmpeg.
            'preferredcodec': 'm4a',
        }
    ]
}

with yt_dlp.YoutubeDL(options) as ydl:
    ydl.download([video_url])


## uv run audio_import.py https://www.youtube.com/watch?v=LdZg-zgzWnk "The Carpenters" "I Heard The Bells On Christmas Day"
