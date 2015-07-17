# -*- coding: utf-8 -*-

from time import sleep
from random import randrange

import requests


class TelegramBotServer():
    last_update_id = 0
    token = ""
    api_url = "https://api.telegram.org/bot%s/" % token
    available_commands = ['/foreveralone']
    sleep_time = 10

    def __init__(self, debug=False):
        self.debug_flag = debug

    def debug(self, message):
        if self.debug_flag:
            print "DEBUG: %s" % message

    def run_server(self):
        self.debug("Starting the server")
        dry_run = True
        while True:
            self.debug("Fetching data")
            data = self.get_data()

            if not self.data_is_ok(data):
                continue

            messages = [x.get('message', {}) for x in data.get('result', [])]
            (messages, next_update_id) = self.process_data(data)
            self.debug("Processing %d messages" % len(messages))
            for message in messages:
                if not self.is_group_chat(message) or dry_run:
                    continue
                self.process_message(message, self.get_chat_id(message))

            self.last_update_id = next_update_id
            self.debug("The new update_id is %s" % self.last_update_id)
            dry_run = False

            sleep(self.sleep_time)

    def get_data(self):
        params = {'offset': self.last_update_id + 1}
        return requests.get(self.api_url + "getUpdates", params=params).json()

    def data_is_ok(self, data):
        return data.get('ok', False)

    def process_data(self, data):
        messages = [x.get('message', {}) for x in data.get('result', [])]
        update_id = self.last_update_id
        if len(messages):
            update_id = data['result'][-1].get('update_id',
                                               self.last_update_id)

        return (messages, update_id)

    def is_group_chat(self, message):
        return self.get_chat_id(message) < 0

    def get_chat_id(self, message):
        chat = message.get('chat', {})
        return chat.get('id', 0)

    def process_message(self, message, chat_id):
        self.debug("Processing the text: %s" % message.get('text', ''))
        text = message.get('text', '').lower().split()
        self.debug("Processing the command: %s" % ' '.join(text))
        if not len(text) or text[0] not in self.available_commands:
            return
        getattr(self, "process_%s" % text[0][1:])(text, chat_id)

    def process_foreveralone(self, text, chat_id):
        data = {'chat_id': chat_id,
                'text': self.get_random_phrase()}
        response = requests.post(self.api_url + "sendMessage", data=data)
        return response.json().get('ok', False)

    def get_random_phrase(self):
        phrases = [
            "Tranquilo, estoy aquí contigo... no estás solito",
            "Esto no lo salva ni Chico Terremoto",
            "Mejor escribe en el grupo del porno :+1:",
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
        ]

        return phrases[randrange(len(phrases))]

if __name__ == "__main__":
    TelegramBotServer(debug=True).run_server()
