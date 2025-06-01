import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import textwrap
from pathlib import Path
import spacy # python -m spacy download de_core_news_sm

""" so word groups would be:
        Verbs: VERB, AUX;
        Adjectives: ADJ, ADV;
        Nouns: NOUN, PROPN, der, die, das;"""

class helper:  
    languages = {
        "uk": "Ukrainian",
        "en": "English",
        "es": "Spanish",
        "fr": "French",
        "tr": "Turkish",
        "pt": "Portuguese",
        "it": "Italian",
        "ro": "Romanian",
        "hu": "Hungarian",
        "pl": "Polish",
        "el": "Greek",
        "nl": "Dutch",
        "cs": "Czech",
        "sv": "Swedish",
        "da": "Danish",
        "ja": "Japanese",
        "ca": "Catalan",
        "fi": "Finnish",
        "no": "Norwegian",
        "eu": "Basque",
        "sr": "Serbian",
        "mk": "Macedonian",
        "sl": "Slovenian",
        "sk": "Slovak",
        "bs": "Bosnian",
        "hr": "Croatian",
        "bg": "Bulgarian",
    }
    # cool colours: https://coolors.co/palette/cdb4db-ffc8dd-ffafcc-bde0fe-a2d2ff
    colors = {
        "orange":        "#F67B1F",
        "shaded_orange": "#E07200",
        "green":         "#4E8F31",
        "shaded_green":  "#2E6A10",
        "blue":          "#3B7D9F",
        "shaded_blue":   "#165B75",
        "red":           "#CF2025",
        "shaded_red":    "#B40A10",
        # here are colors for the flash cards
        "yellow":        "#FCDA7F",
        "cyan":          "#A8A1FF",
    }

    @classmethod
    def split_to_rows(self, text, max_length=60):
        """Split a string into two rows if its length exceeds max_length."""
        if len(text) > max_length:
            wrapped_lines = textwrap.wrap(text, max_length)
            return "\n".join(wrapped_lines[:])
        return text  
   

class Netzverb: 
    # base_url = "https://www.verbformen.de/?w="
    base_url = "https://www.verben.de/?w="
    noun_url = "https://www.verben.de/substantive/?w=" # + word + .htm
    conj_url = "https://www.verben.de/konjunktionen/?w="
    # "https://www.verben.de/substantive/?w="

    nouns = ["der", "die", "das", "NOUN", "PROPN"]
    verbs = ["VERB", "AUX"]
    adjectives = ["ADJ", "ADV"]

    @classmethod
    def get_lang_code(self, lang_name):
        for code, name in helper.languages.items():
            if name == lang_name:
                return code
        return "en"  # Return lang_name if no match is found

    @classmethod
    def get_html_response(self, word):
        request_url = f"{self.base_url}{word}"
        return self._fetch_response(request_url)

    @classmethod
    def get_noun_html_response(self, word):
        request_url = f"{self.noun_url}{word}"
        return self._fetch_response(request_url)
    
    @classmethod
    def get_conj_html_response(self, word):
        request_url = f"{self.conj_url}{word}"
        return self._fetch_response(request_url)

    @classmethod
    def _fetch_response(self, request_url):
        try:
            response = requests.get(request_url)
            response.raise_for_status()  # Raise HTTPError for bad responses
            time.sleep(2)
            return BeautifulSoup(response.content, "html.parser")
        except requests.exceptions.RequestException as e:
            print(f"Error fetching the URL")
            return None
        
    @classmethod # Check whether Netzverb has a page related to specific word
    def check_netz_presence(self, soup: BeautifulSoup, word):
        if soup == None: return False

        if soup.find("h1", string=re.compile(r"^Definition")):
            return True
        else: return False
        
    @classmethod
    def get_translation(self, soup: BeautifulSoup, language):
        if not soup: return None
        dd = soup.find("dd", lang=language)
        if not dd: return None
        span = dd.find_all("span")[1]
        if not span: return None
        words = [word.strip() for word in span.text.split(",")]
        return ", ".join(words[:4])
    
    @classmethod
    def get_example(self, soup: BeautifulSoup, n: int):
        if soup == None: return None
        examples = []
        # Find all <a> tags with href attributes
        anchor_tags = soup.find_all("a", href=True)
        if not anchor_tags: return None
        for tag in anchor_tags:
            href = tag["href"]
            if href.startswith("https://www.satzapp.de/?t="):
                sentance = href.split("=")[1]
                examples.append(sentance)
        return "; ".join(examples[:n])
    
    @classmethod
    def get_meaning(self, soup: BeautifulSoup, n: int): # class=rBox rBoxWht
        if soup == None: return None
        list_prefixes = ("a.", "b.", "c.", "d.", "e.")
        meanings = []
        sections = soup.find_all("section", class_="rBox rBoxWht")
        if not sections: return None
        for section in sections:
            h2 = section.find("h2")
            if h2 and h2.text == "Bedeutungen":
                dl = section.find('dl', class_='wNrn')
                if dl:
                    dd_tags = dl.find_all('dd')
                    for dd in dd_tags:
                        text = dd.text.strip()
                        if text.startswith(list_prefixes):
                            text = text[2:]
                        for part in text.split(";"):
                            part = part.strip()  
                            if part:
                                meanings.append(part)
                    return "; ".join(meanings[:n])
    
    @classmethod
    def get_word(self, soup: BeautifulSoup):
        if soup == None: return None
        return soup.find("div", class_="rCntr rClear").text.strip()
    
    @classmethod
    def check_verb(self, soup: BeautifulSoup):
        if soup == None: return None
        section = soup.find_all("section", class_="rBox rBoxWht")[0]
        span = section.find_all("span", class_="rInf")[0]
        part = span.find_all("span", attrs={'title': "Verb"})
        if part:
            return(part[0].text.upper())

class Vocabulary:
    def __init__(self):
        self.data = pd.DataFrame()
        
    def read_data(self, file):
        self.data = (pd.read_csv(file, header=None, names=["Input"])
                    .dropna()
                    .reset_index(drop=True))

    def noun_type(self, phrase):
        articles = ["der", "die", "das"]
        words = phrase.strip().split()
        if words[0].lower() in articles:
            article = words[0].lower()
            noun = " ".join(words[1:])
            return article, noun
        else:
            return None, phrase.strip()
    
    def word_type(self):
        nlp = spacy.load("de_core_news_sm", disable=["ner", "parser"])
        func = lambda x: nlp(x)[0].pos_
        self.data.type = self.data.type.fillna(self.data.german.apply(func))

    def clean_data(self):
        self.data[["type", "german"]] = self.data["Input"].apply(lambda x: pd.Series(self.noun_type(x)))
        del self.data["Input"]
        self.word_type()

    def output(self, file_name="vocabulary.csv"):
        out_location = Path(__file__).parent / file_name

        # Append if the file exists, otherwise write normally
        self.data.to_csv(
            out_location, 
            index=False, 
            mode="a" if out_location.exists() else "w", 
            header=not out_location.exists()
        )

        print(f"Translations saved to {out_location}")

    def get_netz_info(self, main_lang, second_lang=None, examples=0, meanings=0, progress_callback=None, callback = None):
        # Initialize columns dynamically
        columns = ["translation", "second_translation", "example", "meaning", "score"]
        if len(main_lang) > 2: main_lang = Netzverb.get_lang_code(main_lang)
        if second_lang and len(second_lang) > 2: second_lang = Netzverb.get_lang_code(second_lang)

        for col in columns:
            self.data[col] = None

        def process_row(row):
            word = row["german"]
            row["score"] = 0
            
            print(f"Parsing for {word}")
            if progress_callback: progress_callback(row.name + 1, self.data.shape[0])

            # Determine the correct Netzverb method
            if row["type"] in Netzverb.nouns:
                soup = Netzverb.get_noun_html_response(word)
            elif row["type"] in ["CONJ", "CCONJ", "SCONJ"]:
                soup = Netzverb.get_conj_html_response(word)
            else:
                soup = Netzverb.get_html_response(word)

            # Skip processing if word is not present
            if not Netzverb.check_netz_presence(soup, word):
                return row

            # Get the base form and update German/Type columns
            if row["type"] in Netzverb.nouns: 
                base_form = Netzverb.get_word(soup)
                type_and_word = base_form.split(sep=',',maxsplit=1)
                if len(type_and_word) == 2:
                    row["german"], row["type"] = type_and_word
                    row["type"] = row["type"].strip()
                    row["german"] = row["german"].strip()
                    
            if row["type"] in Netzverb.verbs: 
                base_form = Netzverb.get_word(soup)
                if isinstance(base_form, str):
                    row["german"] = base_form

            # Fill translations and other data
            row["translation"] = Netzverb.get_translation(soup, main_lang)
            if second_lang: row["second_translation"] = Netzverb.get_translation(soup, second_lang)
            if examples: row["example"] = Netzverb.get_example(soup, examples)
            if meanings: row["meaning"] = Netzverb.get_meaning(soup, meanings)
            
            return row

        # Apply processing function to all rows
        self.data = self.data.apply(process_row, axis=1)
        if callback: callback()


if __name__ == "__main__":
    pass
