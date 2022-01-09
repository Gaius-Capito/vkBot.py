from vk_api.bot_longpoll import VkBotEventType
from vk_api.utils import get_random_id
from vk_api.upload import VkUpload
from parser import Meloman


class Server:

    def __init__(self, longpoll, vk, vk_session):
        self.__longpoll = longpoll
        self.vk = vk
        self.vk_session = vk_session
        print('Бот запущен!')

    def start(self, commands):
        self.commands = commands
        self.__command_starter()

    def __command_starter(self):
        for event in self.__longpoll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                msg = event.object['text'].title()
                try:
                    self.commands[msg]['func'](event.object['peer_id'])
                except:
                    self.command_find(event.object['peer_id'], msg)
                    print('i')



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

    def command_find(self, user_id, msg):
        print(msg)
        data = Meloman()
        data.write_in_file(msg)
        send_doc = VkUpload(self.vk_session)
        try:
            mydoc = send_doc.document_message("concerts_to_sent.txt", title=msg, peer_id=user_id)
            self.vk.messages.send(user_id=user_id,
                                  message=msg,
                                  attachment=f"doc{mydoc['doc']['owner_id']}_{mydoc['doc']['id']}",
                                  random_id=get_random_id())
            print(mydoc)
        except Exception as ERROR:
            print(ERROR)
