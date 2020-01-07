# ftp-to-s3

A Python server which uploads files received over FTP to AWS S3.  Builds on pyftpdlib.

## Configuration

Expects the following environment variables to be specified

|Variable|Purpose|
|---|---|
|FTP_USERNAME|Username which will be accepted by the server|
|FTP_PASSWORD|Password which will be accepted by the server|
|BUCKET_NAME|S3 Bucket which the files will be uploaded to|

## Behaviour

Server will accept any login which matches the username and password passed to it in environment variables.  Any files uploaded will be uploaded to S3 following the same folder structure as the FTP upload

e.g. if you upload a file to /folder1/folder2/file.txt on the FTP server then it will be uploaded to

s3://BUCKET_NAME/folder1/folder2/file.txt

Existing files will be ovewritten.

Files are removed from the container filesystem after a valid upload.

## Running (via Docker)

This can be packaged as a Docker image and it is available on Docker hub here:

Because of the way the FTP protocol works you will need to run this in ``host`` network mode e.g.

```sh
docker run --name testftp \
-d \
--network host \
-e FTP_USERNAME=rjk \
-e FTP_PASSWORD=123 \
-e BUCKET_NAME=test \
richardjkendall/ftp-to-s3
```

I also recommend only using FTP passive (PASV) mode.

## To-do

Extend authentication to use a better approach that a single username and password accepted via environment variables
