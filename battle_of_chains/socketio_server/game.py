import random
import time

from .async_db_calls import add_user_to_room, remove_user_from_room


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
        self.current_player = None
        self.state = self.STATE.WAITING
        self.created = time.time()
        self.started = None

    async def add_user(self, user, sid, tanks):
        tanks = sorted(tanks, key=lambda x: x['moving_price'])
        tanks_order = [tank['id'] for tank in tanks[::-1]]
        self.users[user.username] = {'sid': sid, 'tanks': tanks, 'tanks_order': tanks_order}
        await add_user_to_room(self.room, user)

    async def remove_user(self, user):
        try:
            del self.users[user.username]
        except KeyError:
            pass
        await remove_user_from_room(self.room, user)

    async def start(self):
        usernames = list(self.users.keys())
        random.shuffle(usernames)
        self.order = usernames
        uname = self.order[-1]
        tank = self.users[uname]['tanks_order'][-1]
        self.users[uname]['last_tank'] = tank
        self.current_player = {'username': uname, 'tank': tank}
        self.state = Game.STATE.RUNNING
        self.started = time.time()
