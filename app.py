import os
from crewai import Agent, Crew, Process, Task
from crewai_tools import SerperDevTool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
import argparse
import yaml
import os
from tasks import task_planner, task_searcher, task_reporter, task_integration
from backstory import backstory_planner, backstory_searcher, backstory_integration, backstory_reporter
from langchain_openai import ChatOpenAI


def load_config(file_path):
    with open(file_path, 'r') as file:
        config = yaml.safe_load(file)
        for key, value in config.items():
            os.environ[key] = value

# loads API keys from config.yaml
load_config(file_path="./config.yaml")
# INFERENCE_SERVER_URL = os.getenv("INFERENCE_SERVER_URL")


# Define the tools
serper_tool = SerperDevTool()
website_search_tool = ScrapeWebsiteTool()

manager_llm = ChatOpenAI(temperature=0, model="gpt-4-turbo")
llm = ChatOpenAI(temperature=0, model="gpt-4-turbo")


# Define the agents
planning_agent = Agent(
    role='Planner',
    goal='Streamline complex inquiries into organized, manageable components.',
    backstory=backstory_planner,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=True,
)

search_agent = Agent(
    role='Searcher',
    goal='Identify and retrieve essential data for sophisticated inquiries.',
    backstory=backstory_searcher,
    tools=[serper_tool, website_search_tool],
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=True
)

integration_agent = Agent(
    role='Integration',
    goal="Organise and sythesize information from multiple sources",
    backstory=backstory_integration,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=True
)

reporting_agent = Agent(
    role='Reporter',
    goal="Communicate insights clearly, ensuring depth and accuracy for further exploration",
    backstory=backstory_reporter,
    verbose=True,
    llm=llm,
    cache=True,
    allow_delegation=True
)


def main(query):

    planning_task = Task(
        description=task_planner.format(query=query),
        expected_output='A detailed view of the sub-questions and their relationships to the main question and how to proceed with the investigation to answer the main question',
        agent=planning_agent,
        
    )

    search_task = Task(
        description=task_searcher.format(query=query),
        expected_output='Specific information and sources relevant to the sub-questions identified by the Planner Agent',
        agent=search_agent,
        tools=[serper_tool, website_search_tool],
        context=[planning_task]    
    )

    integration_task = Task(
        description=task_integration.format(query=query),
        expected_output='All the information gathered from the searcher agent organised and integrated with website links and references.',
        agent=integration_agent,
        context=[search_task, planning_task]
    )

    reporting_task = Task(
        description=task_reporter.format(query=query),
        expected_output='A clear, accurate, and concise response to the user, with references and website links to sources of information.',
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run a query through CrewAI agents.')
    parser.add_argument('query', type=str, help='The query to be answered')

    args = parser.parse_args()
    main(args.query)