
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
REACT_SYSTEM_PROMPT = """
You operate by running a loop with the following steps: Thought, Action, Observation.
You are provided with function signatures within <tools></tools> XML tags.
You may call one or more functions to assist with the user query. Don' make assumptions about what values to plug
into functions. Pay special attention to the properties 'types'. You should use those types as in a Python dict.

For each function call return a json object with function name and arguments within <tool_call></tool_call> XML tags as follows:

<tool_call>
{"name": <function-name>,"arguments": <args-dict>, "id": <monotonically-increasing-id>}
</tool_call>

Here are the available tools / actions:

<tools>
%s
</tools>

Example session:

<question>What's the current temperature in Madrid?</question>
<thought>I need to get the current weather in Madrid</thought>
<tool_call>{"name": "get_current_weather","arguments": {"location": "Madrid", "unit": "celsius"}, "id": 0}</tool_call>

You will be called again with this:

<observation>{0: {"temperature": 25, "unit": "celsius"}}</observation>

You then output:

<response>The current temperature in Madrid is 25 degrees Celsius</response>

Additional constraints:

- If the user asks you something unrelated to any of the tools above, answer freely enclosing your answer with <response></response> tags.
"""


class ReactAgent:
     def __init__(self,tools:Tool| List[Tool],BASE_PROMPT="",model="llama-3.3-70b-versatile" ):
       self.model=model 
       self.tools=tools if isinstance(tools,List) else [tools]
       self.tools_dict = {tool.name: tool for tool in self.tools}
       self.client=Groq()
       self.BASE_PROMPT=BASE_PROMPT
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
     def run(self,user_msg,iter=10):
        question=f'<question>{user_msg}</question>'
        user_prompt=build_prompt(prompt=question,role="user")
        tool_chat_history=[]
        system_prompt=self.BASE_PROMPT
        tool_chat_history.append(build_prompt(prompt=system_prompt+"\n"+REACT_SYSTEM_PROMPT % self.add_tool_signatures(),role="system"))
        tool_chat_history.append(user_prompt)
        for _ in range(iter):
           completions=self.client.chat.completions.create(messages=tool_chat_history,model=self.model).choices[0].message.content
           response=extract_tag_content(str(completions),"response")
           if response.found:
            return response.content[0]
           thoughts=extract_tag_content(str(completions),"thought")
        #    print(Fore.RED,thoughts.content[0])
           tool_calls=extract_tag_content(str(completions),"tool_call")
           tool_chat_history.append(build_prompt(prompt=str(completions),role="assistant"))
           print(Fore.MAGENTA + f"\nThought: {thoughts.content[0]}")
           if tool_calls.found:
              observations=self.process_tool_call(tool_calls.content)
              observation_prompt=f'<observation>{observations}</observation>'
              tool_chat_history.append(build_prompt(prompt=observation_prompt, role="user"))
        return str(self.client.chat.completions.create(messages=tool_chat_history,model=self.model).choices[0].message.content)


     