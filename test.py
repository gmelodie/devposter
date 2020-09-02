import concurrent.futures
import datetime

def scheduler(timestamps_pool):
    while True:
        now = datetime.datetime.now().timestamp()
        if timestamps_pool[0] <= now():
            timestamp = timestamps_pool.pop(0)
            fp = open(str(timestamp), "w+")
            fp.close()


timestamps_pool = []

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
    executor.submit(scheduler, timestamps_pool)

while True:
    wait_seconds = int(input(f"How many seconds to wait: "))
    now = datetime.datetime.now().timestamp()
    timestamps_pool.append(now + wait_seconds)
