import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

from server import Server


vk_session = vk_api.VkApi(token='')
longpoll = VkBotLongPoll(vk_session, 208877560)

vk = vk_session.get_api()

server = Server(longpoll, vk, vk_session)

commands = {
            'Помощь': {
                'func': server.command_help,
                'description': 'Показывает информацию о возможностях бота'
            },
            'Ближайшие Концерты': {
                'func': server.command_upcoming_concerts,
                'description': 'Показывает информацию о ближайших концертах в вашем городе'
            },
            # '': {
            #     'func': server.command_find,
            #     'description': 'Показывает концерты в Московской консерватории на текущий день'
            # },
            }

while True:
    try:
        server.start(commands)
    except:
        pass
