from dotenv import load_dotenv
load_dotenv()
from crewai import Agent, LLM, Task
from langchain_groq import ChatGroq

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

















# from dotenv import load_dotenv
# load_dotenv()
# from crewai import Agent,LLM
# from langchain_groq import ChatGroq


# import litellm, os
# litellm.set_verbose = True
# os.environ['LITELLM_LOG'] = 'DEBUG'


# from crewai_tools import FirecrawlSearchTool
# from unstructured.partition.html import partition_html
# import os
# from crewai import Agent, Task,LLM
# from langchain.tools import tool
# from langchain_groq import ChatGroq
# llm = LLM(
#                 model="gpt-4o-mini",
#                 temperature=0.8,
 
#         )
# class BrowserTools():

#     @tool("Scrape website content")
#     def scrape_and_summarize_website(website):
#         """Useful to scrape and summarize a website content"""
#         # Initialize FirecrawlSearchTool
#         firecrawl_tool = FirecrawlSearchTool(
#             api_key=os.environ['FIRECRAWL_API_KEY'],  # Ensure you have this environment variable set
#             query=website,  # The website URL to scrape
#             page_options={
#                 "onlyMainContent": True,  # Only return the main content of the page
#                 "includeHtml": False,     # Exclude raw HTML
#                 "fetchPageContent": True  # Fetch the full content of the page
#             }
#         )

#         # Use the Firecrawl tool to scrape the website
#         scraped_content = firecrawl_tool.run()

#         # Partition the HTML content (if needed)
#         elements = partition_html(text=scraped_content)
#         content = "\n\n".join([str(el) for el in elements])

#         # Split content into chunks (if necessary)
#         content_chunks = [content[i:i + 8000] for i in range(0, len(content), 8000)]

#         # Summarize each chunk
#         summaries = []
#         for chunk in content_chunks:
#             agent = Agent(
#                 role='Principal Researcher',
#                 goal='Do amazing researches and summaries based on the content you are working with',
#                 backstory="You're a Principal Researcher at a big company and you need to do a research about a given topic.",
#                 llm=llm,
#                 allow_delegation=False
#             )
#             task = Task(
#                 agent=agent,
#                 description=f'Analyze and summarize the content below, make sure to include the most relevant information in the summary, return only the summary nothing else.\n\nCONTENT\n----------\n{chunk}'
#             )
#             summary = task.execute()
#             summaries.append(summary)

#         # Combine all summaries
#         return "\n\n".join(summaries)

# from langchain.tools import tool

# class CalculatorTools():

#     @tool("Make a calculation")
#     def calculate(operation):
#         """Useful to perform any mathematical calculations, 
#         like sum, minus, multiplication, division, etc.
#         The input to this tool should be a mathematical 
#         expression, a couple examples are `200*7` or `5000/2*10`
#         """
#         try:
#             return eval(operation)
#         except SyntaxError:
#             return "Error: Invalid syntax in mathematical expression"
# import json
# import os

# import requests
# from langchain.tools import tool


# class SearchTools():

#   @tool("Search the internet")
#   def search_internet(query):
#     """Useful to search the internet
#     about a a given topic and return relevant results"""
#     top_result_to_return = 4
#     url = "https://google.serper.dev/search"
#     payload = json.dumps({"q": query})
#     headers = {
#         'X-API-KEY': os.environ['SERPER_API_KEY'],
#         'content-type': 'application/json'
#     }
#     response = requests.request("POST", url, headers=headers, data=payload)
#     # check if there is an organic key
#     if 'organic' not in response.json():
#       return "Sorry, I couldn't find anything about that, there could be an error with you serper api key."
#     else:
#       results = response.json()['organic']
#       string = []
#       for result in results[:top_result_to_return]:
#         try:
#           string.append('\n'.join([
#               f"Title: {result['title']}", f"Link: {result['link']}",
#               f"Snippet: {result['snippet']}", "\n-----------------"
#           ]))
#         except KeyError:
#           next

#       return '\n'.join(string)




# class TripAgents():

#   def city_selection_agent(self):
#     return Agent(
#         role='City Selection Expert',
#         goal='Select the best city based on weather, season, and prices',
#         backstory=
#         'An expert in analyzing travel data to pick ideal destinations',
#         tools=[
#             SearchTools.search_internet,
#             BrowserTools.scrape_and_summarize_website,
#         ],
#         llm=llm,
#         verbose=True)

#   def local_expert(self):
#     return Agent(
#         role='Local Expert at this city',
#         goal='Provide the BEST insights about the selected city',
#         backstory="""A knowledgeable local guide with extensive information
#         about the city, it's attractions and customs""",
#         tools=[
#             SearchTools.search_internet,
#             BrowserTools.scrape_and_summarize_website,
#         ],
#         llm=llm,
#         verbose=True)

#   def travel_concierge(self):
#     return Agent(
#         role='Amazing Travel Concierge',
#         goal="""Create the most amazing travel itineraries with budget and 
#         packing suggestions for the city""",
#         backstory="""Specialist in travel planning and logistics with 
#         decades of experience""",
#         tools=[
#             SearchTools.search_internet,
#             BrowserTools.scrape_and_summarize_website,
#             CalculatorTools.calculate,
#         ],
#         llm=llm,
#         verbose=True)
