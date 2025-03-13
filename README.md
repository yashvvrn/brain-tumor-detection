# Brain Tumor Detection

A Flask web application that uses deep learning to detect and classify brain tumors from MRI images.

## Features

- Upload MRI scan images
- Real-time tumor detection and classification
- Supports multiple tumor types:
  - Pituitary
  - Glioma
  - Meningioma
  - No Tumor (Normal)
- Confidence score for predictions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yashvvrn/brain-tumor-detection.git
cd brain-tumor-detection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download the model:
Place the trained model file `model.h5` in the `models/` directory.

4. Run the application:
```bash
python main.py
```

5. Open your browser and go to `http://localhost:5000`

## Tech Stack

- Python 3.x
- Flask
- TensorFlow
- Keras
- NumPy
- HTML/CSS

## Project Structure

```
BrainTumor/
├── main.py           # Main Flask application
├── models/           # Directory for ML models
├── templates/        # HTML templates
├── uploads/         # Temporary storage for uploaded images
└── requirements.txt # Project dependencies
```

## License

MIT License 