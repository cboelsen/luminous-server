FROM python:3.5-alpine as build

RUN apk update && \
    apk add git libffi-dev libjpeg-turbo-dev build-base && \
    rm /var/cache/* -rf

RUN pip install -U pip setuptools virtualenv && \
    rm /root/.cache/pip/wheels/* -rf

RUN virtualenv /var/lib/luminous

RUN /var/lib/luminous/bin/pip install tox pbr cffi wheel && \
	rm /root/.cache/pip/wheels/* -rf

COPY requirements.txt /tmp/

RUN /var/lib/luminous/bin/pip install -r /tmp/requirements.txt && \
    rm /root/.cache/pip/wheels/* -rf

COPY . /tmp/luminous-install-files
WORKDIR /tmp/luminous-install-files
RUN python setup.py bdist_wheel && /var/lib/luminous/bin/pip install dist/*

FROM python:3.5-alpine

RUN apk update && \
    apk add postgresql-dev libffi libjpeg-turbo supervisor && \
    rm /var/cache/* -rf

COPY --from=build /var/lib/luminous /var/lib/luminous

COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY run_server_dev.py /tmp/

ENTRYPOINT ["/var/lib/luminous/bin/python", "-u", "/tmp/run_server_dev.py"]
