import bs4
import requests
import yt_dlp

options_ytdlp = {
    'format': 'bestaudio',
    'paths': {"home": "\\output"},
    'quiet': '1'
}

def get_title(url):
  request = requests.get(url).text
  title = bs4.BeautifulSoup(request, "html.parser")
  title = title.title.string[:-10]
  # print(title)
  if len(title) > 15:
    new_title = title
  else:
    new_title = title[:15]
  file_name = "".join([i for i in new_title if i.isalpha()])
  # print(file_name)
  return [title, file_name]

def download_song(file_name, url):
  options_ytdlp['outtmpl'] = file_name
  with yt_dlp.YoutubeDL(options_ytdlp) as yt:
    yt.download(url)

if __name__ == "__main__":
  url = "https://www.youtube.com/watch?v=5CSFEaVz-k4"
  titles = get_title(url)
  # print(titles[1])
  # download_song(titles[1], url)