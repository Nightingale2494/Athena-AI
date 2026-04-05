from http.server import BaseHTTPRequestHandler
import json
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from _firebase import db
from _auth import verify_token

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()
        return
    
    def do_GET(self):
        try:
            # Verify authentication
            authorization = self.headers.get('Authorization')
            user = verify_token(authorization)
            user_id = user['uid']
            
            # Query documents
            docs_ref = db.collection('document_analyses').where('user_id', '==', user_id).limit(20).stream()
            
            result = []
            for doc in docs_ref:
                doc_data = doc.to_dict()
                result.append({
                    'id': doc.id,
                    'filename': doc_data.get('filename', ''),
                    'analysis': doc_data.get('analysis', ''),
                    'created_at': doc_data.get('created_at', '')
                })
            
            # Sort by created_at
            result.sort(key=lambda x: x['created_at'], reverse=True)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
