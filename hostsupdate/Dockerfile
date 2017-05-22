FROM alpine:3.5

RUN apk add --no-cache \
    bash \
    python3

RUN pip3 install --upgrade pip
RUN pip3 install \
    berserker-resolver==2.0.1 \
    dnspython==1.15.0 \
    dnspython3==1.15.0

ADD ./hosts.txt /hosts.txt
ENV HOSTSUPDATE_HOSTS_PATH=/hosts.txt

ADD ./bin /usr/local/bin
RUN chmod a+x /usr/local/bin/*
