
import os
import sys
import json
import requests
import inspect
from typing import List, Callable, Any, Dict

# This class mocks the Google ADK Agent behavior using raw REST API
# to ensure compatibility with Python 3.8 where the official SDK is not available.

class Agent:
    def __init__(self, model: str, name: str, instruction: str, tools: List[Callable]):
        self.model = model
        self.name = name
        self.instruction = instruction
        self.tools = {t.__name__: t for t in tools}
        self.api_key = os.environ.get("GOOGLE_API_KEY")
        
        if not self.api_key:
            print("ERROR: GOOGLE_API_KEY environment variable not found.")
            print("Please set it using: $env:GOOGLE_API_KEY='your_key'")
            sys.exit(1)

        self.url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        self.history = []

    def _get_tool_definitions(self):
        # Convert python functions to Gemini Tool definitions
        # This is a basic simplified converter
        funcs = []
        for name, func in self.tools.items():
            func_def = {
                "name": name,
                "description": func.__doc__.strip() if func.__doc__ else "No description",
                "parameters": {
                    "type": "OBJECT",
                    "properties": {
                         "query": {"type": "STRING"} # Simplified: assumption for search
                    },
                    "required": ["query"] if "query" in inspect.signature(func).parameters else []
                }
            }
            # Special handling for get_current_date (no args)
            if name == "get_current_date":
                func_def["parameters"] = {"type": "OBJECT", "properties": {}}
            
            funcs.append(func_def)
            
        return [{"function_declarations": funcs}]

    def run(self, prompt: str) -> str:
        # Add user message to history
        self.history.append({"role": "user", "parts": [{"text": prompt}]})

        # Add system instruction to the request (not history)
        payload = {
            "contents": self.history,
            "system_instruction": {"parts": [{"text": self.instruction}]},
            "tools": self._get_tool_definitions()
        }

        try:
            response = requests.post(self.url, headers={"Content-Type": "application/json"}, json=payload)
            response.raise_for_status()
            data = response.json()
            
            # Check for content
            if "candidates" not in data or not data["candidates"]:
                return "Error: No response from model."
            
            candidate = data["candidates"][0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])

            # Handle Function Calls
            if parts and "functionCall" in parts[0]:
                fc = parts[0]["functionCall"]
                fn_name = fc["name"]
                args = fc.get("args", {})
                
                print(f"[Agent] Calling tool: {fn_name}({args})")
                
                if fn_name in self.tools:
                    tool_result = self.tools[fn_name](**args)
                    
                    # Feed result back to model
                    tool_response_part = {
                        "functionResponse": {
                            "name": fn_name,
                            "response": {"name": fn_name, "content": tool_result}
                        }
                    }
                    
                    # Append model's function call and our response to history
                    self.history.append({"role": "model", "parts": [parts[0]]})
                    self.history.append({"role": "function", "parts": [tool_response_part]})
                    
                    # Recursively call model with tool output
                    follow_up_payload = {
                        "contents": self.history,
                        "system_instruction": {"parts": [{"text": self.instruction}]},
                        "tools": self._get_tool_definitions()
                    }
                    
                    resp2 = requests.post(self.url, headers={"Content-Type": "application/json"}, json=follow_up_payload)
                    resp2.raise_for_status()
                    data2 = resp2.json()
                    if "candidates" in data2 and data2["candidates"]:
                         final_text = data2["candidates"][0]["content"]["parts"][0].get("text", "")
                         self.history.append({"role": "model", "parts": [{"text": final_text}]})
                         return final_text
                else:
                    return f"Error: Tool {fn_name} not found."

            # Normal Text Response
            text = parts[0].get("text", "") if parts else ""
            self.history.append({"role": "model", "parts": [{"text": text}]})
            return text

        except Exception as e:
            return f"API Error: {e}\nResponse: {response.text if 'response' in locals() else 'None'}"
