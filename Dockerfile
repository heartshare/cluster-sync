FROM python:3.9.16-alpine3.16

WORKDIR /usr/src/app

RUN apk add rsync openssh

COPY docker/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN ssh-keygen -A -v
RUN echo "StrictModes no" >> /etc/ssh/sshd_config

COPY docker/id_rsa /root/.ssh/
COPY docker/id_rsa.pub /root/.ssh/
COPY docker/authorized_keys /root/.ssh/
RUN chmod 600 /tmp/id_rsa*

COPY sync.py ./

EXPOSE 22

CMD ["/usr/sbin/sshd", "&&", "python", "-u", "./sync.py"]
