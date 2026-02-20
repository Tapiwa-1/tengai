import redis
from rq import Connection, Worker

from app import create_app

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        redis_conn = redis.from_url(app.config["REDIS_URL"])
        with Connection(redis_conn):
            worker = Worker(["default"])
            worker.work()
