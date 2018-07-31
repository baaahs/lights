FROM python:2.7

RUN apt-get update
RUN apt-get install -y libavahi-compat-libdnssd1 ola-python
RUN pip install https://storage.googleapis.com/google-code-archive-downloads/v2/code.google.com/pybonjour/pybonjour-1.1.1.zip
RUN pip install CherryPy

ADD . lights
WORKDIR lights

ENTRYPOINT python go.py --simulator --host host.docker.internal

EXPOSE 9990/tcp
EXPOSE 5700/udp
EXPOSE 9000/udp
