import multiprocessing
bind = "0.0.0.0:8000"

# 2–4 x CPU cores is typical; start with 3 as you had
workers = 3
worker_class = "sync"

# Keep these modest so idle TCP probes don't hang a worker
timeout = 30            # hard kill after 30s
graceful_timeout = 30
keepalive = 2           # close idle connections quickly

# Logging (stdout/stderr go to docker logs)
accesslog = "-"
errorlog = "-"
loglevel = "info"
