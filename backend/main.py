from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import openai
import os
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load API Key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Request Models
class CodeRequest(BaseModel):
    prompt: str
    language: str

class ModifyRequest(BaseModel):
    code: str
    modification: str

@app.post("/generate_code/")
def generate_code(request: CodeRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Write a valid, executable {request.language} program for the following prompt:\n"
                               f"'{request.prompt}'.\n"
                               f"Ensure the output is pure {request.language} code only—no explanations, comments, markdown, or extra text."
                }
            ]
        )

        # Extract code from OpenAI response
        code_output = response["choices"][0]["message"]["content"].strip()

        # Remove Markdown-style code block syntax
        code_output = code_output.replace(f"```{request.language.lower()}", "").replace("```", "").strip()

        return {"language": request.language, "code": code_output}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/modify_code/")
def modify_code(request: ModifyRequest):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"Modify the following {request.code} to {request.modification}. "
                               f"Only return the modified {request.code} as pure code—no explanations, comments, markdown, or extra text."
                }
            ]
        )

        modified_code = response["choices"][0]["message"]["content"].strip()

        # Ensure the response does NOT contain markdown formatting
        if modified_code.startswith("```"):
            modified_code = modified_code.split("\n", 1)[-1]  # Remove first line (```python)
        if modified_code.endswith("```"):
            modified_code = modified_code.rsplit("\n", 1)[0]  # Remove last line (```)

        return {"modified_code": modified_code.strip()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def home():
    return {"message": "Conversational Code Generation API is running!"}
