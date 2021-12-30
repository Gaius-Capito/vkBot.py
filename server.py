from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id

from parser import Mosconsv


class Server:

    def __init__(self, longpoll, vk):
        self.__longpoll = longpoll
        self.vk = vk
        print('Бот запущен!')

    def start(self, commands):
        self.commands = commands
        self.__command_starter()

    def __command_starter(self):
        for event in self.__longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.object['text'].lower()
                self.commands[msg]['func'](event.object['peer_id'])

    def command_help(self, user_id):
        bot_functions = [f'{value}: {self.commands[value]["description"]}' for number_iteration, value in
                         enumerate(self.commands.keys())]
        bot_functions = '\n'.join(bot_functions)
        self.vk.messages.send(
            message=f'Вот что я умею: {bot_functions}',
            peer_id=user_id,
            random_id=get_random_id()
        )

    def command_upcoming_concerts(self, user_id):
        self.vk.messages.send(
            message=f'Разработчик приуныл. Но в скором времени здесь будет информация о концертах',
            peer_id=user_id,
            random_id=get_random_id()
        )

    def command_mosconsv(self, user_id):
        self.vk.messages.send(
            message=Mosconsv().show_results(),
            peer_id=user_id,
            random_id=get_random_id()
        )

#
