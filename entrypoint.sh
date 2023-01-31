#! /bin/bash

echo "Starting Entrypoint"
echo ""
echo "These Intakes have been set up"
echo "-----------------------------"

# Create rsyslog.conf
envsubst '${DISK_SPACE} ${MEMORY_MESSAGES}' <rsyslog.conf >/etc/rsyslog.conf

# Parse yaml intake file
python3 parse_yaml.py
ret=$?
if [ $ret -ne 0 ]; then
    # If the the YAML is not as expected
    echo -e "\n\nError in the file intakes.yaml. Verify is as expected and rerun the container."
    exit 1
fi

i=1
while IFS=";" read -r rec_column1 rec_column2 rec_column3 rec_column4 || [ -n "$rec_column4" ]
do
    intake_name=$(echo "${rec_column1// /-}" | awk '{print tolower($0)}')
    protocol=$(echo "$rec_column2" | awk '{print tolower($0)}')
    port=$rec_column3
    intake_key=$rec_column4

    intake_name=$intake_name protocol=$protocol port=$port intake_key=${intake_key//[$'\t\r\n']} envsubst <template.conf >/etc/rsyslog.d/$i-$intake_name.conf
    i=$(($i+1))
    echo "Intake name: $intake_name"
    echo "Protocol: $protocol"
    echo "Port: $port"
    echo "Intake key: $intake_key"
    echo ""
done < intakes.csv

exec "$@"
