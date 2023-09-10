import multiprocessing
import os
from datetime import datetime

# 监听内网端口
bind = '127.0.0.1:7872'
# 工作目录
chdir = './'
# 并行工作进程数
# workers = multiprocessing.cpu_count()
workers = 2
# 指定每个工作者的线程数
threads = 4
# 监听队列
backlog = 512
# 超时时间
timeout = 120
# 设置守护进程,将进程交给 supervisor 管理；如果设置为 True 时，supervisor 启动日志为：
# gave up: fastapi_server entered FATAL state, too many start retries too quickly
# 则需要将此改为: False
daemon = False
# 工作模式协程
worker_class = 'uvicorn.workers.UvicornWorker'
# 设置最大并发量
worker_connections = 100

# 设置进程文件目录
log_dir = "./flagged"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
pidfile = './flagged/gunicorn.pid'
# 设置访问日志和错误信息日志路径
accesslog = './logs/websearchaio_access_{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H'))
errorlog = './logs/websearchaio_error_{}.log'.format(datetime.now().strftime('%Y-%m-%d_%H'))
# 如果supervisor管理gunicorn
# errorlog = '-'
# accesslog = '-'
# 设置gunicron访问日志格式，错误日志无法设置
access_log_format = '%(t)s %(p)s %(h)s "%(r)s" %(s)s %(L)s %(b)s %(f)s" "%(a)s"'
# 设置这个值为true 才会把打印信息记录到错误日志里
capture_output = True
# 设置日志记录水平
loglevel = 'info'

# python程序
# pythonpath = ''

# 启动 gunicorn -c gunicorn.py api:app
# 查看进程树 pstree -ap|grep gunicorn
# 终止 kill -9 (pid)
