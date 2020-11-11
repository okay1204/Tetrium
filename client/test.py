import requests


content = requests.get('http://www.killyourself.com/')


print(dir(content))