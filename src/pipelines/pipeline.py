from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain 

def run_research_pipeline(topic: str) -> str:

    state= {}
    """
    A multi-agent research pipeline that:
    1. Uses the Search Agent to gather relevant information on the topic.
    2. Uses the Reader Agent to extract readable text from the gathered URLs.
    3. Uses the Writer Chain to compile a structured research report.
    4. Uses the Critic Chain to review and refine the report.
    """
    # Search Agent is working
    print("\n"+" ="*50)
    print("step 1 - Search Agent is Working....")
    print("="*50+"\n")

    search_agent = build_search_agent()
    search_results = search_agent.invoke({
        "message": [("user", f"find recent, relieable and detailed information about:{topic}")]
    })
    state["search_results"] = search_results['messages'][-1].content

    print("\n search results:", state["search_results"])


    #Step 2 - Reader Agent is working
    print("\n"+" ="*50)
    print("step 2 - Reader Agent is Working....")
    print("="*50+"\n")

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "message": [("user", 
                     f"Based on the following search results about '{topic}'",
                     f"pick the most relevant URL and scrape it for deeper content.\n\n"
                     f"Search Results:\n{state['search_results'][:800]}"
                     )]
    })
    state["reader_result"] = reader_result['messages'][-1].content


    print("\n reader result:", state["reader_result"])



    #Writer Chain
    print("\n"+" ="*50)
    print("step 3 - Writer Chain is Working....")
    print("="*50+"\n")
    research_combined = (
        f"Search Results:\n{state['search_results']}\n\n"
        f"Reader Result:\n{state['reader_result']}"
    )
    state["report"] = writer_chain.invoke({
        "topic": topic,
        "research": research_combined
    })


    print("\n Final Report\n", state["report"] )



#critic report

    print("\n"+" ="*50)
    print("step 4 - Critic Chain is Working....")
    print("="*50+"\n")

    state["feedback"] = critic_chain.invoke({

        "report": state["report"]
    })

    print("\n Feedback on the report:\n", state["feedback"] )
    return state


    