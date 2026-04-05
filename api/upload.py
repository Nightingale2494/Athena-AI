from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime, timezone
import sys
import os
import cgi
import io

sys.path.insert(0, os.path.dirname(__file__))

from _firebase import db
from _auth import verify_token
from _gemini import analyze_document_for_bias

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return
    
    def do_POST(self):
        try:
            # Verify authentication
            authorization = self.headers.get('Authorization')
            user = verify_token(authorization)
            user_id = user['uid']
            
            # Parse multipart form data
            content_type = self.headers.get('Content-Type')
            if not content_type or 'multipart/form-data' not in content_type:
                raise Exception("Content-Type must be multipart/form-data")
            
            # Read file content
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                }
            )
            
            if 'file' not in form:
                raise Exception("No file uploaded")
            
            file_item = form['file']
            filename = file_item.filename
            
            if not filename.endswith('.txt'):
                raise Exception("Only .txt files supported")
            
            # Read file content
            file_content = file_item.file.read()
            try:
                text_content = file_content.decode('utf-8')
            except:
                text_content = file_content.decode('latin-1')
            
            # Analyze document
            analysis_result = analyze_document_for_bias(text_content)
            
            # Save to Firestore
            doc_id = str(uuid.uuid4())
            db.collection('document_analyses').document(doc_id).set({
                'user_id': user_id,
                'filename': filename,
                'analysis': analysis_result['analysis'],
                'created_at': datetime.now(timezone.utc).isoformat()
            })
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'id': doc_id,
                'filename': filename,
                'analysis': analysis_result['analysis'],
                'timestamp': analysis_result['timestamp']
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
