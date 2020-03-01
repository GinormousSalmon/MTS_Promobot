import time
import threading
import speech_recognition as sr

r = sr.Recognizer()

queue = []


def listening():
    global queue
    while True:
        with sr.Microphone() as source:
            # print("Скажите что-нибудь")
            try:
                audio = r.listen(source, timeout=0.5, phrase_time_limit=2)
                queue.append(audio)
            except sr.WaitTimeoutError:
                continue


thread = threading.Thread(target=listening)
thread.daemon = True
thread.start()


while True:
    if len(queue) > 0:
        try:
            audio = queue.pop()
            # print("Распознавание...")
            t = time.time()
            print(r.recognize_google(audio, language="ru-RU"))
            print(time.time() - t)
        except sr.UnknownValueError:
            continue
            # print("Робот не расслышал фразу")
        except sr.RequestError as e:
            print("Ошибка сервиса; {0}".format(e))
