import requests

url = 'https://github.com/CosineCloud/Anony2.0v/tree/main/Anonymous_Chats'
response = requests.get(url)

with open('file.ext', 'wb') as f:
    f.write(response.content)

print("File downloaded!")
