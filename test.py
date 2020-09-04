import threading, queue, datetime, time

q = queue.PriorityQueue()

def poster():
    while True:
        timestamp = q.get()
        now = datetime.datetime.utcnow().timestamp()

        print(f"Trying {timestamp} at {now}")

        if timestamp <= now:
            print(f'Finished {timestamp}')
            q.task_done()
        else:
            q.put(timestamp, timestamp)

        time.sleep(1)

# turn-on the worker thread
threading.Thread(target=poster, daemon=True).start()

now = datetime.datetime.utcnow().timestamp()
print(f"Now: {now}")

timestamp1 = now + 10
timestamp2 = now + 2
timestamp3 = now + 5

q.put(timestamp1, timestamp1)
q.put(timestamp2, timestamp2)
q.put(timestamp3, timestamp3)

print('All task requests sent\n', end='')

# block until all tasks are done
q.join()
print('All work completed')
