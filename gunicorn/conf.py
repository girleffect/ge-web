workers = 3
keepalive = 5
loglevel = 'error'
pidfile = "/run/gunicorn/gunicorn.pid"
bind = 'unix:/run/gunicorn/gunicorn.sock' 
# umask working files (worker tmp files & unix socket) as 0o117 (i.e. chmod as
# 0o660) so that they are only read/writable by django and nginx users.
umask = '0o117'
worker_tmp_dir = "/run/gunicorn"
