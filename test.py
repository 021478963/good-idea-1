import yt_dlp
import requests
import bs4

headers = requests.get("https://youtu.be/5CSFEaVz-k4").content

headers = bs4.BeautifulSoup(headers, "html.parser")
header = headers.title.string[:-10]
print(header)
header = "".join([i for i in header if i.isalpha()])
print(header)

options = {
    'format': 'bestaudio',
    'writethumbnail': '1',
    'paths': {"home": "\\output"},
    'outtmpl': "{file_name}".format(file_name = "hello")
}
with yt_dlp.YoutubeDL(options) as ydl:
    options['outtmpl'] = "{}".format(header)
    yt_dlp.YoutubeDL(options).download(["https://www.youtube.com/shorts/46pra8NwhzU"])