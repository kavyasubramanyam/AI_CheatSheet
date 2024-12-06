import openai

# Define the expected JSON schema for the cheat sheet
cheat_sheet_function = {
    "name": "generate_cheat_sheet",
    "description": "Organize content into a structured cheat sheet format",
    "parameters": {
        "type": "object",
        "properties": {
            "Title": {
                "type": "string",
                "description": "Overarching subject of the cheat sheet"
            },
            "Topics": {
                "type": "object",
                "additionalProperties": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "description": "A subtopic within this topic"
                    }
                },
                "description": "Key topics with their corresponding subtopics"
            }
        },
        "required": ["Title", "Topics"]
    }
}
