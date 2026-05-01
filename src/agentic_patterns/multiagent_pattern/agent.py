from textwrap import dedent

from tool_pattern.tool import  Tool
from reAct_pattern.react_agent import ReactAgent
from multiagent_pattern.crew import Crew 
from typing import List
class Agent:
    def __init__(self,name:str,backstory:str,task_description:str, tools:Tool| List[Tool]|None=None,task_expected_output: str = "", model= "llama-3.3-70b-versatile"):
        self.name=name
        self.backstory=backstory
        self.task_description=task_description
        self.task_expected_output=task_expected_output
        self.tools=tools
        self.model=model
        self.react_agent=ReactAgent(tools or [],BASE_PROMPT=backstory,model=model)
        self.context="" 
        self.dependencies=[]
        self.dependents=[]
        Crew.register_agent(self)
    def __repr__(self):
        return f"{self.name}"
    def __rshift__(self, other):
        """
        Defines the '>>' operator. This operator is used to indicate agent dependency.

        Args:
            other (Agent): The agent that depends on this agent.
        """
        self.add_dependent(other)
        return other  # Allow chaining

    def __lshift__(self, other):
        """
        Defines the '<<' operator to indicate agent dependency in reverse.

        Args:
            other (Agent): The agent that this agent depends on.

        Returns:
            Agent: The `other` agent to allow for chaining.
        """
        self.add_dependency(other)
        return other  # Allow chaining

    def __rrshift__(self, other):
        """
        Defines the '<<' operator.This operator is used to indicate agent dependency.

        Args:
            other (Agent): The agent that this agent depends on.
        """
        self.add_dependency(other)
        return self  # Allow chaining

    def __rlshift__(self, other):
        """
        Defines the '<<' operator when evaluated from right to left.
        This operator is used to indicate agent dependency in the normal order.

        Args:
            other (Agent): The agent that depends on this agent.

        Returns:
            Agent: The current agent (self) to allow for chaining.
        """
        self.add_dependent(other)
        return self  # Allow chaining
    def add_dependecy(self,other):
        if isinstance(other,Agent):
            self.dependencies.append(other)
            other.dependents.append(self)
        elif isinstance(other, list) and all(isinstance(item, Agent) for item in other):
            for item in other:
                self.dependencies.append(item)
                item.dependents.append(self)
        else:
            raise TypeError("The dependency must be an instance or list of Agent.")
    def add_dependent(self,other):
         if isinstance(other, Agent):
            other.dependencies.append(self)
            self.dependents.append(other)
         elif isinstance(other, list) and all(isinstance(item, Agent) for item in other):
            for item in other:
                item.dependencies.append(self)
                self.dependents.append(item)
         else:
            raise TypeError("The dependent must be an instance or list of Agent.")
    def receive_context(self,input_data):
         self.context += f"{self.name} received context: \n{input_data}"
         
    def create_prompt(self):
        prompt = dedent(
            f"""
        You are an AI agent. You are part of a team of agents working together to complete a task.
        I'm going to give you the task description enclosed in <task_description></task_description> tags. I'll also give
        you the available context from the other agents in <context></context> tags. If the context
        is not available, the <context></context> tags will be empty. You'll also receive the task
        expected output enclosed in <task_expected_output></task_expected_output> tags. With all this information
        you need to create the best possible response, always respecting the format as describe in
        <task_expected_output></task_expected_output> tags. If expected output is not available, just create
        a meaningful response to complete the task.

        <task_description>
        {self.task_description}
        </task_description>

        <task_expected_output>
        {self.task_expected_output}
        </task_expected_output>

        <context>
        {self.context}
        </context>

        Your response:
        """
        ).strip()
        return prompt

    def run(self):
        msg = self.create_prompt()
        output = self.react_agent.run(user_msg=msg)

        # Pass the output to all dependents
        for dependent in self.dependents:
            dependent.receive_context(output)
        return output

        
