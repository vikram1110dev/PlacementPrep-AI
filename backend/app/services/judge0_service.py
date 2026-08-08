import httpx
import base64
import os
import time
from typing import Dict, Any, List
from pydantic import BaseModel

class Judge0Result(BaseModel):
    status_id: int
    status_description: str
    stdout: str = None
    stderr: str = None
    compile_output: str = None
    time: float = None
    memory: float = None

class Judge0Service:
    def __init__(self):
        # By default use public CE or local Docker instance
        self.base_url = os.getenv("JUDGE0_URL", "https://ce.judge0.com")
        self.api_key = os.getenv("JUDGE0_API_KEY", None)

    def _get_language_id(self, language: str) -> int:
        mapping = {
            "python": 71,      # Python 3
            "java": 62,        # Java (OpenJDK 13.0.1)
            "cpp": 54,         # C++ (GCC 9.2.0)
            "javascript": 93,  # Node.js 18.15.0
            "c": 50
        }
        return mapping.get(language.lower(), 71)

    async def run_single_test(self, code: str, language: str, input_data: str, expected_output: str) -> Judge0Result:
        lang_id = self._get_language_id(language)
        
        payload = {
            "source_code": base64.b64encode(code.encode()).decode(),
            "language_id": lang_id,
            "stdin": base64.b64encode(input_data.encode()).decode() if input_data else None,
            "expected_output": base64.b64encode(expected_output.encode()).decode() if expected_output else None
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        if self.api_key:
            headers["X-RapidAPI-Key"] = self.api_key
            headers["X-RapidAPI-Host"] = self.base_url.replace("https://", "").replace("http://", "")

        url = f"{self.base_url}/submissions?base64_encoded=true&wait=false"
        
        async with httpx.AsyncClient() as client:
            try:
                # 1. Create submission
                response = await client.post(url, json=payload, headers=headers)
                response.raise_for_status()
                token = response.json()["token"]
                
                # 2. Poll for result (wait=false means we need to poll)
                max_retries = 10
                for _ in range(max_retries):
                    await httpx.AsyncClient().sleep(1.0)
                    poll_url = f"{self.base_url}/submissions/{token}?base64_encoded=true"
                    res = await client.get(poll_url, headers=headers)
                    res.raise_for_status()
                    data = res.json()
                    
                    status_id = data.get("status", {}).get("id")
                    
                    # Status <= 2 means Processing/In Queue
                    if status_id > 2:
                        return self._parse_result(data)
                        
                # Timeout
                return Judge0Result(
                    status_id=13,
                    status_description="Internal Error (Timeout waiting for Judge0)",
                )
                
            except Exception as e:
                return Judge0Result(
                    status_id=13,
                    status_description=f"Internal Error: {str(e)}"
                )

    def _parse_result(self, data: dict) -> Judge0Result:
        def decode_b64(s: str) -> str:
            if not s:
                return ""
            return base64.b64decode(s).decode('utf-8', errors='ignore')

        return Judge0Result(
            status_id=data.get("status", {}).get("id", 13),
            status_description=data.get("status", {}).get("description", "Unknown"),
            stdout=decode_b64(data.get("stdout")),
            stderr=decode_b64(data.get("stderr")),
            compile_output=decode_b64(data.get("compile_output")),
            time=float(data.get("time") or 0.0),
            memory=float(data.get("memory") or 0.0)
        )
