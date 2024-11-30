import os
import re
from groq import Groq
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the API key from environment variables
api_key = os.getenv("GROQ_SECRET_ACCESS_KEY")
if not api_key:
    print("API key is missing from the .env file!")
    exit(1)

# Initialize the Groq client with the API key
client = Groq(api_key=api_key)

# Start the chat with the system message that sets the context
system_message = {
    "role": "system",
    "content": '''You are a helpful assistant and a pro in creating HTML codes with Tailwind. If the color requested by the user is not defined by tailwind you have to define its class.You only need to generate the code, which will be displayed on a webpage. If any other prompt is given,
    just reply 'out of domain'. The user will provide instructions for customizing the generated page.'''
}

# Function to extract HTML code between ``` delimiters
def extract_html_code(response):
    # Use regex to find content between ``` and ```
    html_match = re.search(r'```html\s*(.*?)```', response, re.DOTALL)
    
    if html_match:
        return html_match.group(1).strip()
    
    # If no ``` delimiters found, return the entire response
    print("No HTML code between ``` delimiters found. Using entire response.")
    return response.strip()

# Function to write HTML to a file
def write_html_to_file(html_content, filename='output.html'):
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            file.write(html_content)
        print(f"HTML file '{filename}' has been created successfully!")
    except Exception as e:
        print(f"Error writing to file: {e}")

# Begin the conversation with the user
def chat_with_assistant(user_input):
    # Send the system and user message to Groq API
    completion = client.chat.completions.create(
        model="llama-3.1-70b-versatile",  # Model selection
        messages=[
            system_message,
            {"role": "user", "content": user_input}
        ],
        temperature=1,
        max_tokens=1024,
        top_p=1,
        stream=False,  # Changed to False to get full response
        stop=None,
    )

    # Get the full response
    response = completion.choices[0].message.content
    
    # Print the original response
    print("Original Response:")
    print(response)
    
    # Extract HTML code
    html_content = extract_html_code(response)
    
    # Print extracted HTML
    print("\nExtracted HTML:")
    print(html_content)
    
    # Write the extracted HTML to a file
    write_html_to_file(html_content)

# Main interaction loop
while True:
    user_input = input("Enter your HTML generation prompt (or 'exit' to quit): ")
    if user_input.lower() == "exit":
        print("Goodbye!")
        break
    chat_with_assistant(user_input)