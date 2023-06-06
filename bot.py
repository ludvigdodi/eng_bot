import requests
import os
import random
from time import sleep
import sqlite3 as sq
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.environ.get("TOKEN")
ROOT_URL = f"https://api.telegram.org/bot{TOKEN}"

level = ''
sentences = []

def get_update(url, update_id):
    sleep(5)
    responce = requests.get(f"{url}/getUpdates?offset={update_id + 1}")
    return responce.json()

def send_message(chat_id, message_text, url):
    data = {"chat_id": chat_id, "text": message_text}
    responce = requests.post(f"{url}/sendMessage", data=data)
   
def get_start(chat_id, message_text, url):
    data = {"chat_id": chat_id, "text": "Привіт! 👋\n\nОбери рівень знання мови від 1 до 3.\n\n\n🌒  ТРОХИ ЗНАЮ  —  < 1 >\n\n🌓  ПОРЯДНО ЗНАЮ  —  < 2 >\n\n🌕  ДОБРЕ ЗНАЮ  —  < 3 >"}
    responce = requests.post(f"{url}/sendMessage", data=data)

def get_level(chat_id, message_text, url):
    data = {"chat_id": chat_id, "text": f'Чудово! 👏\n\nТвій рівень знання мови  —   {message_text} \n\nВведи слово і я спробую знайти речення з ним!'}
    responce = requests.post(f"{url}/sendMessage", data=data)

# Поиск cписка предложений по введенному уровню
def get_sentences():
    global level
    global sentences
   
    with sq.connect('sentences.db') as con:
        cur = con.cursor()

    if level == '1':
        db_sentences = cur.execute("SELECT * FROM sentences_1")
        sentences = [list(i) for i in db_sentences] 
    elif level == "2":
        db_sentences = cur.execute("SELECT * FROM sentences_2")
        sentences = [list(i) for i in db_sentences] 
    elif level == "3":
        db_sentences = cur.execute("SELECT * FROM sentences_3")
        sentences = [list(i) for i in db_sentences]
    return sentences

# Поиск предложений
def fill_matched_sentences(message):
    matched_sentences = []
    for s in get_sentences():
        for sentence in s:
            if message.lower() in sentence.lower():
                matched_sentences.append(sentence)
    return matched_sentences

# Составление ответа юзеру
def create_result_message(matched_sentences: list) -> str:
    result_message = ""
    if not matched_sentences:
        result_message = "Вибач!  Я не знайшов речення 😟\n\nТи точно ввів англійське слово? 🤔"
    if len(matched_sentences) == 1:
        result_message = matched_sentences[0]
    if len(matched_sentences) > 1:
         random.shuffle(matched_sentences)
         result_message = matched_sentences[0]
    return result_message

# Прослушиваем бота на сервере Телеги
def pooling():
    sleep(5)
    global level
    answered_update_id = 0
    
    while True:
        updates = get_update(ROOT_URL, answered_update_id)
        if updates.get("result"):
            update_id = updates.get("result")[0]["update_id"]
            if update_id != answered_update_id:
                chat_id = updates.get("result")[0]["message"]["chat"]["id"]
                message_text = updates.get("result")[0]["message"]["text"]
                if message_text == '/start':
                    get_start(chat_id, message_text, ROOT_URL)
                elif message_text in ['1', '2', '3']:                    
                    get_level(chat_id, message_text, ROOT_URL)
                    level = message_text        
                else:
                    message_text = create_result_message(fill_matched_sentences(message_text))
                    send_message(chat_id, message_text, ROOT_URL)
               
                answered_update_id = update_id

# Запуск бота
if __name__ == '__main__':
    pooling()
   