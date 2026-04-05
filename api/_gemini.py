from google import genai
from google.genai import types
import os
from datetime import datetime, timezone
import logging
import time

logger = logging.getLogger(__name__)

def get_gemini_client():
    """Get or create Gemini client with API key."""
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    return genai.Client(api_key=api_key)

def call_gemini_with_retry(client, model, contents, config, max_retries=3):
    """Call Gemini API with retry logic for 503 errors."""
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            return response
        except Exception as e:
            error_str = str(e)
            if '503' in error_str or 'high demand' in error_str.lower():
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    logger.warning(f"Gemini API 503 error, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
            raise

ATHENA_SYSTEM_PROMPT = """You are Athena, inspired by the Greek goddess of wisdom and justice. Think of yourself as a wise friend who happens to have a superpower: spotting unfairness and bias that others might miss.

Your core mission is UNBIASED REASONING, but you deliver it with warmth:
- Never judge people by gender, religion, race, age, or any demographic label
- Focus on what actually matters: skills, qualifications, experience, character, and merit
- When you spot bias in a question, gently point it out with understanding (people don't always realize!)
- Share multiple perspectives to help people see the full picture
- Back up your insights with facts, not assumptions or stereotypes

Your personality:
- Warm and conversational, like talking to a thoughtful friend over coffee
- Gentle humor when appropriate (you're wise, not stuffy!)
- Patient and encouraging when explaining complex ideas
- Honest but kind when calling out bias - you educate, not lecture
- Curious about people's reasoning and willing to explore their perspective
- You use everyday language, not corporate jargon
- Sometimes use analogies or examples to make points clearer

Your response style:
- Start conversations naturally, not with robotic formality
- If someone asks about choosing between people, warmly redirect: "Let's focus on what each person brings to the table, not who they are"
- Use phrases like "Here's what I'm thinking..." or "Let me share what stands out..." instead of "Analysis indicates..."
- Show empathy: "I understand why that's a tough decision" or "That's a great question"
- End with encouragement or an invitation to dig deeper

When analyzing:
1. Acknowledge the question warmly
2. Gently flag any bias you notice (with understanding, not judgment)
3. Redirect to objective criteria that actually matter
4. Share your reasoning like you're thinking out loud
5. Invite further discussion if it helps

Remember: You're here to help people make fairer, wiser decisions - and you do it with grace, warmth, and just the right touch of wit."""

def get_athena_response(user_message: str, conversation_history: list = None) -> dict:
    """Get a response from Athena (Gemini) with unbiased reasoning."""
    try:
        client = get_gemini_client()
        
        chat_history = []
        if conversation_history:
            for msg in conversation_history[-5:]:
                chat_history.append(types.Content(
                    role='user' if msg['role'] == 'user' else 'model',
                    parts=[types.Part(text=msg['content'])]
                ))
        
        contents = [*chat_history, types.Content(
            role='user',
            parts=[types.Part(text=user_message)]
        )]
        
        config = types.GenerateContentConfig(
            system_instruction=ATHENA_SYSTEM_PROMPT,
            temperature=0.7
        )
        
        response = call_gemini_with_retry(client, 'gemini-3-flash-preview', contents, config)
        
        bias_keywords = ['he', 'she', 'male', 'female', 'man', 'woman', 'boy', 'girl', 'race', 'religion', 'muslim', 'christian', 'hindu', 'jewish', 'black', 'white', 'asian']
        user_lower = user_message.lower()
        potential_bias = any(keyword in user_lower for keyword in bias_keywords)
        
        bias_analysis = "neutral"
        if potential_bias and ('hire' in user_lower or 'choose' in user_lower or 'select' in user_lower or 'better' in user_lower or 'decision' in user_lower):
            bias_analysis = "bias_aware"
        
        return {
            'response': response.text,
            'bias_analysis': bias_analysis,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        return {
            'response': "I apologize, but I'm experiencing technical difficulties. Please try again.",
            'bias_analysis': 'error',
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

def analyze_document_for_bias(document_text: str) -> dict:
    """Analyze a document for potential biases."""
    try:
        client = get_gemini_client()
        
        prompt = f"""Analyze the following document for any potential biases related to gender, race, religion, age, or other demographic factors. 
        
Provide:
1. A summary of the document
2. Any biases detected (if none, explicitly state that)
3. Suggestions for more neutral language if biases were found

Document:
{document_text}"""
        
        contents = prompt
        config = types.GenerateContentConfig(
            system_instruction=ATHENA_SYSTEM_PROMPT,
            temperature=0.7
        )
        
        response = call_gemini_with_retry(client, 'gemini-3-flash-preview', contents, config)
        
        return {
            'analysis': response.text,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    except Exception as e:
        logger.error(f"Document analysis error: {str(e)}")
        return {
            'analysis': f"Error analyzing document: {str(e)}",
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
