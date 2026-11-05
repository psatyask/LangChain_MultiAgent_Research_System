
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from src.tools.tools import web_search, scrape_url
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# ----------------------------------------
# 1. Model Initialization
# ----------------------------------------

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)


# ----------------------------------------
# 2. Search Agent
# ----------------------------------------

def build_search_agent():
    """
    Create a search agent that uses Tavily
    to find relevant research information.
    """

    return create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=(
            "You are an expert research search agent. "
            "Use the web_search tool to find relevant, "
            "credible and up-to-date information. "
            "Summarize important findings and always "
            "include the original source URLs. "
            "Do not invent facts or citations."
        )
    )


# ----------------------------------------
# 3. Reader Agent
# ----------------------------------------

def build_reader_agent():
    """
    Create a reader agent that extracts
    information from webpages.
    """

    return create_agent(
        model=llm,
        tools=[scrape_url],
        system_prompt=(
            "You are an expert webpage research reader. "
            "Use the scrape_url tool to read provided URLs. "
            "Extract key facts and relevant information. "
            "Summarize the content accurately and preserve "
            "the source URLs. "
            "Do not fabricate information."
        )
    )


# ----------------------------------------
# 4. Writer Chain
# ----------------------------------------

writer_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert research writer. "
        "Write clear, structured, factual and "
        "insightful research reports. "
        "Use only the provided research evidence. "
        "Do not invent sources or unsupported claims."
    ),
    (
        "human",
        """
Write a detailed research report on the topic below.

Topic:
{topic}

Research Gathered:
{research}

Structure the report as:

1. Introduction
2. Key Findings
   - Minimum 3 well-explained points when supported
     by the research
3. Conclusion
4. Sources
   - Include only URLs present in the research

Be detailed, factual and professional.
Acknowledge gaps if the research is insufficient.
"""
    )
])

writer_chain = (
    writer_prompt
    | llm
    | StrOutputParser()
)


# ----------------------------------------
# 5. Critic Chain
# ----------------------------------------

critic_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a sharp and constructive research critic. "
        "Evaluate research reports for accuracy, clarity, "
        "depth, structure, and source quality. "
        "Be honest, specific and constructive. "
        "Do not claim to have verified sources unless "
        "their contents were actually provided."
    ),
    (
        "human",
        """
Review the research report below and evaluate it strictly.

Report:
{report}

Respond in this exact format:

Score: X/10

Strengths:
- ...
- ...

Areas to Improve:
- ...
- ...

One line verdict:
...
"""
    )
])

critic_chain = (
    critic_prompt
    | llm
    | StrOutputParser()
)
