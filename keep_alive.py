from Flask import Flask, render_template
from threading import Thread

app = Flask(_name_)

@app.route('/')
def index():
  return "Alive"

def run():
  app.run(host='0.0.0.0',port-8080)

def keep_alive():
  t = Thread(target=run)
  t.start()

