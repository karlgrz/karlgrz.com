#!/usr/bin/env python3

import io
import csv

def format_csv_data(r):
	si = io.StringIO()
	cw = csv.writer(si)
	sorted_data = sorted(r.json(), key=sort_by)
	cw.writerow(
		[
			"environment",
			"region",
			"name",
			"dns",
			"id",
			"type",
			"platform",
			"launchTime",
			"imageId",
			"imageName",
			"imageCreationDate",
			"lifecycle",
			"state",
			"flagged",
		]
	)
	for row in sorted_data:
		cw.writerow(
			[
				row["environment"],
				row["region"],
				row["name"],
				row["dns"],
				row["id"],
				row["type"],
				row["platform"],
				row["launchTime"],
				row["imageId"],
				row["imageName"],
				row["imageCreationDate"],
				row["lifecycle"],
				row["state"],
				row["flagged"],
			]
		)
	return si

with open('my_favorite_records_data.csv') as csvfile:
    csvreader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
    for row in csvreader:
        print(f'{row["Band"]} - {row["Album Title"]} ({row["Score (out of 10)"]} / 10)')