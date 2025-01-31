#!/usr/bin/env python3

import io
import csv

records = []

with open('my_favorite_records_data.csv') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in csvreader:
        if row["Score (out of 10)"] != "N/A" and float(row["Score (out of 10)"]) >= 8:
            records.append(row)

# Sort records by score in descending order
records.sort(key=lambda row: float(row["Score (out of 10)"]) if row["Score (out of 10)"] != "N/A" else -1, reverse=True)

for row in records:
    print(f'{row["Band"]} - {row["Album Title"]} ({row["Score (out of 10)"]} / 10) {row["Notes"]}')
