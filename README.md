AI Cheat Sheet Generator

Educational tool with customizable cheat sheets using AI. Built with Streamlit and OpenAI's GPT-4.
Features

Interactive chat interface with an AI tutor
Dynamic cheat sheet generation
LaTeX support for mathematical expressions
Ability to selectively add content to cheat sheets
Save and load multiple cheat sheets
Export cheat sheets to Word documents

Installation

Clone the repository:

installation requirements in requirements.txt

Set up your OpenAI API key in Streamlit secrets:


Create a .streamlit/secrets.toml file
Add your API key: OPENAI_API_KEY = "your-key-here"

Usage

Start the application:

streamlit run app.py

ALTERNATE USE: use the link https://aicheatsheet.streamlit.app/ to run the app

Ask questions in the chat interface
Click the + button next to any response section to add it to your cheat sheet
Use the sidebar to manage and download your cheat sheets

Dependencies

streamlit
openai
python-docx
pylatexenc

SOURCES: Utilized Claude.ai to help implement the OpenAIHelper.py, CheatSheet.py, app.py in additional to manually coding features
