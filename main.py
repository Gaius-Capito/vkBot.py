import vk_api
from vk_api.bot_longpoll import VkBotLongPoll

from server import Server


vk_session = vk_api.VkApi(token='88b82b59a1055a1467ccc8e34ac2374dbc820fe8642d87cd7f3b0b4aeb7210610108f748e658cde1c290e')
longpoll = VkBotLongPoll(vk_session, 208877560)

vk = vk_session.get_api()

server = Server(longpoll, vk)

commands = {
            'помощь': {
                'func': server.command_help,
                'description': 'Показывает информацию о возможностях бота'
            },
            'ближайшие концерты': {
                'func': server.command_upcoming_concerts,
                'description': 'Показывает информацию о ближайших концертах в вашем городе'
            },
            'не важно': {
                'func': server.command_weather,
                'description': 'показывает !'
            },
        }

while True:
    try:
        server.start(commands)
    except:
        pass