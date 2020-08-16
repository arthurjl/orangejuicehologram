from google.cloud import storage

def upload_blob(source_file, destination_blob_name, bucket_name='orangejuicehologram.appspot.com'):
  """Uploads a file to the bucket."""
  # bucket_name = "your-bucket-name"
  # source_file_name = "local/path/to/file"
  # destination_blob_name = "storage-object-name"

  storage_client = storage.Client()
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(destination_blob_name)

  blob.upload_from_file(source_file)

  print(
    "File {} uploaded to {}.".format(
      source_file, destination_blob_name
    )
  )

def download_blob(gcloud_file, local, bucket_name='orangejuicehologram.appspot.com'):
  storage_client = storage.Client()
  bucket = storage_client.bucket(bucket_name)
  blob = bucket.blob(gcloud_file)

  blob.download_to_filename(local)

  print(
    "File {} downloaded to {}.".format(
      gcloud_file, local
    )
  )

if __name__ == "__main__":
  upload_blob(open('random.txt'), 'uploads/random.txt')
  download_blob('uploaxzcvxds/random.txt', 'yeet.txt')

