#!/usr/bin/env python

import yaml
from jinja2 import Environment, FileSystemLoader

# Open input config file
with open("intakes.yaml", "r") as fyaml:
    data = yaml.safe_load(fyaml)

# Load jinja template
template = Environment(loader=FileSystemLoader(".")).get_template("template.j2")

i=1
# Generate one file per intake
for item in data.get("intakes", []):
    config = template.render(item)
    filename = f"/etc/rsyslog.d/{i}_{item['name'].lower()}.conf"
    # Écrire le contenu généré dans le fichier
    with open(filename, "w") as f:
        f.write(config)
    i=i+1

