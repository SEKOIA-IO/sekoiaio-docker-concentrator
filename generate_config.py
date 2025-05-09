#!/usr/bin/env python

import os
import re

import yaml
from jinja2 import Environment, FileSystemLoader


def is_intake_key(intake_key: str) -> re.Match[str] | None:
    pattern = "^[a-zA-Z0-9]{16}"
    return re.search(pattern, intake_key)


def activate_monitoring(item: dict[str, str]) -> None:
    to_print.append("Forwarder monitoring is active")
    to_print.append("Intake key: " + str(item["intake_key"]))
    to_print.append("")
    config = template_stats.render(item)
    filename = f"/etc/rsyslog.d/stats_{item['name']}.conf"
    with open(filename, "w") as f:
        f.write(config)

# Directory where configs will be saved
config_dir = "/etc/rsyslog.d/"

# Check if the directory exists; if not, attempt to create it
try:
    os.makedirs(config_dir, exist_ok=True)
except PermissionError:
    print(f"Permission denied: Cannot create or write to the directory '{config_dir}'.")
    print("Please run the script with appropriate permissions (e.g., using sudo).")
except Exception as e:
    print(f"An unexpected error occurred while accessing '{config_dir}': {e}")

# Generate main rsyslog config file
filename = f"/etc/rsyslog.conf"
with open(filename, "w") as f:
    f.write(Environment(loader=FileSystemLoader(".")).get_template("rsyslog.conf").render(env=os.environ))

# Open input config file
with open("intakes.yaml", "r") as fyaml:
    data = yaml.safe_load(fyaml)

# Load jinja template
template = Environment(loader=FileSystemLoader(".")).get_template("template.j2")
template_tls = Environment(loader=FileSystemLoader(".")).get_template("template_tls.j2")
template_stats = Environment(loader=FileSystemLoader(".")).get_template("stats_template.j2")
template_http = Environment(loader=FileSystemLoader(".")).get_template("template_http.j2")

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
elif region == "usa1":
    endpoint = "app.usa1.sekoia.io"
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
            f"ERROR: The Intake Key provided for Intake Name {item['name']} is incorrect. Exiting..."
        )
        exit(0)

    item["default_queue_size"] = round(int(os.getenv("MEMORY_MESSAGES", 100000)) / len(data.get("intakes")))
    item["endpoint"] = endpoint

    name_origin = item["name"]
    item["name"] = item["name"].replace(" ", "_").lower()

    if item.get("stats") is not None and item.get("stats") is not False:
        activate_monitoring(item)
        continue

    to_print.append("Intake name: " + str(name_origin))
    to_print.append("Intake key: " + str(item["intake_key"]))

    if item["protocol"].lower() == "http":
        if item.get("restpath") is None:
            item["restpath"] = "plain"
        if item.get("compress_level") is None:
            item["compress_level"] = "6"
        to_print.append("InputProtocol: " + str(item["input_protocol"]) + " Input_Port: " + str(item["port"]) + " Protocol: " + str(item["protocol"]) + " RestPath:" + str(item["restpath"]) + " CompressLevel: " + str(item["compress_level"]))
        config = template_http.render(item, env=os.environ)
    elif item["protocol"].lower() == "tls":
        config = template_tls.render(item, env=os.environ)
        to_print.append("Protocol: " + str(item["protocol"] + " Port: " + str(item["port"])))
    else:
        config = template.render(item, env=os.environ)
        to_print.append("Protocol: " + str(item["protocol"] + " Port: " + str(item["port"])))
    to_print.append("")
    filename = f"/etc/rsyslog.d/{i}_{item['name']}.conf"
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
