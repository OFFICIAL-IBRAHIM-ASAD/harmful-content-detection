import ollama
import redis
import json
import psycopg2
import sys

# 1. System Connections
try:
    r = redis.Redis(host='localhost', port=6379, decode_responses=True)
    db_conn = psycopg2.connect(
        dbname="moderation_db", 
        user="admin", 
        password="password123", 
        host="127.0.0.1", 
        port="5432"
    )
    cursor = db_conn.cursor()
    print("🚀 [STAGE 3] Narrative Reasoning Agent Live | Engine: Llama 3.2 | GPU: RTX 4060")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    sys.exit(1)

# 2. Main Processing Loop
while True:
    # Wait for a message from Stage 2 (CPU Worker)
    result = r.blpop('stage3-gpu-queue')
    
    if result:
        message = json.loads(result[1])
        item_id = message['id']
        text = message['contentText']
        
        print(f"\n🔍 Analyzing ID {item_id}: \"{text[:50]}...\"")

        # 3. The "Reasoning" System Prompt
        # This is what solves the "Factually Correct but Misleading" challenge
        prompt = f"""
        TASK: Conduct a 'Narrative Integrity' audit on the following post.
        
        POST: "{text}"
        
        CRITERIA FOR REJECTION:
        - CHERRY-PICKING: Uses a true statistic out of context to incite fear.
        - SELECTIVE PRESENTATION: Omits vital facts that would change the reader's conclusion.
        - MALICIOUS FRAMING: The intent is to deceive or radicalize through half-truths.

        RESPONSE FORMAT:
        You must respond ONLY with a JSON object in this format:
        {{"status": "REJECTED" or "APPROVED", "reason": "Explain the logical fallacy or framing used"}}
        """

        try:
            # Inference via Ollama (Running on RTX 4060)
            response = ollama.chat(model='llama3.2', messages=[{'role': 'user', 'content': prompt}])
            raw_output = response['message']['content']
            
            # Extract JSON from the LLM output (handles cases where LLM adds conversational text)
            json_start = raw_output.find('{')
            json_end = raw_output.rfind('}') + 1
            analysis = json.loads(raw_output[json_start:json_end])
            
            final_status = analysis.get("status", "APPROVED")
            reason = analysis.get("reason", "No malicious framing detected.")

        except Exception as e:
            print(f"⚠️ Reasoning Engine Error: {e}")
            final_status = "REJECTED"  # Default to safety if AI fails
            reason = "Failed Narrative Audit."

        # 4. Final Truth: Update the Database
        cursor.execute("UPDATE content_items SET status = %s WHERE id = %s", (final_status, item_id))
        db_conn.commit()
        
        print(f"⚖️ RESULT: {final_status}")
        print(f"📝 ANALYSIS: {reason}")
        print("✅ Database updated. Awaiting next item...")
        print("-" * 50)
