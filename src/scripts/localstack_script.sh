#!/bin/sh
echo "Initializing localstack s3"

awslocal s3api \
create-bucket --bucket mybucket \
--create-bucket-configuration LocationConstraint=eu-central-1 \
--region eu-central-1

awslocal ses verify-email-identity --email user-management-service@gmail.com
