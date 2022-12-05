#! /bin/bash

echo "Starting Entrypoint"
echo ""
echo "These Intakes have been set up"
echo "-----------------------------"

# Create rsyslog.conf
envsubst '${DISK_SPACE} ${MEMORY_MESSAGES}' <rsyslog.conf >/etc/rsyslog.conf

# Parse yaml intake file
python3 parse_yaml.py

i=1
while IFS=";" read -r rec_column1 rec_column2 rec_column3 || [ -n "$rec_column3" ]
do

  intake_name=$rec_column1
  port=$rec_column2
  intake_key=$rec_column3

  intake_name=$rec_column1 port=$rec_column2 intake_key=${rec_column3//[$'\t\r\n']} envsubst <template.conf >/etc/rsyslog.d/$i-$intake_name.conf
  i=$(($i+1))
  echo "Intake name: $intake_name"
  echo "Port used: $port"
  echo "Intake key: $intake_key"
  echo ""
done < intakes.csv

exec "$@"
