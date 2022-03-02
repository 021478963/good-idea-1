import requests
import urllib.parse
import re

def get_url(search_term):
  encoded_search = urllib.parse.quote(search_term)
  request = requests.get("https://www.youtube.com/results?search_query=" + encoded_search).content
  request = str(request)
  index = request.find("videoId")
  id = request[index + 10:index + 21]
  return "https://www.youtube.com/watch?v=" + id

def is_url(search_term):
  regex2 = re.compile("(https:\/\/)?(www\.)?(youtu)\.?(be)(\.com)*(\/watch\?v=)[a-zA-Z0-9_]{11}")
  if regex2.match(search_term):
    return "https://www.youtube.com/watch?v=" + search_term[-10:]
  else:
    return get_url(search_term)