import random
from google_trans_new import google_translator
from google_trans_new.constant import LANGUAGES

translator = google_translator()
def translate(txt, lang):
    return translator.translate(txt, lang_tgt=lang)

while True:
    txt = input(">")
    lang = random.choice(list(LANGUAGES))
    print("lang: " + LANGUAGES[lang])
    print(translate(txt, lang))

# Ideas:
# 1. Waldo: kr -> random -> kr
# 2. few well-known langs
# 3. complete random languages

# Note:
# let's try using webhooks