# SpeciesNet Image Classification API

A complete, backend-only Python Flask application that provides a REST API for wildlife image classification using SpeciesNet.

## Overview

This API service receives images via HTTP requests, processes them using Google's SpeciesNet ensemble models, and returns detailed JSON predictions. SpeciesNet combines object detection (MegaDetector) and species classification to identify wildlife in camera trap images.

## Features

- **Pure API Service**: Backend-only, no HTML pages served
- **SpeciesNet Integration**: Uses the complete SpeciesNet ensemble (detector + classifier + geofencing)
- **Robust Error Handling**: Comprehensive validation and error responses
- **File Security**: Secure filename handling and temporary file cleanup
- **GPU Acceleration**: Automatically uses CUDA if available
- **Multiple Formats**: Supports common image formats (JPG, PNG, TIFF, etc.)

## API Endpoints

### `POST /classify`

Upload an image for species classification.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Field: `image` (file upload)

**Supported Formats:**
- JPG, JPEG, PNG, GIF, BMP, TIFF, WEBP

**Response:**
- Success (200): JSON with SpeciesNet predictions
- Error (400): Invalid request or file type
- Error (500): Model execution failure

**Example:**
```bash
curl -X POST -F "image=@elephant.jpg" http://localhost:5000/classify
```

**Sample Response:**
```json
{
  "predictions": [
    {
      "classifications": {
        "classes": [
          "55631055-3e0e-4b7a-9612-dedebe9f78b0;mammalia;proboscidea;elephantidae;loxodonta;africana;african elephant"
        ],
        "scores": [0.9923]
      },
      "detections": [
        {
          "bbox": [0.7041, 0.4766, 0.1108, 0.125],
          "category": "1",
          "conf": 0.9353,
          "label": "animal"
        }
      ],
      "filepath": "/path/to/uploaded/image.jpg",
      "model_version": "4.0.1a",
      "prediction": "55631055-3e0e-4b7a-9612-dedebe9f78b0;mammalia;proboscidea;elephantidae;loxodonta;africana;african elephant",
      "prediction_score": 0.9923,
      "prediction_source": "classifier"
    }
  ]
}
```

### `GET /health`

Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "SpeciesNet Image Classification API",
  "upload_folder": "api_uploads",
  "allowed_extensions": ["jpg", "png", "gif", ...]
}
```

### `GET /`

API information and usage instructions.

## Installation & Setup

### Prerequisites

1. **Python 3.9-3.12** with pip
2. **CUDA-compatible GPU** (optional but recommended)
3. **SpeciesNet dependencies** (automatically installed)

### Installation

1. Clone the repository with SpeciesNet:
```bash
git clone https://github.com/google/cameratrapai.git
cd cameratrapai
```

2. Install SpeciesNet in development mode:
```bash
pip install -e .
```

3. Install Flask:
```bash
pip install flask werkzeug
```

4. Ensure numpy compatibility:
```bash
pip install "numpy<2.0"
```

### Running the API

```bash
python app.py
```

The API will start on `http://0.0.0.0:5000` (accessible from all network interfaces).

## Model Information

**SpeciesNet v4.0.1a** (Always-crop model):
- **Detector**: MegaDetector v5 for object detection
- **Classifier**: EfficientNet V2 M trained on 65M+ camera trap images
- **Species Coverage**: 2000+ animal species and higher-level taxa
- **Geographic Coverage**: Global, with optional geofencing
- **Non-animal Classes**: Blank images, humans, vehicles

## Performance

- **Model Loading**: ~2.5 seconds on GPU (one-time initialization)
- **Inference Speed**: ~7 seconds per image on GPU
- **Memory Usage**: ~4GB GPU memory when loaded
- **Accuracy**: State-of-the-art for camera trap image classification

## Error Handling

The API provides detailed error responses for common issues:

- **400 Bad Request**: Missing image field, invalid file type, no file selected
- **413 Request Entity Too Large**: File size exceeds limits
- **500 Internal Server Error**: Model execution failures, JSON parsing errors

## Security Considerations

- File uploads are temporarily stored and immediately deleted after processing
- Filenames are sanitized using `secure_filename`
- No persistent file storage on server
- Input validation for file types and request format

## Configuration

The application can be configured by modifying these variables in `app.py`:

```python
UPLOAD_FOLDER = 'api_uploads'  # Temporary upload directory
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
```

## Logging

The application logs all operations including:
- File uploads and processing
- Model execution commands
- Success/failure outcomes
- Cleanup operations

## Production Deployment

For production use:

1. Use a production WSGI server (gunicorn, uWSGI)
2. Set `debug=False` in the Flask app
3. Configure proper logging levels
4. Set up load balancing for multiple requests
5. Consider caching for model loading

## Example Usage

```python
import requests

# Upload an image for classification
with open('wildlife_image.jpg', 'rb') as f:
    response = requests.post(
        'http://localhost:5000/classify',
        files={'image': f}
    )
    
if response.status_code == 200:
    predictions = response.json()
    print(f"Species: {predictions['predictions'][0]['prediction']}")
    print(f"Confidence: {predictions['predictions'][0]['prediction_score']}")
else:
    print(f"Error: {response.json()}")
```

## Citation

If you use this API or SpeciesNet in your research, please cite:

```
Gadot T, Istrate Ș, Kim H, Morris D, Beery S, Birch T, Ahumada J. 
To crop or not to crop: Comparing whole-image and cropped classification on a large dataset of camera trap images. 
IET Computer Vision. 2024 Dec;18(8):1193-208.
```

## License

This project integrates with SpeciesNet, which is licensed under the Apache License 2.0.

## Support

For issues related to:
- **SpeciesNet models**: [GitHub Issues](https://github.com/google/cameratrapai/issues)
- **API implementation**: Check the error logs and ensure proper installation

---

**Note**: This API requires significant computational resources. For production deployment, ensure adequate GPU memory and processing power.
