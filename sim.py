import pickle as pkl
import time
import threading
import math
import os



#constants
TICK_INTERVAL = 0.05 #tick interval in seconds
NIR = "Input not in range" #input not in range



#global variables
settings = {}
settings_filt = {}
data = {}
prices = {}
st_time = end_time = time.time()



#tool functions
def style(text, *codes):
    return "\033[" + ";".join(map(str, codes)) + "m" + text + "\033[0m"

def clr():
    os.system("cls" if os.name == "nt" else "clear")

def ln(symb="-", *styl):
    print(style(symb * 42, *styl))

def title(txt):
    print(style(txt, 1))
    ln()

def error(txt):
    ln("=", 31)
    print(style(txt, 1, 2, 91))
    ln("=", 31)

def succ(txt):
    ln("+", 92)
    print(style(txt, 1, 2, 92))
    ln("+", 92)

def wait():
    ln()
    print(style("Press enter to continue...", 3))
    input()

def nofilt(x):
    return False

def blank(x):
    return x == ""

def scan(txt, dtype, keep_trying=True, filtera=nofilt, *filters): #filtera: filters before checking type, filters: filters & failmessages after checking type
    while True:
        try:
            ln()
            print(txt, end="")
            c = input()
            if filtera(c): return c
            c = dtype(c)
            ok = True
            for i in range(0, len(filters) - 1, 2):
                if not filters[i](c):
                    error(filters[i + 1])
                    ok = False
                    break
            if ok: return c
        except Exception as e:
            error(f"Input should in type of '{dtype.__name__}'")
        if not keep_trying: break
    return None



#game functions
def init():
    global settings, settings_filt, data, prices, st_time, end_time
    st_time = end_time = time.time()
    settings = {
        "maximum tick simulation": 50000,
        "visualize process of loading data": "on"
    }
    settings_filt = {
        "maximum tick simulation": (lambda x: 5000 <= x and x <= 300000, "Value must be between 5000 and 300000"),
        "visualize process of loading data": (lambda x: x == "on" or x == "off", "Value must be either 'on' or 'off'")
    }
    data = {
        "exp": 0,
        "learning rate": 1,
        "solved tasks": 0,
        "tick speed": 1 / TICK_INTERVAL
    }
    prices = {
        "exp": None,
        "learning rate": None,
        "solved tasks": {"exp": [30, 1.1]},
        "tick speed": {"solved tasks": [20, 1.05]}
    }



def gametick(coeff=1):
    data["learning rate"] = 1 + 0.05 * data["solved tasks"]
    data["exp"] += data["learning rate"] * coeff



def update(interval, show=True):
    ticks = math.ceil(interval * data["tick speed"])
    coe = 1
    if ticks > settings["maximum tick simulation"]:
        coe = ticks / settings["maximum tick simulation"]
        ticks = settings["maximum tick simulation"]
    step = max(1, ticks // 7)
    for i in range(ticks):
        gametick(coe)
        if show:
            if settings["visualize process of loading data"] == "off": continue
            print(f"\rSimulating ticks...   ({i + 1}/{ticks})", end="")
            if (i + 1) % step == 0: time.sleep(0.15)
    if show: print()




def load(): 
    global settings, data, prices, st_time, end_time
    clr()
    print("Loading data...")
    init()
    try:
        with open("data.pkl", "rb") as fi:
            end_time = pkl.load(fi)
            settings = pkl.load(fi)
            d = pkl.load(fi)
            prices = pkl.load(fi)
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
            wait()
    except Exception as e:
        time.sleep(0.1)
        print("Data initialized")
        time.sleep(1)

def save():
    global end_time
    end_time = time.time()
    with open("data.pkl", "wb") as fi:
        pkl.dump(end_time, fi)
        pkl.dump(dict(settings), fi)
        pkl.dump(dict(data), fi)
        pkl.dump(dict(prices), fi)



def timerLoop(func, interval, *args):
    while True:
        func(*args)
        time.sleep(interval)

def timerThrd(func, interval, autostart=True, *args):
    t = threading.Thread(target=timerLoop, args=(func, interval, *args), daemon=True)
    if autostart: t.start()
    return t



#options
def settingsPage():
    while True:
        clr()
        title("Settings")
        for i, k in enumerate(settings.keys()):
            print(f"{i + 1}. {k}: {settings[k]}")
        c = scan("Modify settings: ", int, True, blank, lambda x: 1 <= x and x <= len(settings), NIR)
        if c == "": return
        k = list(settings.keys())[c - 1]
        c = scan(f"Change '{k}' to: ", type(settings[k]), False, nofilt, settings_filt[k][0], settings_filt[k][1])
        if c is not None:
            settings[k] = c
            succ(f"Changed the value of '{k}' to '{c}' successfully!")
        wait()



def upgrades():
    while True:
        clr()
        title("Upgrades")
        for i, j in data.items():
            print(f"{i}: {j:.3g}")
        ln()
        tmp = list(prices.items())
        cnt = 0
        vkeys = [[True]]
        val = {}
        print("Requirements for upgrading:")
        print("0. " + style("Buy maximum number of resources\n", 4, 94))
        for i, j in tmp:
            if j is None: continue
            cnt += 1
            vkeys.append([True, i])
            val[i] = cnt
            print(f"{cnt}. " + style(str(i), 4, 94) + ":")
            for k, l in j.items():
                rem = data[k] - l[0]
                print(k + ": " + style(f"{l[0]:.3g}", 91 if rem < 0 else (92 if rem > 0 else 93)))
                vkeys[cnt].append((k, rem))
                if rem < 0:
                    vkeys[cnt][0] = False
                    break
            if i != tmp[-1][0]: print()
        c = scan("Attribute to upgrade: ", int, True, blank, lambda x: 0 <= x and x <= cnt, NIR, lambda x: vkeys[x][0], "Not enough resources")
        if c == "": return
        if c != 0:
            for i in range(2, len(vkeys[c])):
                data[vkeys[c][i][0]] = vkeys[c][i][1]
                t = prices[vkeys[c][1]][vkeys[c][i][0]]
                t[0] *= t[1]
            data[vkeys[c][1]] += 1
            succ(f"Upgraded '{vkeys[c][1]}' successfully!")
        else:
            num = {}
            for i, j in list(prices.items()):
                if j is None or not vkeys[val[i]][0]: continue
                num[i] = 0
                while True:
                    ok = True
                    for k, l in j.items():
                        if data[k] < l[0]:
                            ok = False
                            break
                    if not ok: break
                    for k, l in j.items():
                        data[k] -= l[0]
                        t = prices[i][k]
                        t[0] *= t[1]
                    data[i] += 1
                    num[i] += 1
            s = "Bought:"
            b = False
            for i, j in num.items():
                if j == 0: continue
                b = True
                s += f"\n - {i}: {j:.3g}"
            if not b:
                error("Not enough resources to buy anything")
            else:
                succ(s)
        wait()



#start game
load()
autosv_thrd = timerThrd(save, 30, True)
gametk_thrd = timerThrd(update, TICK_INTERVAL, True, TICK_INTERVAL, False)

while True:
    clr()
    title("HKOI Simulator")
    for i, j in data.items():
        print(f"{i}: {j:.3g}")
    print(
f'''
Options:
0. Save and exit
1. Settings
2. Upgrades'''
    )
    c = scan("Your choice: ", int, True, lambda x: x == "" or x == "iamcheater", lambda x: 0 <= x and x <= 2, NIR)
    if c == "iamcheater":
        for i in data:
            data[i] *= 1e100
    elif c == 0:
        save()
        exit()
    elif c == 1:
        settingsPage()
    elif c == 2:
        upgrades()