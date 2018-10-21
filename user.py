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
        self._status = None
        self._loc_is_updating = False
        self._start_time = time.time()

    def start_user_tracking(self):
        self._start_time = time.time()
        self._loc_is_updating = True
        self._status = 'reachable'

    def update_status(self, status):
        self._status = status

    def update_location(self):
        if self._loc_is_updating:
            self._loc['lat'] += 0.0005 * random.random()
            self._loc['lon'] += 0.0005 * random.random()

    def freeze_location(self):
        self._loc_is_updating = False

    def get_user_status(self):
        return self._status

    def get_user_location(self):
        return self._loc

    def run(self):
        while True:
            time.sleep(MAIN_LOOP_SLEEP)

            if not self._loc_is_updating:
                continue

            cur_time = time.time()
            if cur_time - self._start_time > UNREACHABLE_TIMEOUT:
                self.update_status('unreachable')
                self.freeze_location()

            self.update_location()
