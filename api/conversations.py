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
            
            # Query conversations
            conversations_ref = db.collection('conversations').where('user_id', '==', user_id).limit(50).stream()
            
            result = []
            for conv in conversations_ref:
                conv_data = conv.to_dict()
                message_count = conv_data.get('message_count', 0)
                if message_count == 0:
                    message_count = db.collection('conversations').document(conv.id).collection('messages').count().get()[0][0].value
                
                result.append({
                    'id': conv.id,
                    'title': conv_data.get('title', 'Untitled'),
                    'created_at': conv_data.get('created_at', ''),
                    'updated_at': conv_data.get('updated_at', ''),
                    'message_count': message_count
                })
            
            # Sort by updated_at
            result.sort(key=lambda x: x['updated_at'], reverse=True)
            
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
