from dotenv import load_dotenv
load_dotenv()
from crewai import Agent, LLM, Task

import litellm, os
litellm.set_verbose = True
os.environ['LITELLM_LOG'] = 'DEBUG'

from crewai_tools import FirecrawlSearchTool
from unstructured.partition.html import partition_html
from langchain.tools import tool
import json
import requests

llm = LLM(
    model="gpt-4o-mini",
    temperature=0.8,
)

class WebScrapingUtils:

    @tool("Scrape website content")
    def scrape_and_summarize_website(website):
        """Scrapes a website and returns a concise summary of its main content."""
        firecrawl_tool = FirecrawlSearchTool(
            api_key=os.environ['FIRECRAWL_API_KEY'],  
            query=website,  
            page_options={
                "onlyMainContent": True,  
                "includeHtml": False,     
                "fetchPageContent": True 
            }
        )

        scraped_content = firecrawl_tool.run()

        elements = partition_html(text=scraped_content)
        content = "\n\n".join([str(el) for el in elements])

        content_chunks = [content[i:i + 8000] for i in range(0, len(content), 8000)]

        summaries = []
        for chunk in content_chunks:
            analysis_agent = Agent(
                role='Content Analyst',
                goal='Analyze and summarize the provided content, extracting the most relevant details.',
                backstory="You're an experienced content analyst skilled in digesting and summarizing large amounts of web data.",
                llm=llm,
                allow_delegation=False
            )
            task = Task(
                agent=analysis_agent,
                description=f'Analyze and summarize the content below, returning only the summary.\n\nCONTENT\n----------\n{chunk}'
            )
            summary = task.execute()
            summaries.append(summary)

        return "\n\n".join(summaries)

class ArithmeticUtils:

    @tool("Make a calculation")
    def calculate(operation):
        """
        Evaluates a mathematical expression.
        Examples: `200*7` or `5000/2*10`
        """
        try:
            return eval(operation)
        except SyntaxError:
            return "Error: Invalid syntax in mathematical expression"

class SearchTools:

    @tool("Search the internet")
    def search_internet(query):
        """Searches the internet for the given query and returns relevant results."""
        top_result_to_return = 4
        url = "https://google.serper.dev/search"
        payload = json.dumps({"q": query})
        headers = {
            'X-API-KEY': os.environ['SERPER_API_KEY'],
            'content-type': 'application/json'
        }
        response = requests.request("POST", url, headers=headers, data=payload)
        if 'organic' not in response.json():
            return "Sorry, I couldn't find anything about that. There might be an issue with your SERPER API key."
        else:
            results = response.json()['organic']
            result_strings = []
            for result in results[:top_result_to_return]:
                try:
                    result_strings.append('\n'.join([
                        f"Title: {result['title']}", 
                        f"Link: {result['link']}",
                        f"Snippet: {result['snippet']}", 
                        "\n-----------------"
                    ]))
                except KeyError:
                    continue
            return '\n'.join(result_strings)

class TravelAdvisors:

    def destination_curator(self):
        return Agent(
            role='Destination Curator',
            goal='Select the best city based on weather, season, and cost considerations.',
            backstory='An expert in analyzing travel data to pick ideal destinations.',
            tools=[
                SearchTools.search_internet,
                WebScrapingUtils.scrape_and_summarize_website,
            ],
            llm=llm,
            verbose=True
        )

    def city_insider(self):
        return Agent(
            role='City Insider',
            goal='Provide the most accurate insights and local tips about the selected city.',
            backstory="""A seasoned local guide with extensive knowledge about the city's attractions and customs.""",
            tools=[
                SearchTools.search_internet,
                WebScrapingUtils.scrape_and_summarize_website,
            ],
            llm=llm,
            verbose=True
        )

    def travel_concierge_extraordinaire(self):
        return Agent(
            role='Travel Concierge Extraordinaire',
            goal="""Design exceptional travel itineraries complete with budget plans and packing suggestions.""",
            backstory="""A veteran travel planner with decades of experience in crafting personalized travel experiences.""",
            tools=[
                SearchTools.search_internet,
                WebScrapingUtils.scrape_and_summarize_website,
                ArithmeticUtils.calculate,
            ],
            llm=llm,
            verbose=True
        )












