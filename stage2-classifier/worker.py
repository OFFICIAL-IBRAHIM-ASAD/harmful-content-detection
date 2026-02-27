import redis
import json
import fasttext

# 1. Load the pre-trained Language Identification model
# This model expects the 'lid.176.ftz' file to be in the same folder
try:
    model = fasttext.load_model("lid.176.ftz")
    print("🧠 Stage 2: fastText Model Loaded Successfully.")
except Exception as e:
    print(f"❌ ERROR: Could not load model. Ensure 'lid.176.ftz' is in this folder. {e}")
    exit(1)

# 2. Connect to the local Redis instance
# decode_responses=True ensures we get strings back from Redis instead of bytes
r = redis.Redis(host='localhost', port=6379, decode_responses=True)

print("🎧 Stage 2 Python Worker listening to 'stage2-fasttext-queue'...")

while True:
    # blpop (blocking pop) waits until a message is available in the queue
    result = r.blpop('stage2-fasttext-queue')
    
    if result:
        queue_name, message = result
        content = json.loads(message)
        text = content.get('contentText', '')
        
        # 3. Perform Language Classification
        # predict() returns the label and the confidence score
        predictions = model.predict(text, k=1)
        
        # Format the label (removes the '__label__' prefix)
        label = predictions[0][0].replace("__label__", "")
        confidence = predictions[1][0]

        print(f"\n📥 Analysis for ID {content.get('id')}:")
        print(f"Text: '{text}'")
        print(f"Detected Language: {label} (Confidence: {confidence:.2f})")
        
        # 4. Routing Logic: Escalation vs. Verification
        if label not in ['en', 'ur']:
            print("⚠️ ALERT: Non-target language or suspicious text detected. Escalating to Stage 3...")
            
            # Pushes the JSON data into the queue that the RTX 4060 is listening to
            r.rpush('stage3-gpu-queue', json.dumps(content)) 
            print(f"🚀 Handover Complete: Task moved to GPU (stage3-gpu-queue)")
        else:
            print("✅ Language verified (English/Urdu). Sending to Stage 3 for Sentiment check anyway...")
            # For your project, you likely want ALL valid text checked by the GPU for harmful sentiment
            r.rpush('stage3-gpu-queue', json.dumps(content))

        print("-" * 40)
