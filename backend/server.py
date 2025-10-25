from fastapi import FastAPI, APIRouter, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime
import json
import asyncio
import base64
import io
import google.generativeai as genai

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Initialize Gemini client
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Models
class Message(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    fileInfo: Optional[dict] = None

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    messages: List[Message] = []
    createdAt: datetime = Field(default_factory=datetime.utcnow)
    updatedAt: datetime = Field(default_factory=datetime.utcnow)

class ChatRequest(BaseModel):
    message: str
    sessionId: str

class ChatResponse(BaseModel):
    message: Message
    sessionId: str

class FileUploadResponse(BaseModel):
    fileId: str
    filename: str
    content: str
    analysis: str

# Routes
@api_router.get("/")
async def root():
    return {"message": "punter613's AI Assistant Backend - Ready to serve!"}

@api_router.get("/sessions", response_model=List[Session])
async def get_sessions():
    """Get all chat sessions"""
    try:
        sessions_cursor = db.sessions.find().sort("updatedAt", -1)
        sessions = []
        async for session_data in sessions_cursor:
            session_data['_id'] = str(session_data['_id'])
            # Convert message timestamps
            for msg in session_data.get('messages', []):
                if isinstance(msg.get('timestamp'), str):
                    msg['timestamp'] = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
            sessions.append(Session(**session_data))
        return sessions
    except Exception as e:
        logger.error(f"Error getting sessions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")

@api_router.post("/sessions", response_model=Session)
async def create_session():
    """Create a new chat session"""
    try:
        session = Session(title="New Conversation")
        session_dict = session.dict()
        session_dict['messages'] = []
        
        result = await db.sessions.insert_one(session_dict)
        session_dict['_id'] = str(result.inserted_id)
        
        return session
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(status_code=500, detail="Failed to create session")

@api_router.get("/sessions/{session_id}", response_model=Session)
async def get_session(session_id: str):
    """Get a specific session with all messages"""
    try:
        session_data = await db.sessions.find_one({"id": session_id})
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session_data['_id'] = str(session_data['_id'])
        # Convert message timestamps
        for msg in session_data.get('messages', []):
            if isinstance(msg.get('timestamp'), str):
                msg['timestamp'] = datetime.fromisoformat(msg['timestamp'].replace('Z', '+00:00'))
        
        return Session(**session_data)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve session")

async def generate_ai_response(message: str, conversation_history: List[Message]) -> str:
    """Generate AI response using Google Gemini 2.0 Flash"""
    try:
        # Build conversation context for Gemini
        conversation_parts = []
        
        # Add system context
        conversation_parts.append({
            "parts": [{
                "text": """You are punter613's AI Assistant - a helpful, knowledgeable, and versatile AI companion. You can:

- Help with coding and development in any programming language
- Analyze documents, files, and data
- Assist with creative tasks and problem-solving
- Provide detailed explanations and tutorials
- Help with app development and technical architecture

Be conversational, helpful, and comprehensive in your responses. Use markdown formatting when appropriate, especially for code blocks. Be engaging and show personality while remaining professional."""
            }]
        })
        
        # Add recent conversation history (last 8 messages for context)
        recent_history = conversation_history[-8:] if len(conversation_history) > 8 else conversation_history
        for msg in recent_history:
            role = "user" if msg.type == "user" else "model"
            conversation_parts.append({
                "role": role,
                "parts": [{"text": msg.content}]
            })
        
        # Add current message
        conversation_parts.append({
            "role": "user",
            "parts": [{"text": message}]
        })
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Start chat with history
        chat = model.start_chat(history=conversation_parts[1:-1])  # Exclude system prompt and current message
        
        # Generate response
        response = await asyncio.to_thread(
            chat.send_message,
            message,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                max_output_tokens=1500,
                top_p=0.9,
                top_k=40
            )
        )
        
        return response.text
        
    except Exception as e:
        logger.error(f"Error generating Gemini AI response: {e}")
        # Fallback to a helpful error message
        return f"""I'm having a brief technical issue connecting to my AI processing system. Let me try to help you anyway!

**You asked about:** "{message[:100]}..."

While I work on resolving the connection, here's what I can suggest:
- If this is about coding, I can help with syntax, debugging, and best practices
- For app development, I can guide you through planning and implementation
- For file analysis, feel free to upload documents for review
- For creative projects, I can help brainstorm and structure ideas

Please try your question again in a moment, or let me know if you'd like me to help with something specific while I reconnect to full processing power!"""

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get AI response"""
    try:
        # Get session
        session_data = await db.sessions.find_one({"id": request.sessionId})
        if not session_data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Create user message
        user_message = Message(
            type="user",
            content=request.message,
            timestamp=datetime.utcnow()
        )
        
        # Get conversation history
        conversation_history = []
        for msg_data in session_data.get('messages', []):
            msg_data['timestamp'] = datetime.utcnow() if not msg_data.get('timestamp') else msg_data['timestamp']
            conversation_history.append(Message(**msg_data))
        
        # Generate AI response
        ai_content = await generate_ai_response(request.message, conversation_history)
        
        ai_message = Message(
            type="assistant",
            content=ai_content,
            timestamp=datetime.utcnow()
        )
        
        # Update session with both messages
        updated_messages = conversation_history + [user_message, ai_message]
        messages_dict = [msg.dict() for msg in updated_messages]
        
        # Update session title if it's the first message
        update_data = {
            "messages": messages_dict,
            "updatedAt": datetime.utcnow()
        }
        
        if len(conversation_history) == 0:
            # Generate title from first message
            title = request.message[:50] + "..." if len(request.message) > 50 else request.message
            update_data["title"] = title
        
        await db.sessions.update_one(
            {"id": request.sessionId},
            {"$set": update_data}
        )
        
        return ChatResponse(message=ai_message, sessionId=request.sessionId)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat: {e}")
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@api_router.post("/upload", response_model=FileUploadResponse)
async def upload_file(file: UploadFile = File(...)):
    """Upload and analyze a file"""
    try:
        # Read file content
        content = await file.read()
        
        # Convert to base64 for storage
        file_base64 = base64.b64encode(content).decode('utf-8')
        
        # Analyze file content based on type
        analysis = ""
        file_content_text = ""
        
        if file.content_type and file.content_type.startswith('text/'):
            file_content_text = content.decode('utf-8')
            analysis = f"📄 **Text File Analysis**\n\n**Filename:** {file.filename}\n**Size:** {len(content)} bytes\n**Type:** {file.content_type}\n\n**Content Preview:**\n```\n{file_content_text[:500]}{'...' if len(file_content_text) > 500 else ''}\n```"
        
        elif file.content_type and file.content_type.startswith('image/'):
            analysis = f"🖼️ **Image File Uploaded**\n\n**Filename:** {file.filename}\n**Size:** {len(content)} bytes\n**Type:** {file.content_type}\n\nImage has been uploaded successfully. I can analyze the visual content if you ask me about it!"
        
        elif file.filename and (file.filename.endswith('.js') or file.filename.endswith('.jsx') or 
                               file.filename.endswith('.py') or file.filename.endswith('.java') or
                               file.filename.endswith('.cpp') or file.filename.endswith('.c')):
            file_content_text = content.decode('utf-8')
            analysis = f"💻 **Code File Analysis**\n\n**Filename:** {file.filename}\n**Size:** {len(content)} bytes\n**Lines:** {len(file_content_text.splitlines())}\n\n**Code Preview:**\n```{file.filename.split('.')[-1]}\n{file_content_text[:500]}{'...' if len(file_content_text) > 500 else ''}\n```\n\nI can help you review, optimize, or explain this code!"
        
        else:
            analysis = f"📁 **File Uploaded**\n\n**Filename:** {file.filename}\n**Size:** {len(content)} bytes\n**Type:** {file.content_type or 'Unknown'}\n\nFile uploaded successfully! I can help analyze its contents if you have specific questions."
        
        # Store file info in database
        file_doc = {
            "id": str(uuid.uuid4()),
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "content": file_base64,
            "text_content": file_content_text,
            "uploaded_at": datetime.utcnow()
        }
        
        result = await db.files.insert_one(file_doc)
        
        return FileUploadResponse(
            fileId=file_doc["id"],
            filename=file.filename,
            content=file_content_text,
            analysis=analysis
        )
        
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=f"File upload error: {str(e)}")

@api_router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a chat session"""
    try:
        result = await db.sessions.delete_one({"id": session_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": "Session deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete session")

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)