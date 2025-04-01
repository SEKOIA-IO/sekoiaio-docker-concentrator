#! /bin/bash

echo "Starting Entrypoint"
echo ""

# Parse yaml intake file
python3 generate_config.py
ret=$?
if [ $ret -ne 0 ]; then
    # If the the YAML is not as expected
    echo -e "\n\nError in the file intakes.yaml. Verify is as expected and rerun the container."
    exit 1
fi

exec "$@"
