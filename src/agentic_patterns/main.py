from reflection_pattern.reflection_agent import RefelctionAgent
from tool_pattern.tool_agent import ToolAgent
from reAct_pattern.react_agent import ReactAgent
from colorama import Fore
from tool_pattern.tool import tool

from multiagent_pattern.agent import Agent

from multiagent_pattern.crew import Crew


@tool
def add(a: int, b: int) -> int:
    """Adds two integers"""
    return a + b
@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two integers"""
    return a * b
@tool
def divide(a: float, b: float) -> float:
    """Divides two numbers"""
    if b == 0:
        return "Cannot divide by zero"
    return a / b
@tool
def reverse_text(text: str) -> str:
    """Reverses the given text"""
    return text[::-1]
@tool
def count_words(text: str) -> int:
    """Counts number of words in a sentence"""
    return len(text.split())
@tool
def to_upper(text: str) -> str:
    """Converts text to uppercase"""
    return text.upper()
@tool
def simple_interest(p: float, r: float, t: float) -> float:
    """Calculates simple interest"""
    return (p * r * t) / 100
@tool
def is_even(n: int) -> bool:
    """Checks if a number is even"""
    return n % 2 == 0
def Reflection_Agent():
    reflectionAgent=RefelctionAgent()
    user_prompt=input("Enter a question:")
    output=reflectionAgent.run(user_prompt)
    print( Fore.GREEN,output,)

def Tool_Agent():
    user_input=input("Enter a question:")
    tools = [
    add,
    multiply,
    divide,
    reverse_text,
    count_words,
    to_upper,
    simple_interest,
    is_even
]
    toolAgent=ToolAgent(tools)
    output=toolAgent.run(user_msg=user_input)
    print(Fore.GREEN,output)
def main():
    user_input=input("Enter a question:")
    tools = [
    add,
    multiply,
    divide,
    reverse_text,
    count_words,
    to_upper,
    simple_interest,
    is_even
]
    reactAgent=ReactAgent(tools)
    output=reactAgent.run(user_msg=user_input)
    print(Fore.GREEN,output)

# Create crew
with Crew() as crew:

    research_agent = Agent(
        name="ResearchAgent",
        backstory="You are good at gathering information.",
        task_description="Find key points about Artificial Intelligence.",
    )

    analysis_agent = Agent(
        name="AnalysisAgent",
        backstory="You are good at analyzing information.",
        task_description="Analyze the given information and extract insights.",
    )

    summary_agent = Agent(
        name="SummaryAgent",
        backstory="You are good at summarizing.",
        task_description="Summarize everything into simple points.",
    )

    # 🔥 Define flow
    research_agent >> analysis_agent >> summary_agent

# Run crew
crew.run()
# if __name__=='__main__':
#     main()
