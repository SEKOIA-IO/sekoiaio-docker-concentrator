FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    rsyslog \
    rsyslog-gnutls \
    gettext-base \
    python3 \
    python3-yaml \
    python3-jinja2 \
    wget

RUN wget -O /SEKOIA-IO-intake.pem https://app.sekoia.io/assets/files/SEKOIA-IO-intake.pem

# Setting default environement variables
ENV DISK_SPACE=32g
ENV MEMORY_MESSAGES=100000
ENV REGION=FRA1

# Setting up Rsyslog
RUN rm -rf /etc/rsyslog.d/50-default.conf

COPY generate_config.py generate_config.py
COPY rsyslog.conf rsyslog.conf
COPY entrypoint.sh entrypoint.sh
COPY intakes.yaml intakes.yaml
COPY template.j2 template.j2

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["rsyslogd", "-n"]
