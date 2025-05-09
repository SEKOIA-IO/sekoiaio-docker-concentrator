# Use the latest Alpine Linux base image
FROM alpine:3.21

# Update the package list and install required packages
RUN apk update && apk add --no-cache \
    rsyslog \
    rsyslog-tls \
    rsyslog-http \
    rsyslog-imrelp \
    rsyslog-omrelp \
    gettext \
    python3 \
    py3-yaml \
    py3-jinja2 \
    wget

RUN wget -O /SEKOIA-IO-intake.pem https://app.sekoia.io/assets/files/SEKOIA-IO-intake.pem

# Setting default environement variables
ENV DISK_SPACE=32g
ENV MEMORY_MESSAGES=100000
ENV REGION=FRA1

# Setting up Rsyslog
RUN rm -rf /etc/rsyslog.d/50-default.conf

COPY generate_config.py generate_config.py
COPY rsyslog-imstats /etc/logrotate.d/rsyslog-imstats
COPY rsyslog.conf rsyslog.conf
COPY entrypoint.sh entrypoint.sh
COPY intakes.yaml intakes.yaml
COPY template.j2 template.j2
COPY template_tls.j2 template_tls.j2
COPY template_http.j2 template_http.j2
COPY stats_template.j2 stats_template.j2

RUN chmod +x entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["rsyslogd", "-n"]
