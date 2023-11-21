from flask import Flask, request, render_template, g, redirect, Response, abort
from datetime import datetime
import json
from utils import *
from config import *



def tweet(): 
  tt  = request.form['text']
  tl = "English"
  pt = str(datetime.now())
  with open("./data.json",'r',encoding='utf-8') as load_f:
    d = json.load(load_f)
  tid = d["Tweetcount"]+1
  d["Tweetcount"] += 1
  uid = d[CurUser]
  Changedata("Tweetcount",d["Tweetcount"]+1)
  params_dict = {"tid":tid,"tt":tt,"tl":tl,"pt":pt, "uid":uid}
  g.conn.execute(text("INSERT INTO Tweets(tweet_id,tweet_text,tweet_language,post_time) VALUES (:tid,:tt,:tl,:pt)"), params_dict)
  g.conn.execute(text("INSERT INTO from_user(tweet_id,user_id) VALUES (:tid, :uid)"), params_dict)
  g.conn.commit()
  return render_template('index')

def like():
  si = str(datetime.now())
  with open("./data.json",'r',encoding='utf-8') as load_f:
    d = json.load(load_f)
  tid = request.form['id']
  uid = d[CurUser]
  Changedata("Tweetcount",d["Tweetcount"]+1)
  params_dict = {"tid": tid, "uid":uid, "si":si}
  g.conn.execute(text("INSERT INTO Likes(tweet_id, user_id,since) VALUES (:tid,:uid,:si)"), params_dict)
  g.conn.commit()
  return render_template('index')

def follow():
  si = str(datetime.now())
  with open("./data.json",'r',encoding='utf-8') as load_f:
    d = json.load(load_f)
  uid = d[CurUser]
  fud = request.form["id"]
  params_dict = {"uid":uid, "fud":fud, "si":si}
  g.conn.execute(text("INSERT INTO Likes(tweet_id, user_id,since) VALUES (:tid,:uid,:si)"), params_dict)
  g.conn.commit()
  return render_template('index')