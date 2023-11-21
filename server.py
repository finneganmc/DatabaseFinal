
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort
from datetime import datetime
import json
from utils import *
from config import *

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://yl5363:240308@34.74.171.121/proj1part2"

#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

# The string needs to be wrapped around text()

conn.execute(text("""CREATE TABLE IF NOT EXISTS test (
  id serial,
  name text
);"""))
conn.execute(text("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""))

# To make the queries run, we need to add this commit line

conn.commit() 

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query 
  #
  cursor = g.conn.execute(text("SELECT name FROM test"))
  g.conn.commit()

  # 2 ways to get results

  # Indexing result by column number
  names = []
  for result in cursor:
    names.append(result[0])  

  # Indexing result by column name
  # names = []
  # results = cursor.mappings().all()
  # for result in results:
  #   names.append(result["name"])
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("login.html", **context)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/another')
def another():
  return render_template("another.html")

@app.route('/toRegister')
def toRegister():
  return render_template("Register.html")

@app.route('/tologin')
def tologin():
  Changedata("CurUser",-1)
  return render_template("login.html")

@app.route('/update')
def update(): 
  print("0")
  cursor = g.conn.execute(text("SELECT tweet_id FROM has_tweet WHERE feed_id=(:id)"),{"id":Readdata("CurUser")})
  Tweet_set = set()
  print("1")
  for i in cursor:Tweet_set.add(i[0])
  Tweet_list = []
  print("2")
  for i in Tweet_set:
    cursor = g.conn.execute(text("SELECT user_id,text,post_time FROM tweets WHERE tweet_id=(:id)"),{"id":i})
    for a,b,c in cursor:
      print(a,b,c)
      c2 = g.conn.execute(text("SELECT user_name FROM users WHERE user_id=(:id)"),{"id":a})
      Tweet_list.append((c2.fetchall()[0][0],b,str(c)[:-10]))
  print(Tweet_list)
  context = dict(data = Tweet_list)
  return render_template("loginsucc.html", **context)
  # params_dict = {"name":name}
  # g.conn.execute(text('INSERT INTO test(name) VALUES (:name)'), params_dict)
  # g.conn.commit()
  return render_template("login.html")

# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add(): 
  name = request.form['name']
  params_dict = {"name":name}
  g.conn.execute(text('INSERT INTO test(name) VALUES (:name)'), params_dict)
  g.conn.commit()
  return redirect('/')

@app.route('/login', methods=['POST'])
def login(): 
  id = request.form['UserID']
  pw = request.form['Password']
  params_dict = {"id":id}
  cursor = g.conn.execute(text('SELECT user_password,user_id,feed_id FROM users where user_name=(:id)'), params_dict)
  res,ID,FID = cursor.fetchall()[0]
  if res == pw:
    with open("./data.json",'r+',encoding='utf-8') as load_f:
      d = json.load(load_f)
      d["CurUser"] = FID
      load_f.seek(0)
      load_f.write(json.dumps(d))
      load_f.truncate()
    return redirect('/update')
  else:
    return render_template('loginfail.html')
  
@app.route('/register', methods=['POST'])
def register(): 
  id = request.form['UserID']
  pw = request.form['Password']
  em = request.form['Email']
  dob = request.form['dob']
  ot = str(datetime.now())
  fid = int(Readdata("Usercount"))+1
  Changedata("Usercount",fid)
  params_dict = {"uid":fid,"id":id,"pw":pw,"em":em,"dob":dob,"ot":ot,"fid":fid}
  print("user id")
  g.conn.execute(text("INSERT INTO feeds(feed_id) VALUES (:fid)"), params_dict)
  g.conn.execute(text("INSERT INTO users(user_id,user_name,user_password,user_email,dob,created,feed_id) VALUES (:uid,:id,:pw,:em,:dob,:ot,:fid)"), params_dict)
  g.conn.commit()
  return render_template('login.html')
  
@app.route('/tweet', methods=['POST'])
def tweet(): 
  tt  = request.form['text']
  tl = "English"
  pt = str(datetime.now())
  with open("./data.json",'r',encoding='utf-8') as load_f:
      d = json.load(load_f)
      uid = d["CurUser"]
  tid = Readdata("Tweetcount")
  print("tid", tid)
  Changedata("Tweetcount", tid+1)
  params_dict = {"tid":tid,"tt":tt,"tl":tl,"pt":pt, "uid":uid}
  g.conn.execute(text("INSERT INTO Tweets(user_id, tweet_id,text,tweet_language,post_time) VALUES (:uid, :tid,:tt,:tl,:pt)"), params_dict)
  g.conn.commit()
  return render_template('loginsucc.html')

@app.route('/like', methods=['POST'])
def like():
  si = str(datetime.now())
  with open("./data.json",'r',encoding='utf-8') as load_f:
    d = json.load(load_f)
    tid = request.form['id']
    uid = d['CurUser']
  params_dict = {"tid": tid, "uid":uid, "si":si}
  g.conn.execute(text("INSERT INTO Likes(tweet_id, user_id,since) VALUES (:tid,:uid,:si)"), params_dict)
  g.conn.commit()
  return render_template('loginsucc.html')

@app.route('/follow', methods=['POST'])
def follow():
  si = str(datetime.now())
  with open("./data.json",'r',encoding='utf-8') as load_f:
    d = json.load(load_f)
    uid = d['CurUser']
  print('here', uid)
  fud = request.form["id"]
  print('there', fud)
  params_dict = {"uid":uid, "fud":fud, "si":si}
  print('ids', uid, fud)
  g.conn.execute(text("INSERT INTO Follows_User(Following_User_ID, Followed_User_Id,since) VALUES (:uid,:fud,:si)"), params_dict)
  g.conn.commit()
  return render_template('loginsucc.html')

@app.route('/createlist', methods=['POST'])
def listadd():
  name = request.form["Name"]
  description = request.form["Description"]
  si = str(datetime.now())
  with open("./data.json",'r',encoding='utf-8') as load_f:
    d = json.load(load_f)
    id = d["Listcount"]
  params_dict = {"id":id, "name":name, "description":description, "si":si}
  g.conn.execute(text("INSERT INTO List(List_Id, List_Name,List_Description, List_time) VALUES (:id, :name, :description,:si)"), params_dict)

  g.conn.commit()
  return render_template('loginsucc.html')

# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
