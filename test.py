import requests
import bs4

request = requests.get(url = "https://youtu.be/5CSFEaVz-k4").text
title = bs4.BeautifulSoup(request, "html.parser")
title = title.title.string[:-10]
print(title)
file_name = "".join([title[i] for i in range(15) if title[i].isalpha()])
print(file_name)