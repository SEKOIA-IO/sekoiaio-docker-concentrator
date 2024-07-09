#!/usr/bin/env python

import os
import re

import yaml
from jinja2 import Environment, FileSystemLoader


def is_intake_key(intake_key: str) -> re.Match[str] | None:
    pattern = "^[a-zA-Z0-9]{16}"
    return re.search(pattern, intake_key)


# Open input config file
with open("intakes.yaml", "r") as fyaml:
    data = yaml.safe_load(fyaml)

# Load jinja template
template = Environment(loader=FileSystemLoader(".")).get_template("template.j2")
template_tls = Environment(loader=FileSystemLoader(".")).get_template("template_tls.j2")

# Identify the region
region = os.getenv("REGION")
if region:
    region = region.lower()
if region == "fra2":
    endpoint = "fra2.app.sekoia.io"
elif region == "mco1":
    endpoint = "mco1.app.sekoia.io"
elif region == "uae1":
    endpoint = "app.uae1.sekoia.io"
else:
    endpoint = "intake.sekoia.io"

i = 1
to_print = []
to_print.append("These Intakes have been set up")
to_print.append("-----------------------------")

# Generate one file per intake
for item in data.get("intakes", []):
    if not is_intake_key(item["intake_key"]):
        print(
            f"ERROR: The Intake Key provided for Intake Name {item['name'].lower()} is incorrect. Exiting..."
        )
        exit(0)

    to_print.append("Intake name: " + str(item["name"].lower()))
    to_print.append("Protocol: " + str(item["protocol"]))
    to_print.append("Port: " + str(item["port"]))
    to_print.append("Intake key: " + str(item["intake_key"]))
    to_print.append("")
    item["endpoint"] = endpoint

    if item["protocol"].lower() == "tls":
        config = template_tls.render(item)
    else:
        config = template.render(item)
    filename = f"/etc/rsyslog.d/{i}_{item['name'].lower()}.conf"
    # Écrire le contenu généré dans le fichier
    with open(filename, "w") as f:
        f.write(config)
    i = i + 1

# Check additional conf
XTENDED_CONF = "/extended_conf/"
if os.path.exists(XTENDED_CONF):
    for file in os.listdir(XTENDED_CONF):
        if file.endswith(".conf"):
            to_print.append(
                "Detected an additonal intake defined in file {}".format(file)
            )

for line in to_print:
    print(line)
