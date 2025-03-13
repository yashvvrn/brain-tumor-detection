from flask import Flask, render_template, request, send_from_directory
from tensorflow.keras.models import load_model
from keras.preprocessing.image import load_img, img_to_array
from werkzeug.utils import secure_filename
import numpy as np
import os
import logging
from pathlib import Path
from dotenv import load_dotenv
from utils.s3_utils import S3Handler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Initialize S3 handler
s3_handler = S3Handler()

# Configure constants
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
IMAGE_SIZE = 128
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload folder if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(parents=True, exist_ok=True)

# Load model safely
try:
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models', 'model.h5')
    # Download model from S3 if it doesn't exist locally
    if not os.path.exists(model_path):
        logger.info("Downloading model from S3...")
        s3_handler.download_file('models/model.h5', model_path)
    
    model = load_model(model_path)
    class_labels = ['pituitary', 'glioma', 'notumor', 'meningioma']
    logger.info("Model loaded successfully")
except Exception as e:
    logger.error(f"Error loading model: {e}")
    raise

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def predict_tumor(image_path):
    try:
        img = load_img(image_path, target_size=(IMAGE_SIZE, IMAGE_SIZE))
        img_array = img_to_array(img) / 255.0
        img_array = np.expand_dims(img_array, axis=0)

        predictions = model.predict(img_array)
        predicted_class_index = np.argmax(predictions, axis=1)[0]
        confidence_score = np.max(predictions, axis=1)[0]

        return (
            "No Tumor" if class_labels[predicted_class_index] == 'notumor' 
            else f"Tumor: {class_labels[predicted_class_index]}", 
            confidence_score
        )
    except Exception as e:
        logger.error(f"Error during prediction: {e}")
        return "Error during prediction", 0.0

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return render_template('index.html', error="No file uploaded")
        
        file = request.files['file']
        if file.filename == '':
            return render_template('index.html', error="No file selected")
        
        if not allowed_file(file.filename):
            return render_template('index.html', error="Invalid file type. Please upload a PNG or JPG image.")
        
        try:
            filename = secure_filename(file.filename)
            file_location = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_location)
            logger.info(f"File saved successfully: {filename}")

            # Upload to S3
            s3_key = f'uploads/{filename}'
            if s3_handler.upload_file(file_location, s3_key):
                # Get temporary URL for the uploaded file
                file_url = s3_handler.get_file_url(s3_key)
                
                result, confidence = predict_tumor(file_location)
                
                # Clean up local file
                os.remove(file_location)
                
                return render_template('index.html', 
                                     result=result, 
                                     confidence=f"{confidence*100:.2f}%", 
                                     file_path=file_url)
            else:
                return render_template('index.html', error="Error uploading file to storage")
                
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return render_template('index.html', error="Error processing file")

    return render_template('index.html', result=None)

@app.route('/uploads/<filename>')
def get_uploaded_file(filename):
    try:
        s3_key = f'uploads/{filename}'
        file_url = s3_handler.get_file_url(s3_key)
        if file_url:
            return redirect(file_url)
        return "File not found", 404
    except Exception as e:
        logger.error(f"Error serving file {filename}: {e}")
        return "File not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
