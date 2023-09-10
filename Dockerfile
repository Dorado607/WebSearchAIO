# 建立python3.10.12环境
FROM python:3.10.12
# 作者
LABEL maintainer="cloud <cloud.hhk@gmail.com>"
# 设置时区
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone
# 在容器内创建WebSearchAIO文件夹
RUN mkdir -p /home/WebSearchAIO
# 安装python环境
WORKDIR /home
COPY requirements.txt /home/requirements.txt
RUN pip install -r requirements.txt -i https://mirrors.cloud.tencent.com/pypi/simple
# 拷贝代码
WORKDIR /home/WebSearchAIO
COPY . /home/WebSearchAIO
# 为启动脚本添加可执行权限
RUN chmod +x /home/WebSearchAIO/start_websearchaio_in_docker.sh
# 说明后端端口
EXPOSE 7872
# 启动后端服务
# CMD ["bash", "/home/AIL-is-now-now/backend/AILawyer/scripts/start_backend_in_test_dev_docker.sh"]
# 启动后端服务 这段代码目前移到了docker-compose中了，所以注释掉了，但是清先保留着，后续调试用
# CMD ["gunicorn","-w","1","--threads","4","--worker-connections","1000","-b","0.0.0.0:8997","AILawyer.wsgi:application"]
# CMD ["bash /home/AIL-is-now-now/backend/AILawyer/scripts/start_backend_in_test_dev.sh"]
