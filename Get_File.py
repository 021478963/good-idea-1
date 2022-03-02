import bs4
import requests
import yt_dlp

options_ytdlp = {
    'format': 'bestaudio',
    'paths': {"home": "\\output"},
}

def get_title(url):
  html_content = requests.get(url).content
  html_content = bs4.BeautifulSoup(html_content, "html.parser")
  title = html_content.title.string[:-10] # Youtube's titles always end in "- Youtube"
  print(title)
  file_name = "".join([i for i in title if i.isalpha()])
  print(file_name)
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