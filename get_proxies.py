import threading
import queue
import requests

q = queue.Queue()
valid_proxies = []
with open('proxies.txt', 'r') as f:
    proxies = f.read().split('\n')
    for p in proxies:
        q.put(p)

def check_proxies():
    global q
    global valid_proxies
    global event
    while not q.empty():
        proxy = q.get()
        try:
            res = requests.get('http://ipinfo.io/json', proxies={'http': proxy, 'https': proxy}, timeout=3)
        except:
            continue
        if res.status_code == 200:
            valid_proxies.append(proxy)
    event.set()

event = threading.Event()

for _ in range(20):
    threading.Thread(target=check_proxies).start()

while not event.is_set():
    pass


to_write = ["{}\n".format(i) for i in valid_proxies]
with open(r'valid_proxies.txt', 'w') as f:
    f.writelines(to_write)
