import requests
from profile import profile
from time import sleep
import threading
import psutil
import hashlib
import datetime

API_KEY = "bFF6vOYn.2oKKcr5Ktbcaki4hEhh0nPeIWuCKMmbR"
API_SECRET = "bFF6vOYn"
SUCCESS = 0
COUNTER = 1


@profile
def make_request(i):
    global SUCCESS, COUNTER
    name = "README.md"
    hash_md5 = hashlib.md5()
    with open(name, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    data = {
        'ip': '192.168.1.120',
        'machine': 'IronMachine',
        'filename': str(datetime.datetime.now()),
        'user': 'Avinash',
        'rank': i,
        'md5sum': hash_md5.hexdigest(),
        'token': API_KEY
    }
    COUNTER += 1
    files = {'pde': open(name, 'rb')}
    # headers = { 'Api-Secret-Key': 'Zm4QsmdXsobX', 'Api-Token': 'f8000c5bb202edd77e994658f02949a2'} #old

    headers = {'Api-Secret-Key': API_SECRET, 'Api-Token': API_KEY, 'MD5SUM': hash_md5.hexdigest(),
               'X-Api-Key': API_KEY, 'Authorization': 'Token ' + API_KEY, 'Token': API_KEY}
    # 'content-type': 'multipart/form-data',
    r = requests.post("https://localhost:8443/pde/add/",
                      data=data, headers=headers, files=files, verify=False)
    # r = requests.post("https://localhost:8000/pde/add/", data=data, headers=headers, files=files, verify=False)
    print(r.text)
    if "Success" in r.text:
        SUCCESS += 1


def stats():
    print("Success: ", SUCCESS)


def seq(c):
    for i in range(c):
        make_request(i)


def con(c):
    for i in range(c):
        threading.Thread(target=make_request, args=(i,)).start()


# con(10)
seq(1)
stats()
