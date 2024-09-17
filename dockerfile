FROM python:3.10


COPY . /SecureRS

RUN apt-get update -y 
RUN apt-get install borgbackup -y

WORKDIR /SecureRS

RUN pip3 install -r requirements.txt
RUN python manage.py makemigrations pde; exit 0
RUN python manage.py migrate; exit 0
RUN echo "from django.contrib.auth.models import User; User.objects.create_superuser('admin', 'admin@example.com', 'admin')" | python manage.py shell ; exit 0
CMD ["python", "manage.py" ,"runsslserver", "0.0.0.0:8443"]


EXPOSE 8443/tcp

#MAINTAINER Avinash tashan.avi@gmail.com