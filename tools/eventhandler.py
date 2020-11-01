import asyncio
from datetime import datetime, timedelta
import threading
import time


# Get discords event loop
_loop = asyncio.get_event_loop()
# How long a reaction should stay up
TIME_TO_LIVE = 10 


class EventHandler():
    SECONDS = 0.5   # The amount of time between checks

    def __init__(self):
        self.msgs = [] # [(msg, dt, card_data)]

        # Start a single thread and run the event handler in the background
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        """ Main loop. Handles the deletion of reactions """
        while True:
            if self.msgs:
                msg, dt, _ = self.msgs[0]
                if datetime.now() >= dt:
                    asyncio.run_coroutine_threadsafe(msg.clear_reaction("👍"), _loop)
                    self.msgs.pop(0)

            time.sleep(self.SECONDS)

    def append(self, msg, card_id):
        """ Appends a msg object on our list and establishes a time to live """
        self.msgs.append((msg, datetime.now() + timedelta(seconds=TIME_TO_LIVE), card_id))

    def get_card_by_msg(self, reacted_msg):
        """  """
        for orig_msg, _, card in self.msgs:
            if orig_msg.id == reacted_msg.id:
                return card
        return {}

# Instantiate the event handler
event_handler = EventHandler()