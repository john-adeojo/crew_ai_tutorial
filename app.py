import os
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
import yaml
import os
from backstory import backstory_planner, backstory_searcher, backstory_reporter, backstory_integration
from langchain_openai import ChatOpenAI

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

# loads API keys from config.yaml
load_config(file_path="./config.yaml")


# Define the tools
serper_tool = SerperDevTool()
website_search_tool = ScrapeWebsiteTool()

manager_llm = ChatOpenAI(temperature=0.7, model="gpt-4-0125-preview")
llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

# Define the agents
planning_agent = Agent(
    role='Planner',
    goal='Deconstruct complex queries into simpler, interconnected sub-questions to guide a comprehensive and methodical investigative process',
    backstory=backstory_planner,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=False,
)

search_agent = Agent(
    role='Searcher',
    goal='Conduct targeted searches to gather specific information needed to construct the context for addressing complex multi-hop questions',
    backstory=backstory_searcher,
    tools=[serper_tool, website_search_tool],
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=False
)

integration_agent = Agent(
    role='Integration',
    goal="Synthesize gathered information into a coherent response that fully addresses the user's original multi-hop question.",
    backstory=backstory_integration,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=False
)

reporting_agent = Agent(
    role='Reporter',
    goal="Deliver a clear, accurate, and comprehensive response to the user, highlighting structured investigation outcomes and further exploration paths.",
    backstory=backstory_reporter,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=False
)


task = Task(
    description="When did the people who captured alakoff come to the region where Philipsburg is located? ",
    expected_output='A concise and accurate answer that must include direct citations.'
)


crew = Crew(
    agents=[planning_agent, search_agent, integration_agent, reporting_agent],
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
