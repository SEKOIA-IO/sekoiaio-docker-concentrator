#!/usr/bin/env python

import yaml
import csv

with open("intakes.yaml", "r") as fyaml:
    data = yaml.safe_load(fyaml)
    with open('intakes.csv', 'w') as fcsv:
        csvwriter = csv.writer(fcsv, delimiter=';')
        for intake in data['intakes']:
            csvwriter.writerow([intake['name'], intake['protocol'], intake['port'], intake['intake_key']])
