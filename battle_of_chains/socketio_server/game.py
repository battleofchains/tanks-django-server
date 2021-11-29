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

    async def add_user(self, user, sid, tanks):
        self.users[user.username] = {'user': user, 'sid': sid, 'tanks': tanks}
        await add_user_to_room(self.room, user)

    async def remove_user(self, user):
        del self.users[user.username]
        await remove_user_from_room(self.room, user)
