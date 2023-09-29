from googletrans import Translator, LANGUAGES

def translate_sinhala_to_english(text):
    translator = Translator()
    translated_text = translator.translate(text, src='si', dest='en')
    return translated_text.text
