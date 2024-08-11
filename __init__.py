import awsgi
from flask import Flask, request, jsonify
import boto3
import json
import os
from dotenv import load_dotenv
from flask_cors import CORS
import logging

app = Flask(__name__)  # Creating an instance of the Flask class

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize the S3 client using environment variables
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
    region_name=os.getenv('REGION_NAME'),
)

# Enable CORS for the Flask app
CORS(app, resources={r"/*": {"origins": ["http://localhost:3000", "https://main.d3ggcc26a7d3ei.amplifyapp.com"]}})

@app.route('/')  # Decorator defines the home route
def home():
    return "Hello World"

@app.route('/allStudent', methods=['GET'])
def get_users():
    # S3 bucket details
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    file_key = os.getenv('AWS_FILE_KEY') # The key of the file you want to fetch

    try:
        # Fetch the file from S3
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        s3_data = s3_response['Body'].read().decode('utf-8')
        user_data = json.loads(s3_data)
        logging.info('Fetched data from S3: %s', user_data)
    except Exception as e:
        logging.error('Error fetching data from S3: %s', str(e))
        return jsonify({'error': str(e)}), 500
    
    return jsonify(user_data), 200

@app.route('/student/<studentid>', methods=['GET'])
def get_student(studentid):
    bucket_name = os.getenv('AWS_BUCKET_NAME')
    file_key = os.getenv('AWS_FILE_KEY')   # The key of the file you want to fetch

    try:
        # Fetch the file from S3
        s3_response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
        s3_data = s3_response['Body'].read().decode('utf-8')
        data = json.loads(s3_data)
        students=data['students']
        # Find the student with the specified ID
        student = next((stu for stu in students if stu.get('id') == studentid), None)
        
        if student:
            logging.info('Found student with ID %s: %s', studentid, student)
            return jsonify(student), 200
        else:
            logging.warning('Student with ID %s not found', studentid)
            return jsonify({'error': 'Student not found'}), 404

    except Exception as e:
        logging.error('Error fetching data from S3 or finding student: %s', str(e))
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)  # Running the app in debug mode

