import os
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
import yaml
import os
from backstory import backstory_planner, backstory_searcher, backstory_reporter, backstory_integration
from langchain_openai import ChatOpenAI

query = """How many Germans live in the colonial
holding in Aruba’s continent that was governed by Prazeres’s country?"""

def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

# loads API keys from config.yaml
load_config(file_path="./config.yaml")
INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL")


# Define the tools
serper_tool = SerperDevTool()
website_search_tool = ScrapeWebsiteTool()

manager_llm = ChatOpenAI(temperature=0.7, model="gpt-4-0125-preview")
llm = ChatOpenAI(temperature=0.7, model="gpt-3.5-turbo")

# OPENAI_MODEL_NAME = os.getenv("OPENAI_MODEL_NAME")
# OPENAI_API_BASE = os.getenv("OPENAI_API_BASE")

# manager_llm = ChatOpenAI(temperature=0, model=OPENAI_MODEL_NAME, openai_api_base=OPENAI_API_BASE)
# llm =  ChatOpenAI(temperature=0, model=OPENAI_MODEL_NAME, openai_api_base=OPENAI_API_BASE)

# Define the agents
planning_agent = Agent(
    role='Planner',
    goal='Streamline complex inquiries into organized, manageable components.',
    backstory=backstory_planner,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=False,
)

search_agent = Agent(
    role='Searcher',
    goal='Identify and retrieve essential data for sophisticated inquiries.',
    backstory=backstory_searcher,
    tools=[serper_tool, website_search_tool],
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=False
)

integration_agent = Agent(
    role='Integration',
    goal="Craft a unified answer to multifaceted questions.",
    backstory=backstory_integration,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=False
)

reporting_agent = Agent(
    role='Reporter',
    goal="Communicate insights clearly, ensuring depth and accuracy for further exploration",
    backstory=backstory_reporter,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=False
)



planning_task = Task(
    description=f'''For the following query: {query}, Deconstruct complex queries into simpler, interconnected sub-questions to guide a comprehensive and methodical investigative process''',
    expected_output='A detailed view of the sub-questions and their relationships to the main question and how to proceed with the investigation to answer the main question',
    agent=planning_agent,

)

search_task = Task(
    description=f'''For the following query: {query}, Conduct targeted searches to gather specific information needed to construct the context for addressing complex multi-hop questions''',
    expected_output='Specific information and sources relevant to the sub-questions identified by the Planner Agent',
    agent=search_agent,
    tools=[serper_tool, website_search_tool],
    context=[planning_task]    
)

integration_task = Task(
    description=f'''For the following query: {query}, Synthesize gathered information into a coherent response that fully addresses the user's original multi-hop question.''',
    expected_output='A comprehensive, integrated response that addresses the user\'s original multi-hop question',
    agent=integration_agent,
    context=[search_task]
)

reporting_task = Task(
    description=f'''For the following query: {query}, Deliver a clear, accurate, and comprehensive response to the user, highlighting structured investigation outcomes and further exploration paths.''',
    expected_output='A clear, accurate, and comprehensive response to the user, highlighting structured investigation outcomes and further exploration paths',
    agent=reporting_agent,
    context=[integration_task, search_task, planning_task]
)


crew = Crew(
    agents=[planning_agent, search_agent, integration_agent, reporting_agent],
    process=Process.hierarchical,
    manager_llm=manager_llm,
    memory=True,
    tasks=[planning_task, search_task, integration_task, reporting_task]
)

try:
    result = crew.kickoff()
    print(result)
except Exception as e:
    print("failed to kickoff the crew: {e}")
