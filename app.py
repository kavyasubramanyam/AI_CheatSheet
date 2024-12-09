import streamlit as st
from openAiHelper import get_openai_response, summarize_with_structure
from CheatSheet import update_cheat_sheet, display_cheat_sheet
from datetime import datetime
if "cheat_sheets" not in st.session_state:
    st.session_state.cheat_sheets = {}
if "current_cheat_sheet" not in st.session_state:
    st.session_state.current_cheat_sheet = None
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "You are a knowledgeable tutor who maintains context across conversations. Build upon previous discussions and provide comprehensive, connected explanations."}
    ]
def handle_cheat_sheet_query(query):
    """
    Process a user's query about a cheat sheet topic and update the cheat sheet accordingly.
    """
    try:
        with st.spinner("Processing..."):
            # Get the response from OpenAI
            answer = get_openai_response(query)
            # Summarize the response with structured content
            structured_response = summarize_with_structure(answer)
            # Update the cheat sheet with the new content
            update_cheat_sheet(
                cheat_sheet_format=st.session_state.cheat_sheet_format,
                question=query,
                structured_response=structured_response
            )
            # Rerun to update the chat display
            st.rerun()
    except Exception as e:
        st.error(f"Error: {str(e)}")
def display_chat_history():
    """Display the chat history in the interface."""
    for message in st.session_state.messages[1:]:  # Skip the system message
        if message["role"] == "user":
            st.write(f"🧑 **You:** {message['content']}")
        else:
            # Get the response content
            content = message['content'].strip()
            
            # Replace LaTeX-style math notation with proper rendering
            content = content.replace('\\[', '$$')
            content = content.replace('\\]', '$$')
            content = content.replace('\\(', '$')
            content = content.replace('\\)', '$')
            
            # Replace \mathbb{R} with ℝ
            content = content.replace('\\mathbb{R}', 'ℝ')
            
            # Replace other common math symbols
            math_replacements = {
                '\\times': '×',
                '\\in': '∈',
                '\\rightarrow': '→',
                '\\leftarrow': '←',
                '\\leq': '≤',
                '\\geq': '≥',
                '\\neq': '≠',
                '\\alpha': 'α',
                '\\beta': 'β',
                '\\gamma': 'γ',
                '\\delta': 'δ',
                '\\theta': 'θ',
                '\\lambda': 'λ',
                '\\sigma': 'σ',
                '\\pi': 'π',
                '\\infty': '∞'
            }
            
            for latex, symbol in math_replacements.items():
                content = content.replace(latex, symbol)
            
            # Handle code blocks
            lines = content.split('\n')
            formatted_lines = []
            in_code_block = False
            code_buffer = []
            
            for line in lines:
                if line.strip().startswith('```'):
                    if in_code_block:
                        # End code block
                        in_code_block = False
                        if code_buffer:
                            formatted_lines.append(f"```python\n{''.join(code_buffer)}```")
                            code_buffer = []
                    else:
                        # Start code block
                        in_code_block = True
                elif in_code_block:
                    code_buffer.append(line + '\n')
                else:
                    formatted_lines.append(line)
            
            # Join the formatted lines
            formatted_content = '\n'.join(formatted_lines)
            
            # Display the message
            st.write(f"🤖 **Assistant:** {formatted_content}")
            
def save_current_cheat_sheet():
    """Save the current cheat sheet with a timestamp"""
    if st.session_state.cheat_sheet_format:  # Only save if there's content
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        title = st.session_state.get("current_title", "Untitled Cheat Sheet")
        key = f"{title} ({timestamp})"
        st.session_state.cheat_sheets[key] = st.session_state.cheat_sheet_format.copy()
        st.session_state.current_cheat_sheet = key
        return True
    return False
def load_cheat_sheet(key):
    """Load a selected cheat sheet"""
    if key in st.session_state.cheat_sheets:
        st.session_state.cheat_sheet_format = st.session_state.cheat_sheets[key].copy()
        st.session_state.current_cheat_sheet = key
def manage_cheat_sheets():
    """Interface for managing multiple cheat sheets"""
    st.sidebar.markdown("---")
    st.sidebar.subheader("Cheat Sheet Manager")
    # Add New Cheat Sheet button at the top
    if st.sidebar.button("New Cheat Sheet"):
        st.session_state.cheat_sheet_format = {}  # Clear the current cheat sheet
        st.session_state.current_cheat_sheet = None
        st.session_state.messages = [st.session_state.messages[0]]  # Reset conversation but keep system message
        st.rerun()
    # Save current cheat sheet
    title = st.sidebar.text_input("Cheat Sheet Title", 
                                key="current_title",
                                value="Untitled Cheat Sheet")
    
    if st.sidebar.button("Save Current Cheat Sheet"):
        if save_current_cheat_sheet():
            st.sidebar.success(f"Saved cheat sheet: {title}")
        else:
            st.sidebar.warning("No content to save!")
    # Display saved cheat sheets
    if st.session_state.cheat_sheets:
        st.sidebar.markdown("### Saved Cheat Sheets")
        selected_sheet = st.sidebar.selectbox(
            "Select a cheat sheet to load",
            options=list(st.session_state.cheat_sheets.keys()),
            index=list(st.session_state.cheat_sheets.keys()).index(st.session_state.current_cheat_sheet) 
            if st.session_state.current_cheat_sheet else 0
        )
        
        col1, col2 = st.sidebar.columns(2)
        
        with col1:
            if st.button("Load Selected"):
                load_cheat_sheet(selected_sheet)
                # Reset conversation when loading a different cheat sheet
                st.session_state.messages = [st.session_state.messages[0]]
                st.success(f"Loaded: {selected_sheet}")
                st.rerun()
        
        with col2:
            if st.button("Delete Selected"):
                if selected_sheet == st.session_state.current_cheat_sheet:
                    st.session_state.cheat_sheet_format = {}
                    st.session_state.current_cheat_sheet = None
                del st.session_state.cheat_sheets[selected_sheet]
                st.success(f"Deleted: {selected_sheet}")
                st.rerun()
def main():
    st.set_page_config(page_title="AI Tutor with Cheat Sheet", layout="wide")
    if "cheat_sheet_format" not in st.session_state:
        st.session_state.cheat_sheet_format = {}
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False

    st.title("AI Tutor with Dynamic Cheat Sheet")
    
    # Create two columns
    chat_col, cheatsheet_col = st.columns([2, 1])
    
    with chat_col:
        # Display chat history
        display_chat_history()
        
        # Input Section
        query = st.text_input("Ask a question:", key="user_input")
        col1, col2 = st.columns([1, 4])
        
        with col1:
            if st.button("Submit") and query.strip() and not st.session_state.processing_complete:
                try:
                    with st.spinner("Processing..."):
                        # Store the user's message
                        st.session_state.messages.append({"role": "user", "content": query})
                        
                        # Fetch the response
                        answer = get_openai_response(query)
                        
                        # Store the assistant's response
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                        
                        # Summarize with context
                        structured_response = summarize_with_structure(answer)
                        
                        # Update the cheat sheet
                        update_cheat_sheet(
                            cheat_sheet_format=st.session_state.cheat_sheet_format,
                            question=query,
                            structured_response=structured_response,
                        )
                        
                        # Mark processing as complete
                        st.session_state.processing_complete = True
                        
                        # Clear the input
                        st.session_state.user_input = ""
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
        
        with col2:
            if st.button("Clear Conversation"):
                st.session_state.messages = [st.session_state.messages[0]]  # Keep only the system message
                st.session_state.processing_complete = False

    with cheatsheet_col:
        # Display current cheat sheet
        display_cheat_sheet(st.session_state.cheat_sheet_format)
        
        # Add the cheat sheet manager
        manage_cheat_sheets()

    # Reset processing_complete at the end of the script
    if st.session_state.processing_complete:
        st.session_state.processing_complete = False
if __name__ == "__main__":
    main()