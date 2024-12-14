import openai
import json
import streamlit as st

if "current_section" not in st.session_state:
    st.session_state.current_section = None

api_key = None

#get key from streamlit secrets
#or hard code in your api key

api_key = st.secrets["OPENAI_API_KEY"]

openai.api_key = api_key


def get_openai_response(query):

    try:
        response = openai.chat.completions.create(
            messages=st.session_state.messages,
            model="gpt-4o-mini",
        )
        
        # get parsed response
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"ERROR - OpenAI call failed: {str(e)}")
        return f"Error fetching response: {str(e)}"

def summarize_with_structure(response):
  # use the response as query to create cheet sheet, used claude to help create the summary request structure 
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
        
        # parse the json content
        start_idx = content.find('{')
        end_idx = content.rfind('}') + 1
        
        if start_idx != -1 and end_idx != -1:
            json_str = content[start_idx:end_idx]
            try:
                # if its a valid json string, parse it
                structured_content = json.loads(json_str)
                print("Structured content:", json.dumps(structured_content, indent=2))
                return structured_content
            #otherwise, structure the string into a simple "topic" and "content"
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {str(e)}")
                return {
                    "Topic": {
                        "Content": response.strip()
                    }
                }
        
        return {"Error": "Failed to structure content"}

    except Exception as e:
        print(f"Summarization error: {str(e)}")
        return {"Error": str(e)}