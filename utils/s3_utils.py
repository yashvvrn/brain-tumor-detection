import boto3
import os
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)

class S3Handler:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.getenv('AWS_BUCKET_NAME')

    def download_file(self, file_key, local_path):
        """Download a file from S3 to local storage"""
        try:
            self.s3_client.download_file(self.bucket_name, file_key, local_path)
            logger.info(f"Successfully downloaded {file_key} to {local_path}")
            return True
        except ClientError as e:
            logger.error(f"Error downloading {file_key}: {e}")
            return False

    def upload_file(self, file_path, file_key):
        """Upload a file from local storage to S3"""
        try:
            self.s3_client.upload_file(file_path, self.bucket_name, file_key)
            logger.info(f"Successfully uploaded {file_path} to {file_key}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading {file_path}: {e}")
            return False

    def get_file_url(self, file_key, expiration=3600):
        """Generate a temporary URL for accessing a file"""
        try:
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(f"Error generating URL for {file_key}: {e}")
            return None

    def delete_file(self, file_key):
        """Delete a file from S3"""
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            logger.info(f"Successfully deleted {file_key}")
            return True
        except ClientError as e:
            logger.error(f"Error deleting {file_key}: {e}")
            return False 