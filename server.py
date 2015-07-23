# -*- coding: utf-8 -*-
from telegram_bot_helper.api import (TelegramAPIHelper, CommandMessage,
                                     JoinMessage)
from telegram_bot_helper.emojis import Emojis

from random import randrange
from time import sleep

import ConfigParser
import pickle
import os.path


class TelegramBotServer():
    LANGUAGE_DB = 'languages.db'
    CONFIGURATION_FILE = 'foreveralone.cfg'
    last_update_id = 0
    sleep_time = 10
    languages = {}
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
        self.telegram = TelegramAPIHelper(self.token)
        self._load_languages_db_from_file()

    def get_configuration(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.read(self.CONFIGURATION_FILE)
        try:
            self.token = self.config.get('main', 'token')
            self.bot_id = self.config.get('main', 'bot_id')
            self.default_language = self.config.get('main', 'default_language')
        except (ConfigParser.NoOptionError, ConfigParser.NoSectionError) as e:
            print "Cannot load configuration file"
            print e.message

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
            self.languages.get(message.chat_id,
                               self.default_language))
        self.telegram.send_message(message.chat_id, phrase)

    def process_spanish(self, message):
        self.process_language(message, 'es')

    def process_english(self, message):
        self.process_language(message, 'en')

    def process_language(self, message, language):
        self.debug("Setting language: (%s - %s)" % (message.chat_id, language))
        self.languages[message.chat_id] = language
        text = {
            'es': "Idioma cambiado correctamente",
            'en': "English language selected"
        }
        self.telegram.send_message(message.chat_id, text[language])
        self._save_languages_db_to_file()

    def send_welcome_text(self, message):
        self.debug("Processing a welcome")
        self.telegram.send_message(message.chat_id, self.welcome_text)

    def process_info(self, message):
        self.debug("Processing a info command")
        self.telegram.send_message(message.chat_id, self.welcome_text)

    def get_random_phrase(self, language):
        phrases_array = getattr(self, "%s_phrases" % language)
        return phrases_array[randrange(len(phrases_array))]

    def _load_languages_db_from_file(self):
        if os.path.isfile(self.LANGUAGE_DB):
            with open(self.LANGUAGE_DB, 'r') as languages_file:
                self.languages = pickle.load(languages_file)

    def _save_languages_db_to_file(self):
        with open(self.LANGUAGE_DB, 'w') as languages_file:
            pickle.dump(self.languages, languages_file)

    es_phrases = [
        "Tranquilo, estoy aquí contigo... no estás solito",
        "Esto no lo salva ni Chico Terremoto",
        "Mejor escribe en el grupo del porno %s" % Emojis.get(':+1:'),
        "¡Déjame en paz! Estoy hablando con un amigo...",
        "¡Estoy harto de ser un segundo plato! ¡Sólo te acuerdas de " +
        "mí cuando nadie te hace caso!",
        "¿Has considerado tener sexo con nuestra amiga Inma?",
        "Cambia de amigos....",
        "Un segundo, me llama mi A-M-I-G-O al teléfono",
        "Un psicólogo te diría que tienes complejo de Rosa Díez",
        "Yo estoy peor que tu... soy un bot programado",
        "Tener amigos está overrated",
        "¿Recuerdas aquella noche con tus amigos? Yo no",
        "¡Somos inmortales! Ni la muerte quiere venir a vernos",
        "La típica paja por aburrimiento",
        "Fap-fap-fap-fap-fap Oliver, Benji, los magos del balón fap-" +
        "fap-fap-fap-fap-f... ¡Cierra la puerta tío!",
        "Estás más solo que Froilán en una reunión de Amigos del Rifle",
        "Estás más solo que el Rey en un meeting de Podemos",
        "A más de 300 kilómetros no son cuernos. El problema es que " +
        "allí sigo estando forever alone",
        "Sorry, no",
        "Jesús te ama",
        "Welcome to the friendzone!",
        "¿Quieres un abrazo? Pues te jodes, no tengo brazos",
        "¿Dices que tienes dos entradas de cine? Felicidades, así " +
        "la puedes ir a ver dos veces",
        "¿Qué haces hablando aquí? Todo el mundo está de juerga",
        "Deja de escribir y trabaja... ¡aunque sólo sea un poquito!",
        "Paciencia, en Halloween podrás salir a la calle",
        "Si tu perro pasa de ti, ¿qué quieres que te diga yo?",
        "Acuario: te sientes con energías, pero estarás muy S O L O",
        "Talking to me?",
        "Youuu shaaall not paaaaaaaaaaaass",
        "Te quiero, pero como amigo",
        "Vete a cenar con el Nan",
        "Mi vida amorosa es mágica. Nada por allí, nada por allá.",
        "¿Quién? ¿Quién? ¿Quién te escucha?",
        "Si hubieras comprado Smirnoff del bueno, al menos te hablarían",
        "Si yo iría a hablar contigo, pero ir pa na', tontería",
        "Copito",
    ]

    en_phrases = [
        "Talking to me?"
    ]
if __name__ == "__main__":
    TelegramBotServer().run_server()
