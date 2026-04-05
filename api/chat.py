from http.server import BaseHTTPRequestHandler
import json
import uuid
from datetime import datetime, timezone
from google.cloud import firestore
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from _firebase import db
from _auth import verify_token
from _gemini import get_athena_response

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
            
            # Parse request body
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            message = data.get('message')
            conversation_id = data.get('conversation_id') or str(uuid.uuid4())
            
            # Get conversation history
            conversation_ref = db.collection('conversations').document(conversation_id)
            conversation_doc = conversation_ref.get()
            
            conversation_history = []
            if conversation_doc.exists:
                messages_ref = conversation_ref.collection('messages').select(['role', 'content']).order_by('timestamp').limit(10)
                messages = messages_ref.stream()
                conversation_history = [{
                    'role': msg.to_dict()['role'],
                    'content': msg.to_dict()['content']
                } for msg in messages]
            else:
                # Create new conversation
                conversation_ref.set({
                    'user_id': user_id,
                    'title': message[:50] + '...' if len(message) > 50 else message,
                    'created_at': datetime.now(timezone.utc).isoformat(),
                    'updated_at': datetime.now(timezone.utc).isoformat(),
                    'message_count': 0
                })
            
            # Get Athena's response
            athena_result = get_athena_response(message, conversation_history)
            
            # Save user message
            user_message_id = str(uuid.uuid4())
            conversation_ref.collection('messages').document(user_message_id).set({
                'role': 'user',
                'content': message,
                'timestamp': datetime.now(timezone.utc).isoformat()
            })
            
            # Save Athena's response
            athena_message_id = str(uuid.uuid4())
            conversation_ref.collection('messages').document(athena_message_id).set({
                'role': 'assistant',
                'content': athena_result['response'],
                'bias_analysis': athena_result['bias_analysis'],
                'timestamp': athena_result['timestamp']
            })
            
            # Update conversation
            conversation_ref.update({
                'updated_at': datetime.now(timezone.utc).isoformat(),
                'message_count': firestore.Increment(2)
            })
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'response': athena_result['response'],
                'bias_analysis': athena_result['bias_analysis'],
                'conversation_id': conversation_id,
                'message_id': athena_message_id
            }
            
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            error_response = {'error': str(e)}
            self.wfile.write(json.dumps(error_response).encode())
