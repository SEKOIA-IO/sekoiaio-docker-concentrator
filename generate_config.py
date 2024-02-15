#!/usr/bin/env python

import yaml
from jinja2 import Environment, FileSystemLoader
import os

# Open input config file
with open("intakes.yaml", "r") as fyaml:
    data = yaml.safe_load(fyaml)

# Load jinja template
template = Environment(loader=FileSystemLoader(".")).get_template("template.j2")

# Identify the region
region = os.getenv("REGION").lower()
if region == "fra2":
    endpoint = "fra2.app.sekoia.io"
elif region == "mco1":
    endpoint = "mco1.app.sekoia.io"
elif region == "uae1":
    endpoint = "app.uae1.sekoia.io"
else:
    endpoint = "intake.sekoia.io"

i=1
# Generate one file per intake
for item in data.get("intakes", []):
    print("Intake name: " + str(item["name"].lower()))
    print("Protocol: " + str(item["protocol"]))
    print("Port: " + str(item["port"]))
    print("Intake key: " + str(item["intake_key"]))
    print("")
    item["endpoint"] = endpoint
    config = template.render(item)
    filename = f"/etc/rsyslog.d/{i}_{item['name'].lower()}.conf"
    # Écrire le contenu généré dans le fichier
    with open(filename, "w") as f:
        f.write(config)
    i=i+1

