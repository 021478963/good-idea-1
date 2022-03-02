import requests
import urllib.parse

def get_url(search_term):
  encoded_search = urllib.parse.quote(search_term)
  request = requests.get("https://www.youtube.com/results?search_query=" + encoded_search).content
  request = str(request)
  index = request.find("videoId")
  id = request[index + 10:index + 21]
  return "https://www.youtube.com/watch?v=" + id