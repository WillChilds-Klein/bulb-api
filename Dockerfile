FROM lambci/lambda:build

RUN echo -e $'\
[main] \n\
keepcache=0 \n\
releasever=2015.09 \
' > /etc/yum.conf

RUN yum clean all && \
    yum -y install python27-pip python27-devel python27-virtualenv vim postgresql postgresql-devel mysql mysql-devel gcc && \
    pip install -U pip && \
    pip install -U awscli virtualenv

WORKDIR /var/bulb

COPY ./requirements.txt requirements.txt

RUN virtualenv /var/venv && \
    source /var/venv/bin/activate && \
    pip install -U pip && \
    pip install -r requirements.txt && \
    deactivate

COPY ./zappa_settings.json zappa_settings.json
COPY ./run.py run.py
COPY scripts/docker/venv_exec /bin/venv_exec

EXPOSE 8080

ENTRYPOINT ["/bin/venv_exec"]

CMD ["./run.py", "local"]
