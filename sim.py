import pickle as pkl
import time
import threading
import math
import os



#constants
TICK_INTERVAL = 0.05 #tick interval in seconds



#global variables
data = {}
prices = {}
st_time = end_time = time.time()



#tool functions
def style(text, *codes):
    return "\033[" + ";".join(map(str, codes)) + "m" + text + "\033[0m"

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def ln():
    print("-" * 42)



#game functions
def init():
    global data, st_time, end_time
    st_time = end_time = time.time()
    data = {
            "exp": 0,
            "learning rate": 1,
            "solved tasks": 0,
            "tick speed": 1 / TICK_INTERVAL
    }
    prices = {
            "exp": None,
            "learning rate": None,
            "solved tasks": (300, "exp"),
            "tick speed": (20, "solved tasks")
    }



def gametick(coeff=1):
    data["learning rate"] = data["solved tasks"] ** 2
    data["exp"] += data["learning rate"] * coeff



def update(interval): 
    ticks = math.ceil(interval * data["tick speed"])
    coe = 1
    if ticks > 50000:
        coe = ticks / 50000
        ticks = 50000
    for i in range(ticks):
        gametick(coe)



def load(): 
    global data, st_time, end_time
    clr()
    print("Loading data...")
    init()
    try:
        with open("data.pkl", "rb") as fi:
            end_time = pkl.load(fi)
            d = pkl.load(fi)
            for i in d.keys():
                data[i] = d[i]
            st_time = time.time()
            offtm = math.ceil(st_time - end_time)
            update(offtm)
            print("Game save loaded")
            hr = offtm // 3600
            mn = (offtm - hr * 3600) // 60
            sc = offtm - hr * 3600 - mn * 60
            tm = "\nIn the"
            if hr: tm += f" {hr} hours"
            if mn: tm += f" {mn} minutes"
            if sc: tm += f" {sc} seconds"
            tm += " offline, you have gained: "
            print(tm)
            for i in d.keys():
                if d[i] != data[i]:
                    print(f"{i}: {data[i] - d[i]:.3g}")
            input()
    except Exception as e:
        time.sleep(0.1)
        print("Data initialized")
        time.sleep(1)

def save():
    global end_time
    end_time = time.time()
    with open("data.pkl", "wb") as fi:
        pkl.dump(end_time, fi)
        pkl.dump(data, fi)



def timerLoop(func, interval, *args):
    while True:
        func(*args)
        time.sleep(interval)

def timerThrd(func, interval, autostart=True, *args):
    t = threading.Thread(target=timerLoop, args=(func, interval, *args), daemon=True)
    if autostart: t.start()
    return t



#options
def solveTask():



#start game
load()
autosv_thrd = timerThrd(save, 30)
gametk_thrd = timerThrd(gametick, TICK_INTERVAL, True, data["tick speed"] * TICK_INTERVAL)

while True:
    clr()
    print(style("HKOI Simulator", 1))
    ln()
    for i, j in data.items():
        print(f"{i}: {j:.3g}")
    print(
f'''
Options:
0. Save and exit
1. Solve a task {style("(300 exp)", 34)}

Your choice: '''
    )
    c = input()
    if c == "iamCHEATER":
        for i in data.keys():
            data[i] = 1e100
        print(style("\nSet all resources to 1e100", 1, 91))
        input()
    elif c == "0":
        save()
        exit()
    elif c == "1":
        pass