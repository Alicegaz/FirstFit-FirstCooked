from threading import Thread
import time
import random

ADDRESS_PATTERN = 'sip:+{addr}@ims8.wirelessfuture.com'
UNREACHABLE_TIMEOUT = 10    # secs
MAIN_LOOP_SLEEP = 0.5   # secs


class User(Thread):
    def __init__(self, addr_num, start_loc):
        super().__init__()
        self._addr = ADDRESS_PATTERN.format(addr=addr_num)
        self._loc = start_loc
        self._status = 'reachable'

    def update_status(self, status):
        self._status = status

    def update_location(self):
        self._loc['lat'] += 0.005 * random.random()
        self._loc['lon'] += 0.005 * random.random()

    def get_user_status(self):
        return self._status

    def get_user_location(self):
        return self._loc

    def run(self):
        start_time = time.time()
        while True:
            cur_time = time.time()
            if cur_time - start_time > UNREACHABLE_TIMEOUT:
                self.update_status('unreachable')

            self.update_location()

            time.sleep(MAIN_LOOP_SLEEP)
