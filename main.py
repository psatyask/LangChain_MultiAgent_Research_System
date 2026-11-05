from src.tools.tools import web_search, scrape_url

from src.pipelines.pipeline import run_research_pipeline

r = run_research_pipeline("What is the latest research on AI in healthcare?")

print(r)
