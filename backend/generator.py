import os
import re
import logging
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory

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
            model_name="llama-3.1-70b-versatile",
            api_key=self.groq_api_key,
            max_tokens=2048,
            response_format={"type": "json_object"},
        )
        
        # Create the system prompt
        self.system_prompt = SystemMessage(content='''You are a helpful assistant and 
        a pro in creating HTML codes with Tailwind. If the color requested by the user is not defined by
        tailwind you have to define its class. You only need to generate the code, 
        which will be displayed on a webpage. Insert the html code in the 'html' json key. 
        If any other prompt is given, just reply 'out of domain'. 
        The user will provide instructions for customizing the generated page.
        Add javascript where necessary. You have to generate complete html code''')
        
        # Add system message to memory
        self.memory.chat_memory.add_message(self.system_prompt)
        
        # Store the last generated HTML
        self.last_generated_html = None
    
    def extract_html_code(self, response):
        """Extract HTML code from JSON response with an HTML key"""
        try:
            # Parse the response as JSON
            response_json = json.loads(response)
            
            # Check if 'html' key exists in the JSON
            if 'html' in response_json:
                return response_json['html'].strip()
            
            logger.warning("No 'html' key found in JSON response.")
            return response.strip()
        
        except json.JSONDecodeError:
            logger.warning("Response is not a valid JSON. Using entire response.")
            
            # Fallback to previous method of finding HTML between ```
            html_match = re.search(r'```html\s*(.*?)```', response, re.DOTALL)
            
            if html_match:
                return html_match.group(1).strip()
            
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