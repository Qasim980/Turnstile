import os
import socket

from flask import Flask, render_template
import redis

app = Flask(__name__)
r = redis.Redis(
    host=os.environ.get('REDIS_HOST', 'redis'),
    port=int(os.environ.get('REDIS_PORT', 6379)),
)

APP_NAME = 'Turnstile'


@app.context_processor
def inject_globals():
    # Container hostname = container ID, handy for seeing which container served you
    return {'app_name': APP_NAME, 'hostname': socket.gethostname()}


@app.route('/')
def hello_world():
    return render_template('home.html')


@app.route('/count')
def count():
    try:
        visits = r.incr('visits')
        error = None
    except redis.exceptions.ConnectionError:
        visits, error = None, 'Redis is unreachable right now. Is the redis container up?'
    return render_template('count.html', visits=visits, error=error)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)
