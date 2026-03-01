# 🛡️ GuardianAI: Distributed Narrative Moderation System

**GuardianAI** is a multi-stage, high-throughput moderation pipeline. It is specifically designed to solve the **"Truthful Deception"** challenge: detecting content that is factually accurate but contextually malicious.

##  The Vision
Most moderation systems rely on simple keyword matching or sentiment analysis, which are easily bypassed by sophisticated actors. GuardianAI uses a **Tiered Sieve Architecture** to balance extreme speed (latency) with deep cognitive reasoning (accuracy).

---

##  System Architecture



Our system is decoupled into three specialized stages:

1.  **Stage 1: Ingestion & Reputation (Java Spring Boot)**
    * **Goal:** Rapid filtering of known threats.
    * **Action:** Performs IP reputation checks and "Hard-Refusal" string matching.
    * **Latency:** < 5ms.

2.  **Stage 2: Semantic Heuristics (Python + fastText)**
    * **Goal:** Cost-efficient noise reduction.
    * **Action:** Runs on CPU to clear 90% of neutral/safe content and identify language (English/Urdu/Roman Urdu).
    * **Latency:** < 50ms.

3.  **Stage 3: Narrative Reasoning (Python + Llama 3.2 + GPU)**
    * **Goal:** Solve "Truthful Deception."
    * **Action:** A local LLM performs a **Fallacy Audit** to detect malicious framing, cherry-picking, and misinformation.
    * **Latency:** 1–3s (Asynchronous).

---

##  Strategic Trade-offs

| Constraint | Strategy | Reason |
| :--- | :--- | :--- |
| **Budget** | **Local Edge Computing** | Running Llama 3.2 locally on an RTX 4060 avoids thousands of dollars in monthly OpenAI/Cloud API fees. |
| **Latency** | **Asynchronous Queuing** | We use **Redis** to ensure the user gets an instant response, while the "Deep Reasoning" happens in the background. |
| **Adaptability** | **Reasoning Prompts** | Instead of static rules, we use LLM-based intent detection, making the system resilient to "adversarial drift." |

---

##  Tech Stack
- **Backend:** Java 17, Spring Boot, PostgreSQL
- **Messaging:** Redis (Distributed Queues)
- **AI/ML:** Llama 3.2 (Ollama), fastText
- **Hardware:** NVIDIA RTX 4060 (8GB VRAM)
- **Monitoring:** Streamlit Live Dashboard

---

##  Failure Mode Declaration
We believe in **Intellectual Honesty**. Our system is robust but has defined boundaries:
1.  **Sarcasm & Irony:** Complex humor may trigger false positives. 
    * *Containment:* Reasoning logs are stored for human appeal.
2.  **Hyper-Local Slang:** Rapidly evolving Urdu "dog whistles" might bypass Stage 2. 
    * *Containment:* Low-confidence scores trigger human-in-the-loop review.
3.  **Multimedia Masking:** Currently text-only. 
    * *Containment:* Metadata flagging for posts with high engagement but low text.

---

##  Setup & Installation
1.  **Database:** `docker-compose up -d` (Postgres & Redis).
2.  **Gateway:** Navigate to `/api-gateway` and run `./mvnw spring-boot:run`.
3.  **CPU Worker:** Navigate to `/stage2-classifier` and run `python worker.py`.
4.  **GPU Worker:** Navigate to `/stage3-deeplearning` and run `python gpu_worker.py`.
5.  **Dashboard:** Run `streamlit run dashboard.py`.

---

**Developed by Ibrahim Asad** 
