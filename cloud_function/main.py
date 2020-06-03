from google.cloud import storage
from dateutil.parser import parse
import re
import os
from google.cloud import bigquery
import requests

def main(data, context):
  print('Event ID: {}'.format(context.event_id))
  print('Event type: {}'.format(context.event_type))
  print('Bucket: {}'.format(data['bucket']))
  print('File: {}'.format(data['name']))
  print('Metageneration: {}'.format(data['metageneration']))
  print('Created: {}'.format(data['timeCreated']))
  print('Updated: {}'.format(data['updated']))

  bucket = data['bucket']
  filename = data['name']

  syslog_to_bq(bucket, filename)


def syslog_to_bq_manual():
  bucket = os.environ.get('BUCKET')
  filename = os.environ.get('FILENAME')
  syslog_to_bq(bucket, filename)

def process_syslog_to_csv(source, destination):

  with open(source, 'r') as f:
    with open(destination, 'a') as fp:
      for line in f:
        try:
          timestamp = parse_timestamp(line)
        except:
          timestamp = ''
        try:
          ip = extract_ip(line)
        except:
          ip = ''
        if ip:
          try:
            country = get_location_from_ip(ip)
          except:
            country = ''
        try:
          user = extract_user(line)
        except:
          user = ''

        fp.write(','.join([timestamp, ip, country, user, line]))

def syslog_to_bq(bucket, filename):

  download_blob(bucket, filename, filename)

  process_syslog_to_csv(filename, filename + '_processed.csv')
  bq_load('processed_logs', 'ssh_logs', filename + '_processed.csv')


def download_blob(bucket_name, source_blob_name, destination_file_name):

  storage_client = storage.Client()

  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(source_blob_name)
  blob.download_to_filename(destination_file_name)

  print(
      "Blob {} downloaded to {}.".format(
          source_blob_name, destination_file_name
      )
  )


def parse_timestamp(log_line):
  parsed_date = parse(log_line[0:20], fuzzy=True)
  return parsed_date.strftime(r"%Y-%m-%d %H:%M:%S")


def extract_ip(text):
  ip_match = re.search(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", text)
  return ip_match.group(0)

# ip location options:
# ->ipinfo - Trusted, rich data, e.g. company data. 50,000 searches a month free
#   ip2location - trusted, download db, then use offline. Paid and free option. Free option only has country, not region.
#   geoip2 - download db, then use offline.
#   various APIs
def get_location_from_ip(ip):
  r = requests.get(f"https://ipinfo.io/{ip}/geo?token=e467ca729258e4")
  ip_data = r.json()
  # {
  #    'ip': '46.208.110.220',
  #    'city': 'Chesham',
  #    'region': 'England',
  #    'country': 'GB',
  #    'loc': '51.7000,-0.6000',
  #    'postal': 'HP5',
  #    'timezone': 'Europe/London'
  # } 
  location = f"{ip_data['city']} {ip_data['region']}"
  return location

def extract_user(text):
  user_match = re.search(r"(?<=user )\w+", text)
  return user_match.group(0)


def bq_load(dataset, table, file):
  client = bigquery.Client()
  
  dataset_ref = client.dataset(dataset)
  table_ref = dataset_ref.table(table)
  job_config = bigquery.LoadJobConfig()
  job_config.source_format = bigquery.SourceFormat.CSV
  job_config.skip_leading_rows = 0
  job_config.autodetect = True
  
  with open(file, "rb") as source_file:
    job = client.load_table_from_file(source_file, table_ref, job_config=job_config)
  
  job.result()  # Waits for table load to complete.
  
  print("Loaded {} rows into {}:{}.".format(job.output_rows, dataset, table))
