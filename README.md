# hackday-logfellas
The result of a day's work trying to create a data pipeline for syslog data.

## terraform/
A work in progress. Creates BigQuery dataset and table with schema. Would be extended to create the storage bucket and cloud function.

## cloud_function/
Python code to run as a GCP Cloud Function, triggered by the upload of a file to a particular storage bucket. The code downloads the log file and reads line by line, extracting a timestamp, IP address and username (if available) using fairly crude means. It also looks up the IP address to obtain a geographical location. It writes these results to a CSV file which can then be loaded into BigQuery.

During the day we were unable to get the Cloud Function working. The BQ upload also had issues with the schema which need addressing. However it was possible to run the function locally, and upload to BQ with an auto-detected schema (adding a header row to the CSV manually).

## sample_data/
The 2000 lines of OpenSSH logs we used to test the pipeline.

## Results
We were able to use the data loaded into BigQuery to produce a map of the locations of failed logins, using Google Data Studio. Further analysis could be performed on the user names identified, and on the meanings of the log messages, now that the data is available in BigQuery.
