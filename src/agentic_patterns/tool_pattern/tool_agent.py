
from typing import List
from colorama import Fore
from tool_pattern.tool import (Tool,validate_arguments)

from tool_pattern.utils import build_prompt
from tool_pattern.extraction import extract_tag_content
from dotenv import load_dotenv
import json
from groq import Groq

import sys
import os 
sys.path.append(os.path.abspath("../../../"))
load_dotenv()
TOOL_SYSTEM_PROMPT = """
You are a function calling AI model. You are provided with function signatures within <tools></tools> XML tags.
You may call one or more functions to assist with the user query. Don't make assumptions about what values to plug
into functions. Pay special attention to the properties 'types'. You should use those types as in a Python dict.
For each function call return a json object with function name and arguments within <tool_call></tool_call>
XML tags as follows:

<tool_call>
{"name": <function-name>,"arguments": <args-dict>,  "id": <monotonically-increasing-id>}
</tool_call>

Here are the available tools:

<tools>
%s
</tools>
"""
class ToolAgent:
    def __init__(self,tools:Tool| List[Tool],model="llama-3.3-70b-versatile" ):
       self.model=model 
       self.tools=tools if isinstance(tools,List) else [tools]
       self.tools_dict = {tool.name: tool for tool in self.tools}
       self.client=Groq()
    def add_tool_signatures(self) -> str:
        """
        Collects the function signatures of all available tools.

        Returns:
            str: A concatenated string of all tool function signatures in JSON format.
        """
        return "".join([tool.fn_signature for tool in self.tools])
    def process_tool_call(self,tool_call:List[str]):
        observations={}
        for tool_call_str in tool_call:
            clean_str=tool_call_str.replace("\\n", "")
            # print(clean_str)
            tool_call = json.loads(clean_str)
            tool_name = tool_call["name"]
            tool = self.tools_dict[tool_name]
            print(Fore.GREEN,f"\nUsing Toll:{tool_name}")
            valid_args=validate_arguments(tool_call,json.loads(tool.fn_signature))
            print(Fore.GREEN + f"\nTool call dict: \n{valid_args}")

            result = tool.run(**valid_args["arguments"])
            print(Fore.GREEN + f"\nTool result: \n{result}")
            observations[valid_args["id"]]=result 
        return observations



    def run(self,user_msg):
        user_prompt=build_prompt(prompt=user_msg,role="user")
        tool_chat_history=[]
        tool_chat_history.append(build_prompt(prompt=TOOL_SYSTEM_PROMPT % self.add_tool_signatures(),role="system"))
        tool_chat_history.append(user_prompt)
        agent_chat_history=[]
        agent_chat_history.append(user_prompt)
        tool_call_response=self.client.chat.completions.create(
            messages=tool_chat_history,model=self.model
        )
        tool_calls=extract_tag_content(str(tool_call_response),"tool_call")

        print(tool_calls)
        
        if tool_calls.found:
            observations=self.process_tool_call(tool_calls.content)
            agent_chat_history.append(build_prompt(prompt=f'Observation:{observations}',role="user"))
        return self.client.chat.completions.create(messages=agent_chat_history,model=self.model).choices[0].message.content 

