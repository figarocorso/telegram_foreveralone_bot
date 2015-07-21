# -*- coding: utf-8 -*-

from time import sleep
from random import randrange

import requests


class TelegramAPIHelper():
    emojis = {
        ':+1:': u'\U0001F44D',
    }

    def __init__(self, token):
        self.last_update_id = 0
        self.url = "https://api.telegram.org/bot%s/" % token

    def get_new_messages(self, mark_as_read=True):
        data = self._get_data(mark_as_read)
        self.raw_messages = data.get('result', [])
        self.messages = self._parse_raw_messages()

        return self.messages

    def update_offset(self):
        if not len(self.messages):
            return
        self.last_update_id = self.messages[-1].get('update_id')

    def send_message(self, chat, message, tries=5):
        success = False
        while not success and tries > 0:
            data = {'chat_id': chat, 'text': message}
            success = self._send_post_request("sendMessage", data)
            tries -= 1
            sleep(1)

    def reply(self, message, text):
        pass

    def _get_data(self, mark_as_read):
        params = {'offset': self.last_update_id + 1} if mark_as_read else {}
        try:
            response = requests.get(self.url + "getUpdates", params=params)
        except requests.exceptions.ConnectionError:
            return {}

        if not response.ok:
            return {}

        return response.json()

    def _parse_raw_messages(self):
        messages = []
        for raw_message in self.raw_messages:
            message = raw_message.get('message', {})
            message['update_id'] = raw_message.get('update_id', 0)
            messages.append(message)

        return messages

    def _send_post_request(self, method, data):
        try:
            response = requests.post("%s%s" % (self.url, method),
                                     data=data)
            return response.ok
        except requests.exceptions.ConnectionError:
            return False


class TelegramBotServer():
    last_update_id = 0
    token = ""
    available_commands = ['/foreveralone']
    sleep_time = 10

    def __init__(self, debug=False):
        self.debug_flag = debug
        self.telegram = TelegramAPIHelper(self.token)

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
                if not self.is_group_chat(message) or dry_run:
                    continue
                self.process_message(message, self.get_chat_id(message))

            dry_run = False

            sleep(self.sleep_time)

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
        self.telegram.send_message(chat_id, self.get_random_phrase())

    def get_random_phrase(self):
        emojis = self.telegram.emojis
        phrases = [
            "Tranquilo, estoy aquí contigo... no estás solito",
            "Esto no lo salva ni Chico Terremoto",
            "Mejor escribe en el grupo del porno %s" % emojis[':+1:'],
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

        return phrases[randrange(len(phrases))]

if __name__ == "__main__":
    TelegramBotServer(debug=True).run_server()
