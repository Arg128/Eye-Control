from deep_translator import GoogleTranslator
import tkinter as tk
#   from deep_translator import GoogleTranslator
from deep_translator.exceptions import TranslationNotFound
import sys
import threading


def translate_text(text: str, source_lang: str = "auto", target_lang: str = "en") -> str:
    """
    Translate text using GoogleTranslator from deep-translator.
    
    :param text: The text to translate.
    :param source_lang: Source language code or 'auto' for auto-detection.
    :param target_lang: Target language code.
    :return: Translated text.
    """
    if not text.strip():
        raise ValueError("Input text cannot be empty.")

    try:
        translator = GoogleTranslator(source=source_lang, target=target_lang)
        translated = translator.translate(text)
        return translated
    except TranslationNotFound:
        raise RuntimeError("Translation could not be found.")
    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")

if __name__ == "__main__":
    try:
        # Example usage
        original_text = input("Enter text to translate: ")
        target_language = input("Enter target language code (e.g., 'es', 'fr', 'de'): ")

        result = translate_text(original_text, target_lang=target_language)
        print(f"Translated text: {result}")

    except ValueError as ve:
        print(f"Input error: {ve}", file=sys.stderr)
    except RuntimeError as re:
        print(f"Translation error: {re}", file=sys.stderr)

class Dictionary():
    def __init__(self):
        self.target = 'en'
        self.objects = dict()
        self.objects2 = dict()
        self.translator = GoogleTranslator(source='es', target=self.target)
        self._cancel_flag = threading.Event()

    def change_language(self, source : str):
        self.target = source
        self.translator = GoogleTranslator(source='es', target=self.target)
    
    def add_object(self, object):
        text = None
        print(object)
        if isinstance(object, tk.Text):
            text = object.get("1.0", tk.END)
        elif isinstance(object, tk.Label):
            text = object.cget('text')
        else:
            text = object.cget('text')

        self.objects[object.winfo_id()] = text

        self.objects2[object.winfo_id()] = object

    def add_text(self, text):
        new_text = self.translator.translate(text)
        return new_text
    
    def _put_translations(self):
        try:
            for id in self.objects:
                if isinstance(self.objects2[id], tk.Text):
                    self.objects2[id].insert("1.0", self.objects[id])
                elif isinstance(self.objects2[id], tk.Label):
                    self.objects2[id].config(text=self.objects[id])
                else:
                    self.objects2[id].config(text=self.objects[id])

        except Exception as e:
            print(e)
    def translate(self, master):
        """         print("Whata unu")
        print(master)
        master.after(1000, self._translate) """

        self._translate()

    def _translate(self):      
        print(self.objects)  
        for id in self.objects:
            print("Traduciendo : ", self.objects[id])
            print("Idioma en el target : ", self.target)
            text = self.translator.translate(self.objects[id])
            self.objects[id] = text
            if self._cancel_flag.is_set():
                print("Porque hiciste eso ??¿¿")
                break
                """             if isinstance(object, tk.Text):
                text = object.get("1.0", tk.END)
                text = self.translator.translate(text)
                object.insert("1.0", text)
                continue """
    def translate_acync(self, master):
        self._cancel_flag.clear()
        process = threading.Thread(target=self._translate)
        process.start()
        while process.is_alive():
            #   self.master.update_idletasks()
            master.update()
        print("NUEVO DICT : ", self.objects)
        self._put_translations()
        #Resetar todo lo ya usado
        self.objects = dict()
        self.objects2 = dict()
        process.join()

    def cancel_translation(self):
        """Request cancellation of the running translation thread."""
        self._cancel_flag.set()
        

        