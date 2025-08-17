import glob
from logging import getLogger
import os
import yaml
from functools import lru_cache

import os

def read_yaml(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = yaml.safe_load(file)
    return data


# Загружаем все переводы
trans_data = {}
for file in glob.glob("translations/*.yaml"):
    ln = os.path.splitext(os.path.basename(file))[0]
    yaml_data = read_yaml(file)
    trans_data[ln] = yaml_data

def get_langs():
    return tuple(trans_data.keys())

def get_lang_title(lang):
    return trans_data[lang].get('__title__')


from jinja2 import Environment, StrictUndefined

env = Environment(
    undefined=StrictUndefined,
    trim_blocks=True,
    autoescape=True
)

import inspect
import utils

env.globals.update({
    name: obj
    for name, obj in vars(utils).items()
    if inspect.isfunction(obj)
})


class Translator:
    def __init__(self, lang, data):
        self.lang = lang
        self.data = data
        self.logger = getLogger('BOT').getChild("translator")

    def __call__(self, key, default="Error: translation not found!", **kwargs) -> str:
        if key in self.data:
            text = self.data[key]
        else:
            return default

        if kwargs:
            try:
                template = env.from_string(text)
                text = template.render(**kwargs)
            except Exception as e:
                self.logger.error("Something wrong in translation", exc_info=True)
                raise e

        return text

@lru_cache
def get_translator(lang):
    return Translator(lang, trans_data.get(lang, {}))

@lru_cache
def get_all_trans(key):
    translations = {}
    for lang in trans_data.keys():
        translator = get_translator(lang)
        translations[lang] = translator(key)
    return translations


from telebot.types import Message, Message as M, CallbackQuery, CallbackQuery as C

async def tr(obj: M|C|Message|CallbackQuery) -> Translator:
    """
    Get translator from message or callback
    
    Args:
        obj: message or callbackquery object
        
    Returns:
        Translator
    """
    from database import db
    lang = await db.get_lang(obj.from_user.id)
    return get_translator(lang)

def get_text_translations(key: str, default="") -> dict:
    if key not in {k for d in trans_data.values() for k in d.keys()}:
        return default
    return {lang: get_translator(lang)(key, default) for lang in trans_data}

