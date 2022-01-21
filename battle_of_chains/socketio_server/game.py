import random
import time

from .async_db_calls import add_user_to_room, get_battle_settings, remove_user_from_room


class Game:

    class STATE:
        WAITING = 'waiting'
        RUNNING = 'running'
        FINISHED = 'finished'

    def __init__(self, room, battle):
        self.id = f'{room.id}_{battle.id}'
        self.room = room
        self.battle = battle
        self.order = []
        self.users = {}
        self.current_player = {}
        self.state = self.STATE.WAITING
        self.created = time.time()
        self.started = None
        self.time_to_move = 30

    async def add_user(self, user, sid, tanks):
        tanks = sorted(tanks, key=lambda x: x['moving_price'])
        tanks_order = [tank['id'] for tank in tanks[::-1]]
        self.users[user.username] = {'sid': sid, 'tanks': tanks, 'tanks_order': tanks_order}
        await add_user_to_room(self.room, user)

    async def remove_user(self, user):
        if self.current_player.get('username') == user.username:
            self.set_next_player()
        if self.order:
            self.order.pop(self.order.index(user.username))
        try:
            del self.users[user.username]
        except KeyError:
            pass
        await remove_user_from_room(self.room, user)

    def set_next_player(self):
        cur_index = self.order.index(self.current_player['username'])
        current_player = self.order[cur_index - 1]
        tanks_order = self.users[current_player]['tanks_order']
        last_tank = self.users[current_player].get('last_tank')
        if last_tank:
            cur_tank_index = tanks_order.index(last_tank)
            current_tank = tanks_order[cur_tank_index - 1]
        else:
            current_tank = tanks_order[-1]
        self.users[current_player]['last_tank'] = current_tank
        self.current_player = {'username': current_player, 'tank': current_tank}

    async def start(self):
        battle_settings = await get_battle_settings()
        self.time_to_move = battle_settings.time_to_move
        usernames = list(self.users.keys())
        random.shuffle(usernames)
        self.order = usernames
        uname = self.order[-1]
        tank = self.users[uname]['tanks_order'][-1]
        self.users[uname]['last_tank'] = tank
        self.current_player = {'username': uname, 'tank': tank}
        self.state = Game.STATE.RUNNING
        self.started = time.time()
