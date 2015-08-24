# -*- coding: utf-8 -*-
from telegram_bot_helper.api import (TelegramAPIHelper, CommandMessage,
                                     JoinMessage)
from phrases import Phrases

from random import randrange
from time import sleep

import ConfigParser
import pickle
import os.path


class TelegramBotServer():
    LANGUAGE_DB = 'languages.db'
    CONFIGURATION_FILE = 'foreveralone.cfg'
    phrases = {}
    chat_languages = {}
    last_update_id = 0
    sleep_time = 10
    available_languages = {}
    available_commands = ['foreveralone', 'info', 'spanish', 'english']
    welcome_text = ("Hello! I cannot read your messages but, when in a "
                    "group, ping me with a /foreveralone command and you "
                    "(or your friends) will not be alone again (/info "
                    "to see this message again)\n\n"
                    "Hola! No puedo leer tus mensajes pero si estamos en "
                    "un grupo puedes llamarme con el comando /foreveralone "
                    "y tu (o tus amigos) no volveréis a estar solos ("
                    "escribe /info para ver este mensaje de nuevo)\n\n"
                    "Switch to English with /english \n"
                    "Cambia a español con /spanish")

    def __init__(self, debug=False):
        self.debug_flag = debug
        self.get_configuration()
        self.telegram = TelegramAPIHelper(self.token, self.bot_name)
        self.load_phrases()
        self._load_chat_languages_db_from_file()

    def get_configuration(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.CONFIGURATION_FILE)
        try:
            self.token = self.config.get('main', 'token')
            self.bot_id = self.config.get('main', 'bot_id')
            self.bot_name = self.config.get('main', 'bot_name')
            self.default_language = self.config.get('main', 'default_language')
            self.available_languages = self.config.get('main',
                                                       'languages').split(', ')
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            print "Cannot load configuration file"
            print e.message

    def load_phrases(self):
        for lan in self.available_languages:
            try:
                self.phrases[lan] = getattr(Phrases, "%s_phrases" % lan)
            except AttributeError:
                pass

    def debug(self, message):
        if self.debug_flag:
            print "DEBUG: %s" % message

    def run_server(self):
        self.debug("Starting the server")
        dry_run = True
        while True:
            self.debug("Fetching data")
            messages = self.telegram.get_new_messages()
            self.telegram.update_offset()
            self.debug("Processing %d messages" % len(messages))

            for message in messages:
                if dry_run:
                    continue
                self.process_message(message)

            dry_run = False
            sleep(self.sleep_time)

    def process_message(self, message):
        if self._valid_command(message):
            getattr(self, "process_%s" % message.command)(message)
        elif self._bot_joined(message):
            self.send_welcome_text(message)

    def _valid_command(self, message):
        return isinstance(message, CommandMessage) and \
            message.command in self.available_commands

    def _bot_joined(self, message):
        return isinstance(message, JoinMessage) and \
            str(message.subject_id) == str(self.bot_id)

    def process_foreveralone(self, message):
        self.debug("Processing a command: %s" % message.command)
        phrase = self.get_random_phrase(
            self.chat_languages.get(message.chat_id, self.default_language))
        self.telegram.send_message(self._get_data(message, phrase))

    def process_spanish(self, message):
        self.process_language(message, 'es')

    def process_english(self, message):
        self.process_language(message, 'en')

    def process_language(self, message, language):
        self.debug("Setting language: (%s - %s)" % (message.chat_id, language))
        self.chat_languages[message.chat_id] = language
        text = {
            'es': "Idioma cambiado correctamente",
            'en': "English language selected"
        }
        self.telegram.send_message(self._get_data(message, text[language]))
        self._save_chat_languages_db_to_file()

    def send_welcome_text(self, message):
        self.debug("Processing a welcome")
        self.telegram.send_message(self._get_data(message, self.welcome_text))

    def process_info(self, message):
        self.debug("Processing a info command")
        self.telegram.send_message(self._get_data(message, self.welcome_text))

    def _get_data(self, message, text):
        return {'chat_id': message.chat_id, 'text': text}

    def get_random_phrase(self, language):
        phrases_array = self.phrases.get(language, self.default_language)
        return phrases_array[randrange(len(phrases_array))]

    def _load_chat_languages_db_from_file(self):
        if os.path.isfile(self.LANGUAGE_DB):
            with open(self.LANGUAGE_DB, 'r') as languages_file:
                self.chat_languages = pickle.load(languages_file)

    def _save_chat_languages_db_to_file(self):
        with open(self.LANGUAGE_DB, 'w') as languages_file:
            pickle.dump(self.chat_languages, languages_file)

if __name__ == "__main__":
    TelegramBotServer().run_server()
