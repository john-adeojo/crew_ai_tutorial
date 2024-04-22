import os
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
import yaml
import os
from backstory import backstory_planner, backstory_searcher, backstory_reporter, backstory_reviewer
from langchain_openai import ChatOpenAI

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

# loads API keys from config.yaml
load_config(file_path="./config.yaml")

# os.environ["OPENAI_MODEL_NAME"]="gpt-4-0125-preview"

# Define the tools
serper_tool = SerperDevTool()
website_search_tool = ScrapeWebsiteTool()

manager_llm = ChatOpenAI(temperature=0.7, model="gpt-4-0125-preview")
llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

# Define the agents
planning_agent = Agent(
    role='Planner',
    goal='Determine the sequence of question hops',
    backstory=backstory_planner,
    verbose=True,
    llm=llm,
    cache=True,
)

search_agent = Agent(
    role='Searcher',
    goal='Retrieve information for each hop',
    backstory=backstory_searcher,
    tools=[serper_tool, website_search_tool],
    verbose=True,
    llm=llm,
    cache=True,
)

reporting_agent = Agent(
    role='Reporter',
    goal='Synthesize responses into a comprehensive report with citations',
    backstory=backstory_reporter,
    verbose=True,
    llm=llm,
    cache=True,
)

review_agent = Agent(
    role='Reviewer',
    goal='Ensure the accuracy and completeness of the report',
    backstory=backstory_reviewer,
    verbose=True,
    llm=llm,
    cache=True,
)

# task = Task(description='Explain the steps involved in photosynthesis and its impact on the environment.')

task = Task(
    description='Explain the steps involved in photosynthesis and its impact on the environment.',
    expected_output='A detailed explanation including all major steps of photosynthesis and its environmental impact.'
)


crew = Crew(
    agents=[planning_agent, search_agent, reporting_agent, review_agent],
    process=Process.hierarchical,
    manager_llm=manager_llm,
    memory=True,
    tasks=[task]
)

try:
    result = crew.kickoff()
    print(result)
except Exception as e:
    print("failed to kickoff the crew: {e}")
