#!/usr/bin/env python3
"""
Flask API for Image Classification using SpeciesNet

This is a backend-only Flask application that provides a REST API for image classification.
It receives images via multipart/form-data, processes them using SpeciesNet, and returns
clean, structured JSON predictions optimized for Spring Boot integration.

SpeciesNet is an ensemble of AI models for classifying wildlife in camera trap images,
developed by Google. It combines object detection (MegaDetector) and species classification
to identify animals in images.

API Endpoints:
- POST /classify: Upload an image for classification (returns clean format)
- POST /classify/raw: Upload an image for classification (returns raw SpeciesNet output)
- GET /health: Health check endpoint

Usage Example:
curl -X POST -F "image=@your_image.jpg" http://localhost:5000/classify

Author: Generated for SIH25 project
"""

import os
import sys
import subprocess
import json
import logging
import tempfile
import uuid
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'api_uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit

# Create uploads directory
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logging.info(f"Created uploads directory: {UPLOAD_FOLDER}")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def get_cameratrapai_path():
    """Find the cameratrapai directory relative to this script."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    cameratrapai_path = os.path.join(app_dir, 'cameratrapai')
    
    if os.path.exists(cameratrapai_path):
        return cameratrapai_path
    
    raise FileNotFoundError(
        f"cameratrapai directory not found at: {cameratrapai_path}\n"
        f"Please ensure cameratrapai directory exists in the same folder as app.py"
    )

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_speciesnet_output(raw_predictions):
    """
    Convert raw SpeciesNet output to clean, structured format for Spring Boot.
    
    Args:
        raw_predictions: Raw JSON output from SpeciesNet
        
    Returns:
        Clean, structured prediction data
    """
    try:
        # Handle case where no predictions
        if not raw_predictions.get('predictions') or len(raw_predictions['predictions']) == 0:
            return {
                "biologicalClass": None,
                "order": None,
                "family": None,
                "genus": None,
                "species": None,
                "commonName": None,
                "score": 0.0,
                "bboxX": None,
                "bboxY": None,
                "bboxWidth": None,
                "bboxHeight": None
            }

        prediction_data = raw_predictions['predictions'][0]
        
        # Check if any animals were detected
        detections = prediction_data.get('detections', [])
        
        # Filter for animal detections (category "1" = animal)
        animal_detections = [d for d in detections if d.get('category') == '1']
        
        if not animal_detections:
            return {
                "biologicalClass": None,
                "order": None,
                "family": None,
                "genus": None,
                "species": None,
                "commonName": None,
                "score": 0.0,
                "bboxX": None,
                "bboxY": None,
                "bboxWidth": None,
                "bboxHeight": None
            }
        
        # Get top prediction and detection
        top_prediction = prediction_data.get('prediction', '')
        prediction_score = prediction_data.get('prediction_score', 0.0)
        top_detection = max(animal_detections, key=lambda x: x.get('conf', 0))
        
        # Parse taxonomic information from prediction string
        # Format: "uuid;class;order;family;genus;species;common_name"
        taxonomy_parts = top_prediction.split(';')
        
        biological_class = taxonomy_parts[1] if len(taxonomy_parts) > 1 else None
        order = taxonomy_parts[2] if len(taxonomy_parts) > 2 else None
        family = taxonomy_parts[3] if len(taxonomy_parts) > 3 else None
        genus = taxonomy_parts[4] if len(taxonomy_parts) > 4 else None
        species = taxonomy_parts[5] if len(taxonomy_parts) > 5 else None
        common_name = taxonomy_parts[6] if len(taxonomy_parts) > 6 else None
        
        # Extract bounding box
        bbox = top_detection.get('bbox', [0, 0, 0, 0])
        bbox_x = bbox[0] if len(bbox) > 0 else 0
        bbox_y = bbox[1] if len(bbox) > 1 else 0
        bbox_w = bbox[2] if len(bbox) > 2 else 0
        bbox_h = bbox[3] if len(bbox) > 3 else 0
        
        # Build clean response
        response = {
            "biologicalClass": biological_class if biological_class else None,
            "order": order if order else None,
            "family": family if family else None,
            "genus": genus if genus else None,
            "species": species if species else None,
            "commonName": common_name if common_name else None,
            "score": prediction_score,
            "bboxX": bbox_x,
            "bboxY": bbox_y,
            "bboxWidth": bbox_w,
            "bboxHeight": bbox_h
        }
        
        return response
        
    except Exception as e:
        logging.error(f"Error processing SpeciesNet output: {e}")
        return {
            "biologicalClass": None,
            "order": None,
            "family": None,
            "genus": None,
            "species": None,
            "commonName": None,
            "score": 0.0,
            "bboxX": None,
            "bboxY": None,
            "bboxWidth": None,
            "bboxHeight": None
        }

def run_speciesnet_classification(image_path):
    """
    Run SpeciesNet classification on an image.
    
    Args:
        image_path: Path to the image file
        
    Returns:
        Raw SpeciesNet predictions as JSON
    """
    # Create temporary output file
    temp_output_path = os.path.join(tempfile.gettempdir(), f'speciesnet_output_{uuid.uuid4().hex}.json')
    
    try:
        # Get cameratrapai directory
        cameratrapai_dir = get_cameratrapai_path()
        
        # Prepare command for SpeciesNet inference
        absolute_image_path = os.path.abspath(image_path)
        cmd = [
            sys.executable, '-m', 'speciesnet.scripts.run_model',  # Use current Python interpreter
            '--filepaths', absolute_image_path,
            '--predictions_json', temp_output_path,
            '--noprogress_bars',
            '--bypass_prompts'
        ]
        
        logging.info(f"Executing SpeciesNet command: {' '.join(cmd)}")
        logging.info(f"Working directory: {cameratrapai_dir}")
        
        # Execute the SpeciesNet model
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=True,
            cwd=cameratrapai_dir
        )
        
        # Read the predictions from the output file
        with open(temp_output_path, 'r') as f:
            predictions = json.load(f)
            
        return predictions
        
    finally:
        # Clean up temporary output file
        if os.path.exists(temp_output_path):
            try:
                os.remove(temp_output_path)
                logging.info(f"Cleaned up temporary output file: {temp_output_path}")
            except OSError as e:
                logging.error(f"Failed to delete temporary output file {temp_output_path}: {e}")

@app.route('/classify', methods=['POST'])
def classify_image():
    """
    Classify an uploaded image using SpeciesNet.
    Returns clean, structured format optimized for Spring Boot integration.
    
    Expects:
        - multipart/form-data with an 'image' file field
        
    Returns:
        - Clean JSON response with taxonomic classification and bounding box
        - Error responses for various failure conditions
    """
    temp_file_path = None
    
    try:
        # Validate request has file part
        if 'image' not in request.files:
            return jsonify({
                'error': 'No image field in request',
                'message': 'Request must contain a file field named "image"'
            }), 400
        
        file = request.files['image']
        
        # Validate file was selected
        if file.filename == '':
            return jsonify({
                'error': 'No file selected',
                'message': 'Please select a file to upload'
            }), 400
        
        # Validate file type
        if not allowed_file(file.filename):
            return jsonify({
                'error': 'Invalid file type',
                'message': f'Allowed file types: {", ".join(ALLOWED_EXTENSIONS)}',
                'filename': file.filename
            }), 400
        
        # Secure filename and save temporarily
        filename = secure_filename(file.filename)
        temp_file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_file_path)
        
        logging.info(f"Saved uploaded file: {temp_file_path}")
        
        # Run SpeciesNet classification
        raw_predictions = run_speciesnet_classification(temp_file_path)
        
        # Process into clean format
        clean_response = process_speciesnet_output(raw_predictions)
        
        logging.info(f"Successfully processed classification for {filename}")
        return jsonify(clean_response)
            
    except FileNotFoundError as e:
        logging.error(f"SpeciesNet installation not found: {e}")
        return jsonify({
            'error': 'SpeciesNet not found',
            'message': 'The SpeciesNet installation directory could not be located',
            'details': str(e)
        }), 500
            
    except subprocess.CalledProcessError as e:
        logging.error(f"SpeciesNet script failed with return code {e.returncode}")
        logging.error(f"stderr: {e.stderr}")
        return jsonify({
            'error': 'Model execution failed',
            'message': 'The SpeciesNet model script encountered an error',
            'return_code': e.returncode,
            'stderr': e.stderr
        }), 500
        
    except Exception as e:
        logging.exception(f"Unexpected error during image classification: {e}")
        return jsonify({
            'error': 'Internal server error',
            'message': 'An unexpected error occurred during processing',
            'details': str(e)
        }), 500
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logging.info(f"Cleaned up temporary file: {temp_file_path}")
            except OSError as e:
                logging.error(f"Failed to delete temporary file {temp_file_path}: {e}")

@app.route('/classify/raw', methods=['POST'])
def classify_image_raw():
    """
    Classify an uploaded image using SpeciesNet.
    Returns raw SpeciesNet output for debugging and advanced use cases.
    
    Expects:
        - multipart/form-data with an 'image' file field
        
    Returns:
        - Raw JSON response from SpeciesNet
    """
    temp_file_path = None
    
    try:
        # Same validation as main classify endpoint
        if 'image' not in request.files:
            return jsonify({'error': 'No image field in request'}), 400
        
        file = request.files['image']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        temp_file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(temp_file_path)
        
        # Run SpeciesNet classification
        raw_predictions = run_speciesnet_classification(temp_file_path)
        
        return jsonify(raw_predictions)
        
    except Exception as e:
        logging.exception(f"Error in raw classification: {e}")
        return jsonify({'error': str(e)}), 500
        
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except OSError:
                pass

# ... keep all your existing route handlers (api_info, health_check, error handlers) ...

@app.route('/', methods=['GET'])
def api_info():
    """Provide API information and usage instructions."""
    return jsonify({
        'name': 'SpeciesNet Image Classification API',
        'version': '2.0.0',
        'description': 'Backend API for classifying wildlife in camera trap images using SpeciesNet',
        'endpoints': {
            'POST /classify': {
                'description': 'Upload an image for species classification (clean format)',
                'parameters': {'image': 'File upload field (multipart/form-data)'},
                'response_format': {
                    'biologicalClass': 'string',
                    'order': 'string',
                    'family': 'string', 
                    'genus': 'string',
                    'species': 'string',
                    'commonName': 'string',
                    'score': 'float (0-1)',
                    'bboxX': 'float (normalized 0-1)',
                    'bboxY': 'float (normalized 0-1)',
                    'bboxWidth': 'float (normalized 0-1)',
                    'bboxHeight': 'float (normalized 0-1)'
                },
                'example': 'curl -X POST -F "image=@your_image.jpg" http://localhost:5000/classify'
            },
            'POST /classify/raw': {
                'description': 'Upload an image for species classification (raw SpeciesNet format)',
                'parameters': {'image': 'File upload field (multipart/form-data)'},
                'example': 'curl -X POST -F "image=@your_image.jpg" http://localhost:5000/classify/raw'
            },
            'GET /health': {
                'description': 'Health check endpoint',
                'example': 'curl -X GET http://localhost:5000/health'
            }
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'service': 'SpeciesNet Image Classification API',
        'upload_folder': UPLOAD_FOLDER,
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large errors."""
    return jsonify({
        'error': 'File too large',
        'message': 'The uploaded file exceeds the maximum allowed size (100MB)'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/classify (POST)', '/classify/raw (POST)', '/health (GET)']
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors."""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'This endpoint does not support the requested HTTP method'
    }), 405

if __name__ == '__main__':
    logging.info("Starting SpeciesNet Image Classification API v2.0")
    logging.info(f"Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    logging.info(f"Allowed file extensions: {ALLOWED_EXTENSIONS}")
    
    app.run(
        host='0.0.0.0',
        debug=True,
        port=5000
    )