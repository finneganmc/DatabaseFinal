import json

def Changedata(name,value):
    with open("data.json",'r',encoding='utf-8') as load_f:
        d = json.load(load_f)
    d[name] = value
    with open("data.json",'w',encoding='utf-8') as f:
        json.dump(d, f,ensure_ascii=False)

def Readdata(name):
    with open("data.json",'r',encoding='utf-8') as load_f:
        d = json.load(load_f)
    return d[name]
