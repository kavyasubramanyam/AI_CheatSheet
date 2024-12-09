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

def display_chat_history():
    """Display the chat history in the interface."""
    # Skip the first system message

    messages_to_display = list(reversed(st.session_state.messages[1:]))

    for message in messages_to_display:  
        if message["role"] == "user":
            content = message['content'].strip()
            
            # Replace LaTeX-style math notation
            content = content.replace('\\[', '$$')
            content = content.replace('\\]', '$$')
            content = content.replace('\\(', '$')
            content = content.replace('\\)', '$')
            content = content.replace('\\mathbb{R}', 'ℝ')
            
            # Handle math replacements
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
                        in_code_block = False
                        if code_buffer:
                            formatted_lines.append(f"```python\n{''.join(code_buffer)}```")
                            code_buffer = []
                    else:
                        in_code_block = True
                elif in_code_block:
                    code_buffer.append(line + '\n')
                else:
                    formatted_lines.append(line)
            
            formatted_content = '\n'.join(formatted_lines)
            st.write(f"🤖 **Assistant:** {formatted_content}")
        elif message["role"] == "user":
            st.write(f"🧑 **You:** {message['content']}")
            st.markdown("---")

            
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
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {"role": "system", "content": "You are a knowledgeable tutor who maintains context across conversations. Build upon previous discussions and provide comprehensive, connected explanations."}
        ]

    st.title("AI Tutor with Dynamic Cheat Sheet")
    
    # Create two columns
    chat_col, cheatsheet_col = st.columns([2, 1])
    
    with chat_col:
        # Create placeholder for chat history
        chat_placeholder = st.empty()
        
        # Create a form for the input
        with st.form(key='query_form', clear_on_submit=True):
            query = st.text_input("Ask a question:", key="query_input")
            col1, col2 = st.columns([1, 4])
            
            with col1:
                submitted = st.form_submit_button("Submit")
            
            if submitted and query.strip():
                # Add user message
                st.session_state.messages.append({"role": "user", "content": query})
                
                # Get response
                answer = get_openai_response(query)
                
                # Add assistant message
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Update cheat sheet
                structured_response = summarize_with_structure(answer)
                update_cheat_sheet(
                    cheat_sheet_format=st.session_state.cheat_sheet_format,
                    question=query,
                    structured_response=structured_response,
                )
                
                # Clear the form
                query = ""
        
        # Display chat history after form submission
        display_chat_history()
        
        if st.button("Clear Conversation"):
            st.session_state.messages = [st.session_state.messages[0]]

    with cheatsheet_col:
        # Display current cheat sheet
        display_cheat_sheet(st.session_state.cheat_sheet_format)
        
        # Add the cheat sheet manager
        manage_cheat_sheets()
if __name__ == "__main__":
    main()