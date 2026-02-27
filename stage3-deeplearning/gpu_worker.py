import torch
import redis
import json
import psycopg2 
from transformers import pipeline

# 1. Initialize GPU
device = 0 if torch.cuda.is_available() else -1
print(f"🚀 Device: {'GPU (RTX 4060)' if device == 0 else 'CPU'}")

# 2. Load Deep Learning Model (It will use the one already downloaded)
classifier = pipeline("sentiment-analysis", model="cardiffnlp/twitter-roberta-base-sentiment", device=device)

# 3. Connections
r = redis.Redis(host='localhost', port=6379, decode_responses=True)
# We use '127.0.0.1' to ensure it connects properly from WSL to Docker
db_conn = psycopg2.connect(
    dbname="moderation_db", 
    user="admin", 
    password="password123", 
    host="127.0.0.1", 
    port="5432"
)
cursor = db_conn.cursor()

print("🔥 Stage 3: GPU Worker Live & Database Connected!")

while True:
    result = r.blpop('stage3-gpu-queue')
    if result:
        message = json.loads(result[1])
        item_id = message['id']
        text = message['contentText']
        
        # Inference
        prediction = classifier(text)[0]
        
        # LABEL_0 is Negative for this model
        final_status = "REJECTED" if prediction['label'] == 'LABEL_0' else "APPROVED"
        
        print(f"\n🔬 ID {item_id} | Sentiment: {prediction['label']} | Action: {final_status}")

        # 4. CRITICAL: Update the Postgres Database
        cursor.execute("UPDATE content_items SET status = %s WHERE id = %s", (final_status, item_id))
        db_conn.commit()
        
        print(f"✅ DB UPDATED: ID {item_id} is now {final_status}")
        print("-" * 40)
