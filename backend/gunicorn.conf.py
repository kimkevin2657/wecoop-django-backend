import multiprocessing

bind = "0.0.0.0:8000"
workers = multiprocessing.cpu_count() * 2 + 1
accesslog = "-"
access_log_format = '"%(r)s" %(s)s %(b)s "%(h)s" "%(L)s" "%(u)s"'
wsgi_app = "config.wsgi:application"
