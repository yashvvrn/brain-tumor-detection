import os
from dotenv import load_dotenv
from utils.s3_utils import S3Handler

def test_s3_connection():
    # Load environment variables
    load_dotenv()
    
    # Initialize S3 handler
    s3_handler = S3Handler()
    
    # Test bucket access
    try:
        # Try to list objects in the bucket
        response = s3_handler.s3_client.list_objects_v2(
            Bucket=s3_handler.bucket_name,
            MaxKeys=1
        )
        print("✅ Successfully connected to S3!")
        print(f"Bucket name: {s3_handler.bucket_name}")
        print(f"Region: {s3_handler.s3_client.meta.region_name}")
        return True
    except Exception as e:
        print("❌ Failed to connect to S3:")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_s3_connection() 