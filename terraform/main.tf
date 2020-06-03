provider "google" {
  project     = "${var.gcloud_project_id}"
}

resource "google_bigquery_dataset" "dataset" {
  dataset_id                  = "processed_log"
  friendly_name               = "logfellas dataset"
  description                 = "Geolocation of users IP address"
  location                    = "europe-west2"
}

resource "google_bigquery_table" "dataset" {
  dataset_id = "processed_log"
  table_id   = "ssh_log"

  schema = <<EOF
  [
    {
      "name": "timestamp",
      "type": "TIMESTAMP",
      "mode": "NULLABLE",
      "description": "Log timestamp"
    },
    {
      "name": "ip_address",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "IP address if found in the log"
    },
    {
      "name": "country",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "Country of access (if available)"
    },
    {
      "name": "user",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "Username if found in the log"
    },
    {
      "name": "log_message",
      "type": "STRING",
      "mode": "NULLABLE",
      "description": "Remainder of the log message"
    }
  ]
EOF

}
