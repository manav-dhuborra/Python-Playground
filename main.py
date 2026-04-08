from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from google import genai  

# ==========================================
# 1. SETUP YOUR KEYS & CREDENTIALS
# ==========================================

GEMINI_API_KEY = ""
SUPPORT_EMAIL = "support@hubora.com"       

client = genai.Client(api_key="AIzaSyDFauWJMWQoNABM_b18KemD80M5bEmGKm8")

class UserMessage(BaseModel):
    user_email: str
    question: str

# ==========================================
# 2. THE SIMULATED EMAIL FUNCTION
# ==========================================

def send_email_ticket(user_email: str, question: str):
    """Simulates sending the ticket to support."""
    
    simulated_email = f"""
    =========================================
    NEW SUPPORT TICKET GENERATED 
    =========================================
    TO: {SUPPORT_EMAIL}
    FROM: {user_email}
    SUBJECT: Escalated Support Request
    
    MESSAGE:
    A user requested help that was out of scope for the FAQ bot.
    User Question: "{question}"
    =========================================
    """
    print(simulated_email)

# ==========================================
# 3. FASTAPI APP & TOON KNOWLEDGE BASE
# ==========================================
app = FastAPI(title="Hubora Support")

# THE TOON (Token-Oriented Object Notation) DATASET
# This explicit tokenization makes it extremely easy for the LLM to parse
COMPANY_FAQS_TOON = """
<FAQ_DATASET>
    <ITEM>
        <TKN_INTENT>PASSWORD_RESET</TKN_INTENT>
        <TKN_Q>How to reset password?</TKN_Q>
        <TKN_A>Go to settings and click reset.</TKN_A>
    </ITEM>
    <ITEM>
        <TKN_INTENT>BUSINESS_HOURS</TKN_INTENT>
        <TKN_Q>What are your hours?</TKN_Q>
        <TKN_A>9 AM to 5 PM EST.</TKN_A>
    </ITEM>
</FAQ_DATASET>
"""
@app.get("/")
async def home_page():
    return {"message": "Hubora API running. Knowledge Base loaded via TOON. Visit /docs to test."}

@app.post("/chat")
async def chat_with_bot(message: UserMessage, background_tasks: BackgroundTasks):
    
    # 🧠 PROMPT ENGINEERING: Instructing the AI to read the TOON format
    prompt = f"""
    You are a professional support AI for Hubora.
    You will be provided with a knowledge base formatted in Token-Oriented Object Notation (TOON).
    
    [KNOWLEDGE_BASE_START]
    {COMPANY_FAQS_TOON}
    [KNOWLEDGE_BASE_END]
    
    User Query: "{message.question}"
    
    Instructions:
    1. Scan the <FAQ_DATASET> for a <TKN_Q> that semantically matches the User Query.
    2. If a match is found, reply politely using ONLY the information provided in the corresponding <TKN_A>.
    3. If the User Query does not match any existing <TKN_INTENT>, reply exactly with the word: ESCALATE
    """
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt
    )
    bot_reply = response.text.strip()
    
    # Trigger Escalation Protocol
    if "ESCALATE" in bot_reply:
        background_tasks.add_task(send_email_ticket, message.user_email, message.question)
        return {"reply": "Generally it takes 24-48 hours to respond"}
    
    # Standard FAQ Response
    return {"reply": bot_reply}

