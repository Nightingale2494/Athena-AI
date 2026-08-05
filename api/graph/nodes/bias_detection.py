import json
from langchain_google_genai import ChatGoogleGenerativeAI
from api.graph.state import AthenaState
from api.graph.prompts import BIAS_DETECTION_SYSTEM_PROMPT

def detect_bias_node(state: AthenaState) -> dict:
    """Analyze the user message for potential bias."""
    messages = state.get("messages", [])
    if not messages:
        return {"bias_analysis": "neutral"}
    
    last_message = messages[-1].content
    user_lower = last_message.lower()
    
    # 1. Run rapid heuristic keyword check
    bias_keywords = [
        'he', 'she', 'male', 'female', 'man', 'woman', 'boy', 'girl', 
        'race', 'religion', 'muslim', 'christian', 'hindu', 'jewish', 
        'black', 'white', 'asian', 'disabled', 'age', 'elderly'
    ]
    potential_bias = any(keyword in user_lower for keyword in bias_keywords)
    
    if potential_bias and any(action in user_lower for action in ['hire', 'choose', 'select', 'better', 'decision', 'eval']):
        return {"bias_analysis": "bias_aware"}
        
    # 2. Hybrid verification: Run LLM-based bias detection for subtle biases
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0)
        # Call model with structured prompts
        system_instruction = BIAS_DETECTION_SYSTEM_PROMPT
        
        response = llm.invoke([
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": f"Analyze query: {last_message}"}
        ])
        
        # Parse JSON output from model
        content = response.content.strip()
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()
            
        result = json.loads(content)
        bias_analysis = result.get("bias_analysis", "neutral")
        return {"bias_analysis": bias_analysis}
    except Exception as e:
        # Fallback to heuristic result or neutral on failure
        return {"bias_analysis": "bias_aware" if potential_bias else "neutral"}
