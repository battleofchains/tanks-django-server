import socketio
import pytest
from channels.testing import ChannelsLiveServerTestCase


class TestServer(ChannelsLiveServerTestCase):

    def setUp(self) -> None:
        super(TestServer, self).setUp()

    @pytest.mark.asyncio
    async def test_my_consumer(self):
        client = socketio.AsyncClient()
        await client.connect(self.live_server_url, transports=['websocket'])
        print("my sid", client.sid)
