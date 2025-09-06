#!/usr/bin/env python3
"""
Flask API for Image Classification using SpeciesNet

This is a backend-only Flask application that provides a REST API for image classification.
It receives images via multipart/form-data, processes them using SpeciesNet, and returns
the raw JSON predictions from the model.

SpeciesNet is an ensemble of AI models for classifying wildlife in camera trap images,
developed by Google. It combines object detection (MegaDetector) and species classification
to identify animals in images.

API Endpoints:
- POST /classify: Upload an image for classification
- GET /health: Health check endpoint

Usage Example:
curl -X POST -F "image=@your_image.jpg" http://localhost:5000/classify

Author: Generated for SIH25 project
"""

import os
import subprocess
import json
import logging
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Initialize Flask app
app = Flask(__name__)

# Create uploads directory
UPLOAD_FOLDER = 'api_uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    logging.info(f"Created uploads directory: {UPLOAD_FOLDER}")

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/classify', methods=['POST'])
def classify_image():
    """
    Classify an uploaded image using SpeciesNet.
    
    Expects:
        - multipart/form-data with an 'image' file field
        
    Returns:
        - JSON response with SpeciesNet predictions
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
        
        # Create a temporary output file for predictions
        import tempfile
        import uuid
        import uuid
        temp_output_path = os.path.join(tempfile.gettempdir(), f'speciesnet_output_{uuid.uuid4().hex}.json')
        
        try:
            # Prepare command for SpeciesNet inference
            # Use absolute paths to avoid working directory issues
            absolute_image_path = os.path.abspath(temp_file_path)
            cmd = [
                'python', '-m', 'speciesnet.scripts.run_model',
                '--filepaths', absolute_image_path,
                '--predictions_json', temp_output_path,
                '--noprogress_bars',  # Disable progress bars for cleaner output
                '--bypass_prompts'    # Bypass any interactive prompts
            ]
            
            logging.info(f"Executing SpeciesNet command: {' '.join(cmd)}")
            
            # Execute the SpeciesNet model
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True,
                cwd='/home/arnav/SIH25/cameratrapai'  # Set working directory to cameratrapai
            )
            
            # Read the predictions from the output file
            with open(temp_output_path, 'r') as f:
                predictions = json.load(f)
                
        finally:
            # Clean up temporary output file
            if os.path.exists(temp_output_path):
                try:
                    os.remove(temp_output_path)
                    logging.info(f"Cleaned up temporary output file: {temp_output_path}")
                except OSError as e:
                    logging.error(f"Failed to delete temporary output file {temp_output_path}: {e}")
        
        # Parse the JSON output from SpeciesNet
        try:
            logging.info(f"Successfully parsed SpeciesNet output for {filename}")
            return jsonify(predictions)
            
        except json.JSONDecodeError as e:
            logging.error(f"Failed to parse SpeciesNet output as JSON: {e}")
            logging.error(f"Raw stdout: {result.stdout}")
            return jsonify({
                'error': 'Invalid JSON output from model',
                'message': 'The model script did not return valid JSON',
                'details': str(e),
                'raw_output': result.stdout[:1000]  # First 1000 chars for debugging
            }), 500
            
    except subprocess.CalledProcessError as e:
        logging.error(f"SpeciesNet script failed with return code {e.returncode}")
        logging.error(f"stderr: {e.stderr}")
        return jsonify({
            'error': 'Model execution failed',
            'message': 'The SpeciesNet model script encountered an error',
            'return_code': e.returncode,
            'stderr': e.stderr,
            'command': ' '.join(e.cmd) if e.cmd else 'Unknown command'
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

@app.route('/', methods=['GET'])
def api_info():
    """Provide API information and usage instructions."""
    return jsonify({
        'name': 'SpeciesNet Image Classification API',
        'version': '1.0.0',
        'description': 'Backend API for classifying wildlife in camera trap images using SpeciesNet',
        'endpoints': {
            'POST /classify': {
                'description': 'Upload an image for species classification',
                'parameters': {
                    'image': 'File upload field (multipart/form-data)'
                },
                'supported_formats': list(ALLOWED_EXTENSIONS),
                'example': 'curl -X POST -F "image=@your_image.jpg" http://localhost:5000/classify'
            },
            'GET /health': {
                'description': 'Health check endpoint',
                'example': 'curl -X GET http://localhost:5000/health'
            },
            'GET /': {
                'description': 'API information and usage instructions'
            }
        },
        'about_speciesnet': {
            'description': 'SpeciesNet is an ensemble of AI models for wildlife classification',
            'developer': 'Google Camera Traps AI team',
            'models': ['MegaDetector (object detection)', 'SpeciesNet Classifier (species identification)'],
            'capabilities': ['Animal detection', 'Species identification', 'Blank image detection', 'Human/vehicle detection']
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
        'message': 'The uploaded file exceeds the maximum allowed size'
    }), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'available_endpoints': ['/classify (POST)', '/health (GET)']
    }), 404

@app.errorhandler(405)
def method_not_allowed(error):
    """Handle method not allowed errors."""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'This endpoint does not support the requested HTTP method'
    }), 405

if __name__ == '__main__':
    logging.info("Starting SpeciesNet Image Classification API")
    logging.info(f"Upload folder: {os.path.abspath(UPLOAD_FOLDER)}")
    logging.info(f"Allowed file extensions: {ALLOWED_EXTENSIONS}")
    
    app.run(
        host='0.0.0.0',
        debug=True,
        port=5000
    )
