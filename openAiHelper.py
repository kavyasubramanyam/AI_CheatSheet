import openai
import json
import streamlit as st
import os
from dotenv import load_dotenv
if "current_section" not in st.session_state:
    st.session_state.current_section = None

# Set your OpenAI API key
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

cheat_sheet_function = {
    "name": "generate_cheat_sheet",
    "description": "Creates a structured cheat sheet with support for deeply nested information",
    "parameters": {
        "type": "object",
        "properties": {
            "sections": {
                "type": "object",
                "description": "Main sections of the cheat sheet",
                "additionalProperties": {
                    "type": "object",
                    "description": "Topics within a section",
                    "additionalProperties": {
                        "oneOf": [
                            {
                                "type": "string",
                                "description": "Direct content"
                            },
                            {
                                "type": "object",
                                "description": "Nested subsections",
                                "additionalProperties": {
                                    "oneOf": [
                                        {
                                            "type": "string",
                                            "description": "Subsection content"
                                        },
                                        {
                                            "type": "object",
                                            "description": "Further nested content",
                                            "additionalProperties": {}
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            }
        },
        "required": ["sections"]
    }
}
def get_openai_response(query):
    """
    Gets a response from OpenAI with conversation history.
    """
    try:
        # Add the new user query to messages
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Get completion from OpenAI
        response = openai.chat.completions.create(
            messages=st.session_state.messages,
            model="gpt-4o-mini",
        )
        
        # Get the response
        answer = response.choices[0].message.content.strip()
        
        # Add the assistant's response to the message history
        st.session_state.messages.append({"role": "assistant", "content": answer})
        
        return answer
    except Exception as e:
        print(f"ERROR - OpenAI call failed: {str(e)}")
        return f"Error fetching response: {str(e)}"

def summarize_with_structure(response):
    """
    Summarizes and organizes the OpenAI response into a structured format.
    """
    try:
        summary_request = f"""
        Create a structured cheat sheet from the following content:

        Rules:
        1. Extract the main topic as the top-level key
        2. Organize sub-topics under the main topic
        3. Include all important details, examples, and implementations
        4. Format code snippets cleanly
        5. Format mathematical expressions clearly

        Return the content in this JSON structure (replace with actual content):
        {{
            "Topic Name": {{
                "Definition": "Clear explanation",
                "Key Concepts": {{
                    "Concept 1": "Explanation",
                    "Concept 2": "Explanation"
                }},
                "Examples": {{
                    "Example 1": "Details",
                    "Example 2": "Details"
                }},
                "Implementation": {{
                    "Step 1": "Description",
                    "Code": "Code snippet if applicable"
                }}
            }}
        }}

        Content to structure:
        {response}

        Return ONLY the JSON object, nothing else.
        """

        chat_response = openai.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a structured content generator. Always return perfectly formatted JSON."
                },
                {
                    "role": "user", 
                    "content": summary_request
                }
            ],
            model="gpt-4o-mini"
        )

        content = chat_response.choices[0].message.content.strip()
        
        # Clean up the response to ensure it's valid JSON
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx:end_idx]
            try:
                # Parse the JSON string
                structured_content = json.loads(json_str)
                print("Structured content:", json.dumps(structured_content, indent=2))
                return structured_content
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                # Create a basic structure if parsing fails
                return {
                    "Topic": {
                        "Content": response.strip()
                    }
                }
        
        return {"Error": "Failed to structure content"}

    except Exception as e:
        print(f"Summarization error: {str(e)}")
        return {"Error": str(e)}