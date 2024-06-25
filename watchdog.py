from threading import Thread
import time
import os


class Watchdog(object):

    def __init__(self):
        self.last_ping = time.time()
        self.time_to_stop = False
        self.must_die = False

        self.thread = Thread(target=self)
        self.thread.daemon = True
        self.thread.start()

    def __call__(self):
        while True:
            time.sleep(1)
            if self.time_to_stop:
                return

            since_last = time.time() - self.last_ping

            if since_last > 10.0:
                # OMG OMG OMG!!!!
                print("\n\n   OMG OMG OMG!!!!!")
                print("   Watchdog timer was not pinged frequently enough.")
                print("   Exiting with extreme prejudice because we assume a show is hung.\n\n")
                print("%f" % since_last)

                os._exit(1)

            if self.must_die:
                print("\n\n Must die set. Exiting")
                os._exit(2)



    def ping(self):
        self.last_ping = time.time()

    def stop(self):
        self.time_to_stop = True

    def manual_reset(self):
        print("--------------------------------------------------------")
        print("  MANUAL SERVER RESET")
        print("--------------------------------------------------------")

        self.must_die = True

