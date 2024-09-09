FROM python:3.7

ADD . /SecureRS

WORKDIR /SecureRS

RUN chmod +x /install.sh
CMD [ "./install.sh" ]


EXPOSE 443/tcp

#MAINTAINER Avinash tashan.avi@gmail.com