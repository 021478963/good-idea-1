import yt_dlp

options = {
    'format': 'bestaudio',
    'writethumbnail':'1',
    'paths': {"home":"\\output"}
}
with yt_dlp.YoutubeDL(options) as ydl:
    yt_dlp.YoutubeDL(options).download(["https://www.youtube.com/shorts/46pra8NwhzU"])