from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
  return "sudo caffeinate -u -t 99999"

def run():
  app.run(host="0.0.0.0", port=9000)

def caffeinate():
  t = Thread(target = run)
  t.start()