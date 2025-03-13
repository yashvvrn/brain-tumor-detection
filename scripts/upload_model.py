import os
from dotenv import load_dotenv
from utils.s3_utils import S3Handler

def upload_model():
    # Load environment variables
    load_dotenv()
    
    # Initialize S3 handler
    s3_handler = S3Handler()
    
    # Model path
    model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models', 'model.h5')
    
    # Check if model exists
    if not os.path.exists(model_path):
        print(f"Error: Model file not found at {model_path}")
        return
    
    # Upload model
    print("Uploading model to S3...")
    if s3_handler.upload_file(model_path, 'models/model.h5'):
        print("Model uploaded successfully!")
    else:
        print("Failed to upload model")

if __name__ == "__main__":
    upload_model() 