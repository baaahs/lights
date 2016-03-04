
import sheep
import time


class TestEvilShow(object):

    name = "_Test Evil"
    ok_for_random = False

    # This has to be set True when testing
    is_show = False

    def __init__(self, sheep_sides):
        self.count = 0
        pass


    def next_frame(self):
        while True:
            raise Exception("You shouldn't try to run this")

            self.count += 1
            if self.count < 5:
                yield 0.001

            time.sleep(0.5)
