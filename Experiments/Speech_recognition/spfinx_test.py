import os
from pocketsphinx import LiveSpeech, get_model_path
import time

model_path = get_model_path()

speech = LiveSpeech(
    hmm=os.path.join(model_path, 'zero_ru.cd_cont_4000'),
    lm=os.path.join(model_path, 'ru.lm'),
    dic=os.path.join(model_path, 'ru.dic')
)

print("Say something!")
for phrase in speech:
    print(phrase)
