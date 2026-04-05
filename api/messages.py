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
            
            # Get conversation_id from path
            path_parts = self.path.split('/')
            if len(path_parts) < 4:
                raise Exception("Invalid path")
            
            conversation_id = path_parts[3]  # /api/messages?id=xxx or /api/conversations/{id}/messages
            
            # Verify user owns this conversation
            conversation_ref = db.collection('conversations').document(conversation_id)
            conversation_doc = conversation_ref.get()
            
            if not conversation_doc.exists:
                raise Exception("Conversation not found")
            
            conversation_data = conversation_doc.to_dict()
            if conversation_data.get('user_id') != user_id:
                raise Exception("Access denied")
            
            # Get messages
            messages_ref = conversation_ref.collection('messages').order_by('timestamp')
            messages = messages_ref.stream()
            
            result = []
            for msg in messages:
                msg_data = msg.to_dict()
                result.append({
                    'id': msg.id,
                    'role': msg_data.get('role', 'user'),
                    'content': msg_data.get('content', ''),
                    'bias_analysis': msg_data.get('bias_analysis'),
                    'timestamp': msg_data.get('timestamp', '')
                })
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            self.wfile.write(json.dumps(result).encode())
            
        except Exception as e:
            self.send_response(500 if 'Access denied' not in str(e) else 403)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
