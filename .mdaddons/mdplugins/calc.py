import math
import numpy as np
from Classes.AeServer import AeServer

class mdplugin():
    def __init__(self, server: AeServer):
        self.server = server
        self.restrictions = {
            "__builtins__": None,
            "math": math,
            "abs": abs,
            "round": round,
            "np": np
        }

    async def on_player_message(self, player: str, message: str):

        if message.startswith('=='):
            expresion = message.removeprefix('==')
            value = str(eval(expresion, self.restrictions))
            print(value)
            self.server.send_response('@a', value, colour = 'golden')
