FROM alpine:3.5

RUN apk add --no-cache \
    bash \
    python3

RUN pip3 install --upgrade pip
RUN pip3 install \
    ipwhois==0.15.1

ADD ./hosts.txt /hosts.txt
ENV HOSTSUPDATE_HOSTS_PATH=/hosts.txt

ADD ./bin /usr/local/bin
RUN chmod a+x /usr/local/bin/*
