import os
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import Annotated
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.graph.message import add_messages
from IPython.display import Image

from src.backend.agents.deep_researcher import Article
from src.backend.utils import load_yaml_config
from src.backend.prompt_builder import build_prompt_from_config
from src.backend.paths import APP_CONFIG_FPATH, PROMPT_CONFIG_FPATH
from src.backend.logger import logger

load_dotenv()

class News(BaseModel):
    topic: str
    news_articles: list[Article]

class NewsletterState(BaseModel):
    news: list[News] = []
    newsletter: str # Markdown string
    messages: Annotated[list, add_messages]

class NewsletterWriter:
    def __init__(self, groq_api_key: str):
        # Load application configurations
        app_config = load_yaml_config(APP_CONFIG_FPATH)
        self.llm_model = app_config["llm"]

        # Load prompt configurations
        prompt_config = load_yaml_config(PROMPT_CONFIG_FPATH)
        self.newsletter_writer_prompt = prompt_config["newsletter_writer_agent_prompt"]

        self.llm = ChatGroq(api_key=groq_api_key, model_name=self.llm_model)

        logger.info("[NewsletterWriter] Agent initialized")
    
    # The LLM node - where your agent thinks and decides
    def generate_newsletter(self, state: NewsletterState) -> dict:
        """
        Generate a newsletter markdown.
        This function uses news articles related to trending topics in AI to generate a newsletter and updates the state with the results.

        Args:
            state (NewsletterState): The current state of the newsletter writer, which will be updated with the generated newsletter.

        Returns:
            dict: A dictionary containing the updated state with the generated newsletter.
        """

        # Use the LLM to find news articles using the response from rss news extraction tool
        logger.info("[NewsletterWriter] Calling LLM...")
        logger.info("[NewsletterWriter] Generating newsletter...")
        state.newsletter = self.llm.invoke(state.messages)

        return {"newsletter": state.newsletter}
    
    # Build graph
    def build_newsletter_writer_graph(self) -> CompiledStateGraph:
        logger.info("[NewsletterWriter] Building graph...")
        workflow = StateGraph(NewsletterState)

        # Register nodes
        workflow.add_node("generate_newsletter", self.generate_newsletter)
        
        # Set entry point
        workflow.set_entry_point("generate_newsletter")
        workflow.add_edge("generate_newsletter", END)

        return workflow.compile()


def main():
    # Initialize the topic finder with Groq API key
    groq_api_key = os.getenv("GROQ_API_KEY")
    newsletter_writer = NewsletterWriter(groq_api_key)
    graph = newsletter_writer.build_newsletter_writer_graph()

    # Visualize the graph
    graph_png = Image(graph.get_graph().draw_mermaid_png())
    # Save the graph to a file
    with open("resources/newsletter_writer_graph.png", "wb") as f:
        f.write(graph_png.data)

    received_news = {
        "Quantum computers and their advancements": [
            {
                "title": "Quantum computing revolutionizes AI",
                "link": "https://www.cnn.com/2023/03/21/tech/quantum-computing-revolutionizes-ai/index.html",
                "summary": "Quantum computing revolutionizes AI",
                "content": "Quantum computing revolutionizes AI"
            },
            {
                "title": "Quantum computing revolutionizes AI",
                "link": "https://www.cnn.com/2023/03/21/tech/quantum-computing-revolutionizes-ai/index.html",
                "summary": "Quantum computing revolutionizes AI",
                "content": "Quantum computing revolutionizes AI"
            }
        ],
        "Quantum Computing Just Got a Boost": [
            {
                "title": "Quantum computing revolutionizes AI",
                "link": "https://www.cnn.com/2023/03/21/tech/quantum-computing-revolutionizes-ai/index.html",
                "summary": "Quantum computing revolutionizes AI",
                "content": "Quantum computing revolutionizes AI"
            },
            {
                "title": "Quantum computing revolutionizes AI",
                "link": "https://www.cnn.com/2023/03/21/tech/quantum-computing-revolutionizes-ai/index.html",
                "summary": "Quantum computing revolutionizes AI",
                "content": "Quantum computing revolutionizes AI"
            }
        ]
    }       

    # Add news (topics and news articles) to the system prompt
    news = "\n\nNews:\n"
    for topic, articles in received_news.items():
        news += f"Topic: {topic} (Number of articles: {len(articles)})\n"
        for article in articles:
            news += f"Title: {article['title']}\n"
            news += f"Link: {article['link']}\n"
            news += f"Summary: {article['summary']}\n"
            news += f"Content: {article['content']}\n\n"

    system_prompt = build_prompt_from_config(config=newsletter_writer.newsletter_writer_prompt, input_data=news)

    initial_state = NewsletterState(messages=[SystemMessage(content=system_prompt)], newsletter="")

    final_state = graph.invoke(initial_state, config={"recursion_limit": 100})

    print(f"\n === Newsletter: ===")
    print(final_state["newsletter"])


if __name__ == "__main__":
    main()