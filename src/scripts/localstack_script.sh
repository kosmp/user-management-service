#!/bin/sh
echo "Initializing localstack s3"

awslocal s3api \
create-bucket --bucket $S3_BUCKET_NAME \
--create-bucket-configuration LocationConstraint=eu-central-1 \
--region eu-central-1
