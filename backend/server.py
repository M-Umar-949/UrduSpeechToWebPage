# Server.py
import os
import re
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory
from fastapi.responses import JSONResponse

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class HTMLGenerator:
    def __init__(self):
        # Retrieve API keys
        self.groq_api_key = os.getenv("GROQ_SECRET_ACCESS_KEY")
        self.upload_folder = 'uploads'
        
        # Create uploads directory if not exists
        os.makedirs(self.upload_folder, exist_ok=True)
        
        # Validate API key
        if not self.groq_api_key:
            logger.error("Groq API key is missing from the .env file!")
            raise ValueError("Groq API key is required")
        
        # Initialize memory
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Create the chat model
        self.chat_model = ChatGroq(
            temperature=1,
            model_name="llama-3.2-90b-vision-preview",
            api_key=self.groq_api_key,
            max_tokens=2048
        )
        
        # Create the system prompt
        self.system_prompt = SystemMessage(content='''You are a helpful assistant and a pro in creating HTML 
        codes with Tailwind. If the color requested by the user is not defined by
        tailwind you have to define its class. You only need to generate the code, 
        which will be displayed on a webpage. If any other prompt is given,
        just reply 'out of domain'. The user will provide instructions for 
        customizing the generated page.''')
        
        # Add system message to memory
        self.memory.chat_memory.add_message(self.system_prompt)
        
        # Store the last generated HTML
        self.last_generated_html = None
    
    def extract_html_code(self, response):
        """Extract HTML code between ``` delimiters"""
        html_match = re.search(r'```html\s*(.*?)```', response, re.DOTALL)
        
        if html_match:
            return html_match.group(1).strip()
        
        logger.warning("No HTML code between ``` delimiters found. Using entire response.")
        return response.strip()
    
    def write_html_to_file(self, html_content, filename='output.html'):
        """Write HTML content to a file"""
        try:
            filepath = os.path.join(self.upload_folder, filename)
            with open(filepath, 'w', encoding='utf-8') as file:
                file.write(html_content)
            logger.info(f"HTML file '{filename}' has been created successfully!")
            return html_content
        except Exception as e:
            logger.error(f"Error writing to file: {e}")
            return None
    
    def generate_html_from_transcription(self, transcription):
        """Generate HTML based on transcription while maintaining conversation history"""
        try:
            # Add user message to memory
            self.memory.chat_memory.add_message(HumanMessage(content=transcription))
            
            # Retrieve conversation history
            history = self.memory.chat_memory.messages
            
            # Create prompt template with memory
            prompt = ChatPromptTemplate.from_messages([
                self.system_prompt,
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}")
            ])
            
            # Create the chain
            chain = prompt | self.chat_model | StrOutputParser()
            
            # Generate response
            response = chain.invoke({
                "history": history[1:],  # Exclude system message from history
                "input": transcription
            })
            
            # Extract HTML
            html_content = self.extract_html_code(response)
            
            # Write to file
            final_html = self.write_html_to_file(html_content)
            
            # Store the last generated HTML
            self.last_generated_html = final_html
            
            # Add AI message to memory
            self.memory.chat_memory.add_message(AIMessage(content=response))
            
            logger.info("\n--- Generated HTML ---")
            logger.info(final_html)
            
            return final_html
        
        except Exception as e:
            logger.error(f"Error in HTML generation: {e}")
            return None
    
    def modify_html(self, modification_prompt):
        """Modify the last generated HTML based on user instructions"""
        try:
            # Check if there's a previous HTML to modify
            if not self.last_generated_html:
                logger.error("No previous HTML to modify")
                return None
            
            # Add user message to memory
            self.memory.chat_memory.add_message(HumanMessage(content=modification_prompt))
            
            # Retrieve conversation history
            history = self.memory.chat_memory.messages
            
            # Create prompt template with memory
            prompt = ChatPromptTemplate.from_messages([
                self.system_prompt,
                MessagesPlaceholder(variable_name="history"),
                ("human", "Here's the existing HTML: ```html\n{existing_html}\n```\n\nPlease modify the HTML based on this instruction: {modification}")
            ])
            
            # Create the chain
            chain = prompt | self.chat_model | StrOutputParser()
            
            # Generate response
            response = chain.invoke({
                "history": history[1:],  # Exclude system message from history
                "existing_html": self.last_generated_html,
                "modification": modification_prompt
            })
            
            # Extract HTML
            html_content = self.extract_html_code(response)
            
            # Write to file
            final_html = self.write_html_to_file(html_content)
            
            # Update the last generated HTML
            self.last_generated_html = final_html
            
            # Add AI message to memory
            self.memory.chat_memory.add_message(AIMessage(content=response))
            
            logger.info("\n--- Modified HTML ---")
            logger.info(final_html)
            
            return final_html
        
        except Exception as e:
            logger.error(f"Error in HTML modification: {e}")
            return None

# FastAPI Application
app = FastAPI()

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global HTML Generator
html_generator = HTMLGenerator()

# Colab server URL for transcription
COLAB_URL = os.getenv("COLAB_TRANSCRIPTION_URL", "https://your-default-ngrok-url.ngrok-free.app/transcribe")

@app.post("/upload")
async def upload_audio(audio: UploadFile = File(...)):
    try:
        # Validate file
        if not audio.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Ensure it's a supported audio file
        allowed_extensions = ['.wav', '.mp3', '.ogg']
        if not any(audio.filename.lower().endswith(ext) for ext in allowed_extensions):
            raise HTTPException(status_code=400, detail="Only WAV, MP3, and OGG files are supported")

        # Save the uploaded file locally
        filepath = os.path.join(html_generator.upload_folder, 'recording.wav')
        with open(filepath, 'wb') as buffer:
            buffer.write(await audio.read())
        
        logger.info(f"File saved locally: {filepath}")
        
        # Send the file to the Colab server for transcription
        with open(filepath, 'rb') as f:
            files = {'file': ('recording.wav', f, 'audio/wav')}
            logger.info(f"Sending file to Colab URL: {COLAB_URL}")
            
            try:
                response = requests.post(COLAB_URL, files=files, timeout=30)
                
                logger.info(f"Response status code: {response.status_code}")
                logger.info(f"Response content: {response.text}")
                
                # Check if the transcription was successful
                if response.status_code == 200:
                    data = response.json()
                    transcription = data.get('transcription', '')
                    
                    # Save the transcription to a local file
                    transcription_file = os.path.join(html_generator.upload_folder, "transcription.txt")
                    with open(transcription_file, "w", encoding='utf-8') as txt_file:
                        txt_file.write(transcription)
                    
                    # Generate HTML from transcription
                    html_output = html_generator.generate_html_from_transcription(transcription)
                    
                    return JSONResponse({
                        "message": "File uploaded, transcribed, and HTML generated successfully",
                        "transcription": transcription,
                        "html_content": html_output
                    })
                else:
                    return JSONResponse({
                        "message": f"Error {response.status_code}: {response.text}"
                    }, status_code=response.status_code)
            
            except requests.RequestException as e:
                logger.error(f"Request error: {e}")
                return JSONResponse({
                    "message": f"Request failed: {str(e)}"
                }, status_code=500)

    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()