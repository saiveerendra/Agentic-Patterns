from groq import Groq
from colorama import Fore
from reflection_pattern.utils import build_prompt
import os
import sys 
from dotenv import load_dotenv
sys.path.append(os.path.abspath("../../.."))
load_dotenv()






BASE_GENERATION_SYSTEM_PROMPT = """
You are an expert assistant.

Your task is to generate the best possible response for the user's request.

If a critique is provided, improve the previous response accordingly.

IMPORTANT:
- Be accurate
- Be clear
- Be complete
- Do not add unnecessary conversation
- Output only the final answer
"""
BASE_REFLECTION_SYSTEM_PROMPT = """
You are a strict reviewer.

Evaluate the response based on:
- correctness
- clarity
- completeness
- relevance to the user's request

If there are issues, provide specific actionable improvements.

If the response is perfect, return ONLY: <OK>
"""

class RefelctionAgent:
    def __init__(self,model="llama-3.3-70b-versatile"):
        self.client=Groq()
        self.model=model
    def __str__(self):
        return "Reflection Agent"
    def generator(self,generation_history):
        output=self.client.chat.completions.create(
                messages=generation_history,model=self.model
            ).choices[0].message.content
        
        return output
    def reviewer(self,reviewer_history):
        output=self.client.chat.completions.create(
                messages=reviewer_history,model=self.model
            ).choices[0].message.content
        
        return output
        
    def run(self,
            user_prompt:str,
            generation_prompt="",
            reviwer_prompt="",
            
            iter:int=3):
        generation_prompt+=BASE_GENERATION_SYSTEM_PROMPT
        reviwer_prompt+=BASE_REFLECTION_SYSTEM_PROMPT
        generation_history=[
            build_prompt(prompt=generation_prompt,role="system"),
            build_prompt(prompt=user_prompt,role="user")
        ]
        reviewer_history=[
            build_prompt(prompt=reviwer_prompt,role="system")
        ]
        for i in range(iter):
            generator_output=self.generator(generation_history)
            generation_history.append(build_prompt(prompt=generator_output,role="assistant"))

            reviewer_history.append(build_prompt(prompt=generator_output,role="user"))
            reviewer_output=self.reviewer(reviewer_history)
            if "<OK>" in reviewer_output:
                print( Fore.RED,
                    "\n\nStop Sequence found. Stopping the reflection loop ... \n\n",)
                break

            reviewer_history.append(build_prompt(prompt=reviewer_output,role="assistant"))
            generation_history.append(build_prompt(prompt=reviewer_output,role="user"))
        return generator_output
            





        
        
