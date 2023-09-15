
import pathlib
import requests
from os.path import exists
from bs4 import BeautifulSoup
import lxml.html


listofurls = []
for pageno in range(1, 25):
    url = f'https://www.fool.com/earnings-call-transcripts/?page={pageno}'
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36'}
    response = requests.get(url, headers=headers, timeout=100)
    page = response.text
    soup = BeautifulSoup(page, "lxml")
    for a in soup.find(class_="page").find_all(lambda x: x.name == 'a' and x.get('class') == ['text-gray-1100']):
        listofurls.append('https://www.fool.com'+str(a['href']))
        if len(listofurls) % 10 == 0:
            print(f"{len(listofurls)}", end=" ", flush=True)

print("Links downloaded", flush=True)

for idx, url in enumerate(listofurls):
    path = pathlib.PurePath(url)
    filename = 'out-text-analysis/' + path.name + '.txt'
    if exists(filename):
        print("Hello!")
        continue

    response = requests.get(url, headers=headers, timeout=100)
    page = response.text
    soup = BeautifulSoup(page, features="html.parser")

    for script in soup(["script", "style"]):
        script.extract()
    
    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())

    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))

    text = '\n'.join(chunk for chunk in chunks if chunk)
    textClean = '\n'.join(text.split("\n")[308:])
    textFullClean = textClean.split("All earnings call transcripts")[0]


    with open(filename, "w") as file:
            file.write(str(textFullClean))

    print(idx)

    print(filename, flush=True)
