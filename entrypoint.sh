#! /bin/sh
set -e

echo "Starting Entrypoint"
echo ""

# Create rsyslog.conf
envsubst '${DISK_SPACE} ${MEMORY_MESSAGES}' <rsyslog.conf >/etc/rsyslog.conf

# Parse yaml intake file
python3 generate_config.py

exec "$@"
