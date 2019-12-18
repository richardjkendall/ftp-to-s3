import tempfile
import boto3
from botocore.exceptions import ClientError
import os
import logging

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import ThreadedFTPServer
from pyftpdlib.authorizers import DummyAuthorizer

logging.basicConfig(level=logging.INFO)

def upload_file_to_s3(file_name, bucket, object_name):
  s3 = boto3.client("s3")

  try:
    response = s3.upload_file(
      file_name,
      bucket,
      object_name
    )
  except ClientError as e:
    logging.error(e)
    return False
  return True

class S3UploadHandler(FTPHandler):

  tempdir = ""

  def on_connect(self):
    logging.info("%s:%s connected" % (self.remote_ip, self.remote_port))
    pass

  def on_disconnect(self):
    # do something when client disconnects
    logging.info("%s:%s disconnected" % (self.remote_ip, self.remote_port))
    pass

  def on_login(self, username):
    # do something when user login
    logging.info("%s:%s:%s login" % (self.remote_ip, self.remote_port, self.username))
    pass

  def on_logout(self, username):
    # do something when user logs out
    pass

  def on_file_sent(self, file):
    # do something when a file has been sent
    pass

  def on_file_received(self, file):
    # trigger S3 upload
    file_key = file.replace(self.tempdir, "", 1)
    if file_key[0] == "/":
      file_key = file_key[1:]
    logging.info("Got a file %s" % (file_key))
    if upload_file_to_s3(
      file_name = file,
      bucket = self.bucket_name,
      object_name = file_key
    ):
      logging.info("Uploaded file to S3")
      os.remove(file)
      logging.info("Removed file from container")
    else:
      logging.error("File failed to upload")
    pass

  def on_incomplete_file_sent(self, file):
    # do something when a file is partially sent
    pass

  def on_incomplete_file_received(self, file):
    # remove partially uploaded files
    os.remove(file)

def main():
  tempfolder = tempfile.TemporaryDirectory()
  tempfolder_name = os.path.realpath(tempfolder.name)
  logging.info("Temp dir will be: %s" % (tempfolder_name))
  
  authorizer = DummyAuthorizer()
  authorizer.add_user(os.environ["FTP_USERNAME"], os.environ["FTP_PASSWORD"], homedir=tempfolder_name, perm="elradfmwMT")

  handler = S3UploadHandler
  handler.authorizer = authorizer
  handler.tempdir = tempfolder_name
  handler.bucket_name = os.environ["BUCKET_NAME"]
  if "MASQ_ADDR" in os.environ:
    handler.masquerade_address = os.environ["MASQ_ADDR"]
  handler.passive_ports = range(60000, 61000)
  server = ThreadedFTPServer(("", 10021), handler)
  server.serve_forever()

def check_environment():
  """
  Make sure we have the environment variables we need to run
  Exit with code 1 if not
  """
  bad = False
  if "FTP_USERNAME" not in os.environ:
    bad = True
    logging.warning("Need FTP_USERNAME in environment")
  if "FTP_PASSWORD" not in os.environ:
    bad = True
    logging.warning("Need FTP_PASSWORD in environment")
  if "BUCKET_NAME" not in os.environ:
    bad = True
    logging.warning("Need BUCKET_NAME in environment")
  if bad:
    exit(1)

if __name__ == "__main__":
  check_environment()
  main()