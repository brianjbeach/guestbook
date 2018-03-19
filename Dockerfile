FROM amazonlinux
ADD . /var/www/guestbook/
RUN yum install -y wget httpd mod_wsgi stress
RUN mv /var/www/guestbook/wsgi.conf /etc/httpd/conf.d/wsgi.conf
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python get-pip.py
RUN pip install -r /var/www/guestbook/requirements.txt
RUN useradd ec2-user
EXPOSE 80
CMD /usr/sbin/apachectl -D FOREGROUND
