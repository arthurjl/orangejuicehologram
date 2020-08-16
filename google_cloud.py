import binascii
import collections
import datetime
import hashlib
import sys

from backend.video_converter import convertVideo

# pip install google-auth
from google.oauth2 import service_account
# pip install six
import six
from six.moves.urllib.parse import quote

from google.cloud import storage

def generate_signed_url(object_name, service_account_file='secret/orangejuicehologram-1fa0acc47040.json', bucket_name='orangejuicehologram.appspot.com',
                        subresource=None, expiration=604800, http_method='GET',
                        query_parameters=None, headers=None):

  if expiration > 604800:
    print('Expiration Time can\'t be longer than 604800 seconds (7 days).')
    sys.exit(1)

  escaped_object_name = quote(six.ensure_binary(object_name), safe=b'/~')
  canonical_uri = '/{}'.format(escaped_object_name)

  datetime_now = datetime.datetime.utcnow()
  request_timestamp = datetime_now.strftime('%Y%m%dT%H%M%SZ')
  datestamp = datetime_now.strftime('%Y%m%d')

  google_credentials = service_account.Credentials.from_service_account_file(
      service_account_file)
  client_email = google_credentials.service_account_email
  credential_scope = '{}/auto/storage/goog4_request'.format(datestamp)
  credential = '{}/{}'.format(client_email, credential_scope)

  if headers is None:
    headers = dict()
  host = '{}.storage.googleapis.com'.format(bucket_name)
  headers['host'] = host

  canonical_headers = ''
  ordered_headers = collections.OrderedDict(sorted(headers.items()))
  for k, v in ordered_headers.items():
    lower_k = str(k).lower()
    strip_v = str(v).lower()
    canonical_headers += '{}:{}\n'.format(lower_k, strip_v)

  signed_headers = ''
  for k, _ in ordered_headers.items():
    lower_k = str(k).lower()
    signed_headers += '{};'.format(lower_k)
  signed_headers = signed_headers[:-1]  # remove trailing ';'

  if query_parameters is None:
    query_parameters = dict()
  query_parameters['X-Goog-Algorithm'] = 'GOOG4-RSA-SHA256'
  query_parameters['X-Goog-Credential'] = credential
  query_parameters['X-Goog-Date'] = request_timestamp
  query_parameters['X-Goog-Expires'] = expiration
  query_parameters['X-Goog-SignedHeaders'] = signed_headers
  if subresource:
    query_parameters[subresource] = ''

  canonical_query_string = ''
  ordered_query_parameters = collections.OrderedDict(
    sorted(query_parameters.items()))
  for k, v in ordered_query_parameters.items():
    encoded_k = quote(str(k), safe='')
    encoded_v = quote(str(v), safe='')
    canonical_query_string += '{}={}&'.format(encoded_k, encoded_v)
  canonical_query_string = canonical_query_string[:-1]  # remove trailing '&'

  canonical_request = '\n'.join([http_method,
                                  canonical_uri,
                                  canonical_query_string,
                                  canonical_headers,
                                  signed_headers,
                                  'UNSIGNED-PAYLOAD'])

  canonical_request_hash = hashlib.sha256(
      canonical_request.encode()).hexdigest()

  string_to_sign = '\n'.join(['GOOG4-RSA-SHA256',
                              request_timestamp,
                              credential_scope,
                              canonical_request_hash])

  # signer.sign() signs using RSA-SHA256 with PKCS1v15 padding
  signature = binascii.hexlify(
    google_credentials.signer.sign(string_to_sign)
  ).decode()

  scheme_and_host = '{}://{}'.format('https', host)
  signed_url = '{}{}?{}&x-goog-signature={}'.format(
    scheme_and_host, canonical_uri, canonical_query_string, signature)

  return signed_url


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
  # upload_blob(open('random.txt'), 'uploads/random.txt')
  x = generate_signed_url('uploads/video-1597551723.mp4')
  print(x)
  # convertVideo(x, 500)