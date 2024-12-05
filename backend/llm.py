# llm.py
import os
import re
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain.memory import ConversationBufferMemory

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("GROQ_SECRET_ACCESS_KEY")
if not api_key:
    print("API key is missing from the .env file!")
    exit(1)

class HTMLGenerator:
    def __init__(self):
        # Initialize memory
        self.memory = ConversationBufferMemory(return_messages=True)
        
        # Create the chat model
        self.chat_model = ChatGroq(
            temperature=1,
            model_name="llama-3.1-70b-versatile",
            api_key=api_key,
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
        
    def extract_html_code(self, response):
        """Extract HTML code between ``` delimiters"""
        html_match = re.search(r'```html\s*(.*?)```', response, re.DOTALL)
        
        if html_match:
            return html_match.group(1).strip()
        
        print("No HTML code between ``` delimiters found. Using entire response.")
        return response.strip()
    
    def write_html_to_file(self, html_content, filename='output.html'):
        """Write HTML content to a file"""
        try:
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(html_content)
            print(f"HTML file '{filename}' has been created successfully!")
        except Exception as e:
            print(f"Error writing to file: {e}")
        return html_content
    
    def generate_html(self, user_input):
        """Generate HTML based on user input while maintaining conversation history"""
        try:
            # Add user message to memory
            self.memory.chat_memory.add_message(HumanMessage(content=user_input))
            
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
                "input": user_input
            })
            
            # Extract HTML
            html_content = self.extract_html_code(response)
            
            # Write to file
            final_html = self.write_html_to_file(html_content)
            
            # Add AI message to memory
            self.memory.chat_memory.add_message(AIMessage(content=response))
            
            # Print results
            print("\n--- Generated HTML ---")
            print(final_html)
            
            return final_html
        
        except Exception as e:
            print(f"Error in HTML generation: {e}")
            return None

def main():
    # Create HTML generator instance
    html_generator = HTMLGenerator()
    
    print("HTML Generation Chat (type 'exit' to quit)")
    
    while True:
        # Get user input
        user_input = input("\nEnter your HTML generation/customization prompt: ")
        
        # Check for exit
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        
        # Generate HTML
        html_generator.generate_html(user_input)

if __name__ == "__main__":
    main()