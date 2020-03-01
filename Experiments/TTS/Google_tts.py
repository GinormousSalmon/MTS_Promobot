import os
import re
from pygame import mixer
import datetime
import time
from gtts import gTTS

# Для того чтобы не возникало коллизий при удалении mp3 файлов
# заведем переменную mp3_name_old в которой будем хранить имя предыдущего mp3 файла
mp3_name_old = '111'
mp3_name = "1.mp3"

# Инициализируем звуковое устройство
mixer.init()

ss = "The pygame module is required to play the mp3 file received from Google"
t = time.time()
# Делим прочитанные строки на отдельные предложения
split_regex = re.compile(r'[.|!|?|…]')
sentences = filter(lambda t: t, [t.strip() for t in split_regex.split(ss)])

# Перебираем массив с предложениями
for x in sentences:
    print(x)
    if x != "":
        print(x)
        # Эта строка отправляет предложение которое нужно озвучить гуглу
        tts = gTTS(text=x)
        # Получаем от гугла озвученное предложение в виде mp3 файла
        tts.save(mp3_name)
        # Проигрываем полученный mp3 файл
        mixer.music.load(mp3_name)
        print(time.time() - t)
        mixer.music.play()
        while mixer.music.get_busy():
            time.sleep(0.1)
        # Если предыдущий mp3 файл существует удаляем его
        # чтобы не захламлять папку с приложением кучей mp3 файлов
        if os.path.exists(mp3_name_old) and (mp3_name_old != "1.mp3"):
            os.remove(mp3_name_old)
        mp3_name_old = mp3_name
        # Формируем имя mp3 файла куда будет сохраняться озвученный текст текущего предложения
        # В качестве имени файла используем текущие дату и время
        now_time = datetime.datetime.now()
        mp3_name = now_time.strftime("%d%m%Y%I%M%S") + ".mp3"

# Устанвливаем текущим файлом 1.mp3 и закрываем звуковое устройство
# Это нужно чтобы мы могли удалить предыдущий mp3 файл без колизий
mixer.music.load('1.mp3')
mixer.stop()
mixer.quit()

# Удаляем последний предыдущий mp3 файл
if os.path.exists(mp3_name_old):
    os.remove(mp3_name_old)
