
import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
backlog = 2048

workers = int(os.getenv('WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 50

timeout = 120
keepalive = 2
graceful_timeout = 30

accesslog = "-"
errorlog = "-"
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

proc_name = 'cryptobot-supremo'

daemon = False
pidfile = '/tmp/gunicorn.pid'
user = None
group = None
tmp_upload_dir = None

keyfile = os.getenv('SSL_KEY_PATH')
certfile = os.getenv('SSL_CERT_PATH')

preload_app = True
sendfile = True

def on_starting(server):
    server.log.info("Starting CryptoBot Supremo server...")

def on_reload(server):
    server.log.info("Reloading CryptoBot Supremo server...")

def worker_int(worker):
    worker.log.info("Worker received INT or QUIT signal")

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def post_worker_init(worker):
    worker.log.info("Worker initialized (pid: %s)", worker.pid)

def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")
