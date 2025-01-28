import time

# from tqdm import tqdm
# from prettytable import PrettyTable
import streamlit as st
from bs4 import BeautifulSoup
from bs4 import Tag
import requests
from g4f import Client

def parsing():

    for i in range(5):
        block: Tag = blocks[i]

        autor = block.find("a", {"class": "Link"}).get("href").split("/")[1]
        name = block.find("a", {"class": "Link"}).get("href").split("/")[2]
        star = block.find("a", {"href": f"/{autor}/{name}/stargazers"}).text.strip()
        fork = block.find("a", {"href": f"/{autor}/{name}/forks"}).text.strip()

        if autor and name and star and fork != None:
            readme = requests.get(f"https://raw.githubusercontent.com/{autor}/{name}/refs/heads/main/README.md")
            if readme.status_code != 200:
                readme = requests.get(f"https://raw.githubusercontent.com/{autor}/{name}/refs/heads/master/README.md")
                if readme.status_code != 200:
                    readme = requests.get(f"https://raw.githubusercontent.com/{autor}/{name}/refs/heads/dev/README.md")
                # if readme.status_code != 200:
                #     raise AttributeError("ВНИМАНИЕ! REAMDE ЛИБО ОТСУТСТВУЕТ, ЛИБО НЕ ПРАВИЛЬНО БЫЛ ВВЕДЁН URL")
            namestoauthors[name] = autor
            nametostars[name] = star
            nametoforks[name] = fork
            nametoreadme[name] = readme.text
        time.sleep(0.5)

        prg.progress(((i + 1) * 20), text="Производится парсинг...")
def postprocess():
    global prg

    del prg
    st.title("Топ 5 репозиториев.")
    for k, v, in namestoauthors.items():
        with st.expander(f"{v}/{k}"):
            sokroshenno = skorot(nametoreadme[k])
            st.write(f"{sokroshenno}\n- **Форков**: {nametoforks[k]}\n- **Звёзд**: {nametostars[k]}\n- [GitHub](https://github.com/{v}/{k})")
def skorot(readme: str) -> str:
    text = f"{readme}"

    response = gpt.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": f"Привет! В сообщение вложен текст файла README. Твоя задача вернуть мне ТОЛЬКО сокращённый до 3 коротеньких предложений текст. Используй MakrDown, что бы выделить основные аспекты. Не оставляй ссылки на источники. Текст должен быть на русском языке.\n{text}"}],
        web_search=False
    )

    return response.choices[0].message.content


gpt = Client()
r = requests.get("https://github.com/trending/css?since=daily")
soup = BeautifulSoup(r.text, "html.parser")
namestoauthors = {}
nametostars = {}
nametoforks = {}
nametoreadme = {}

blocks = soup.find_all("article", class_="Box-row")

prg = st.progress(0, text="Производится парсинг...")
btn = st.button("Запуск сего процесса.", type="primary")

if btn:
    parsing()
    postprocess()

#/php/php-src