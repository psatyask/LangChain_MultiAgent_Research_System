
import time
from datetime import datetime

import streamlit as st

from src.agents.agents import (
    build_search_agent,
    build_reader_agent,
    writer_chain,
    critic_chain,
)


# -------------------------------------------
# PAGE CONFIGURATION
# -------------------------------------------

st.set_page_config(
    page_title="Atlas | AI Research Studio",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# -------------------------------------------
# CUSTOM STYLING
# -------------------------------------------

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');

    .stApp {
        background:
            radial-gradient(
                ellipse at 78% -20%,
                rgba(48,86,172,.19),
                transparent 48%
            ),
            radial-gradient(
                ellipse at 5% 24%,
                rgba(23,113,123,.10),
                transparent 43%
            ),
            #0a0e17;
        color: #eef3ff;
    }

    html, body {
        font-family: 'DM Sans', sans-serif;
    }

    .block-container {
        max-width: 1260px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    [data-testid="stHeader"] {
        background: transparent;
    }

    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
    }

    .brand {
        font-family: 'Space Grotesk', sans-serif;
        font-size: .85rem;
        font-weight: 700;
        letter-spacing: .18em;
        color: #a5b4fc;
    }

    .brand span {
        color: #eff4ff;
        letter-spacing: normal;
        margin-left: .7rem;
    }

    .eyebrow {
        color: #8ea6c6;
        text-transform: uppercase;
        letter-spacing: .18em;
        font-size: .72rem;
        font-weight: 700;
        margin-top: 3rem;
    }

    .hero-title {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 700;
        font-size: clamp(2.35rem, 5vw, 4.5rem);
        line-height: 1.09;
        letter-spacing: -.06em;
        margin: .7rem 0 1rem;
        color: #f4f7ff;
    }

    .hero-title em {
        font-style: normal;
        background: linear-gradient(
            115deg,
            #85c9ff,
            #b3a4ff
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-copy {
        max-width: 710px;
        font-size: 1.04rem;
        line-height: 1.75;
        color: #a7b7cc;
        margin-bottom: 1.8rem;
    }

    .section-label {
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        font-size: .76rem;
        color: #91a6c7;
        letter-spacing: .13em;
        text-transform: uppercase;
        margin-bottom: .9rem;
    }

    .process-step {
        border: 1px solid #28334a;
        border-radius: 15px;
        padding: 1.15rem 1.1rem;
        background: #111827;
        min-height: 116px;
    }

    .process-step.done {
        border-color: #286a5b;
        background: #0e2728;
    }

    .process-step.running {
        border-color: #668be1;
        background: #14213b;
    }

    .step-top {
        color: #8198ba;
        font-size: .68rem;
        font-weight: 700;
        letter-spacing: .12em;
        margin-bottom: .65rem;
    }

    .step-name {
        color: #f0f5ff;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 1rem;
        font-weight: 600;
    }

    .step-desc {
        color: #94a4bc;
        font-size: .78rem;
        margin-top: .3rem;
    }

    .step-state {
        color: #8fa8c8;
        font-size: .72rem;
        float: right;
    }

    .process-step.done .step-state {
        color: #68d8ba;
    }

    .process-step.running .step-state {
        color: #a6bbff;
    }

    div[data-testid="stForm"] {
        border: 1px solid #2a3b57;
        border-radius: 20px;
        background: rgba(21,30,46,.72);
        padding: 1.3rem;
    }

    div[data-testid="stTextArea"] textarea {
        background: #0c1525;
        border: 1px solid #33415b;
        border-radius: 12px;
        color: #edf4ff;
        font-size: 1rem;
    }

    .stFormSubmitButton button[kind="primary"] {
        border: none;
        background: linear-gradient(
            110deg,
            #699af4,
            #8876e7
        );
        color: white;
        font-weight: 700;
        border-radius: 10px;
        min-height: 2.8rem;
    }

    .stButton button {
        border-radius: 10px;
    }

    div[data-testid="stExpander"] {
        background: #121a2a;
        border: 1px solid #26344d;
        border-radius: 12px;
    }

    .footnote {
        color: #6f819d;
        font-size: .75rem;
        text-align: center;
        margin-top: 3rem;
    }

    @media (max-width: 760px) {
        .block-container {
            padding: 1.15rem 1rem 3rem;
        }

        .eyebrow {
            margin-top: 1.7rem;
        }

        .hero-copy {
            font-size: .94rem;
        }
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------
# PIPELINE CONFIGURATION
# -------------------------------------------

STEPS = [
    (
        "search",
        "Discover",
        "Find credible sources",
        "🔎"
    ),
    (
        "reader",
        "Read",
        "Extract article insights",
        "📖"
    ),
    (
        "writer",
        "Synthesize",
        "Write the research report",
        "✍️"
    ),
    (
        "critic",
        "Review",
        "Evaluate report quality",
        "🛡️"
    ),
]

EXAMPLES = [
    "How are AI agents changing enterprise software?",
    "Recent progress in open-source language models",
    "Challenges of deploying RAG systems in production",
]


# -------------------------------------------
# SESSION STATE
# -------------------------------------------

defaults = {
    "topic_input": "",
    "topic": "",
    "results": {},
    "error": "",
    "active_step": None,
    "finished_seconds": None,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# -------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------

def normalize_content(content):
    """
    Convert agent responses into readable text.
    """

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        parts = []

        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(
                        str(item.get("text", ""))
                    )

            elif isinstance(item, str):
                parts.append(item)

        return "\n".join(parts)

    return str(content)


def agent_reply(agent, prompt):
    """
    Invoke a LangChain agent and return
    its final response.
    """

    response = agent.invoke({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })

    messages = response.get("messages", [])

    if not messages:
        raise RuntimeError(
            "The agent returned no messages."
        )

    answer = normalize_content(
        messages[-1].content
    ).strip()

    if not answer:
        raise RuntimeError(
            "The agent returned an empty response."
        )

    return answer


def name_for_key(key):
    """Get the display name of a pipeline stage."""

    names = {
        "search": "Search Agent",
        "reader": "Reader Agent",
        "writer": "Writer Chain",
        "critic": "Critic Chain",
    }

    return names.get(key, key)


# -------------------------------------------
# PIPELINE VISUALIZATION
# -------------------------------------------

def draw_steps(target):

    columns = target.columns(
        4,
        gap="small"
    )

    results = st.session_state.results
    active_step = st.session_state.active_step

    for index, step in enumerate(STEPS):

        key, name, description, emoji = step

        if key in results:
            status = "done"

        elif active_step == key:
            status = "running"

        else:
            status = "waiting"

        labels = {
            "done": "✓ COMPLETE",
            "running": "● ACTIVE",
            "waiting": "UP NEXT",
        }

        with columns[index]:

            st.markdown(
                f"""
                <div class="process-step {status}">
                    <div class="step-top">
                        STEP {index + 1:02d}
                        <span class="step-state">
                            {labels[status]}
                        </span>
                    </div>

                    <div class="step-name">
                        {emoji} {name}
                    </div>

                    <div class="step-desc">
                        {description}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# -------------------------------------------
# RESEARCH PIPELINE
# -------------------------------------------

def run_research(topic, pipeline_holder, progress_holder):

    st.session_state.results = {}
    st.session_state.error = ""
    st.session_state.topic = topic

    start_time = time.monotonic()

    jobs = [
        ("search", "Searching for trustworthy sources"),
        ("reader", "Reading relevant webpages"),
        ("writer", "Generating research report"),
        ("critic", "Evaluating report quality"),
    ]

    progress_bar = progress_holder.progress(
        0,
        text="Preparing research pipeline..."
    )

    with st.status(
        "Research pipeline running",
        expanded=True
    ) as status:

        for index, (key, description) in enumerate(jobs):

            st.session_state.active_step = key

            pipeline_holder.empty()
            draw_steps(pipeline_holder)

            progress_bar.progress(
                index / len(jobs),
                text=(
                    f"Step {index + 1} of 4 — "
                    f"{description}"
                )
            )

            st.write(
                f"{STEPS[index][3]} {description}..."
            )

            try:

                # ---------------------------------
                # STEP 1: SEARCH
                # ---------------------------------

                if key == "search":

                    search_agent = build_search_agent()

                    value = agent_reply(
                        search_agent,
                        (
                            f"Research this topic: {topic}. "
                            "Search the web and return key "
                            "findings with their source URLs. "
                            "Prefer credible sources."
                        )
                    )

                # ---------------------------------
                # STEP 2: READER
                # ---------------------------------

                elif key == "reader":

                    reader_agent = build_reader_agent()

                    value = agent_reply(
                        reader_agent,
                        (
                            f"Topic: {topic}\n\n"
                            "Search results:\n"
                            f"{st.session_state.results['search'][:5500]}\n\n"
                            "Select a relevant public URL "
                            "from these results. "
                            "Use scrape_url to read it and "
                            "summarize the evidence. "
                            "Preserve the source URL. "
                            "If no URL is accessible, "
                            "say so explicitly."
                        )
                    )

                # ---------------------------------
                # STEP 3: WRITER
                # ---------------------------------

                elif key == "writer":

                    research = (
                        "SEARCH RESULTS:\n"
                        f"{st.session_state.results['search']}\n\n"
                        "SCRAPED CONTENT:\n"
                        f"{st.session_state.results['reader']}"
                    )

                    value = writer_chain.invoke({
                        "topic": topic,
                        "research": research
                    })

                # ---------------------------------
                # STEP 4: CRITIC
                # ---------------------------------

                else:

                    value = critic_chain.invoke({
                        "report": st.session_state.results["writer"]
                    })

                st.session_state.results[key] = (
                    normalize_content(value)
                )

            except Exception as error:

                st.session_state.error = (
                    f"{name_for_key(key)} failed: {error}"
                )

                status.update(
                    label="Research stopped",
                    state="error",
                    expanded=True
                )

                st.session_state.active_step = None

                pipeline_holder.empty()
                draw_steps(pipeline_holder)

                progress_bar.empty()
                return

        status.update(
            label="All four research stages completed",
            state="complete",
            expanded=False
        )

    st.session_state.active_step = None

    st.session_state.finished_seconds = (
        time.monotonic() - start_time
    )

    progress_bar.progress(
        1.0,
        text="Research complete!"
    )

    pipeline_holder.empty()
    draw_steps(pipeline_holder)


# -------------------------------------------
# HERO HEADER
# -------------------------------------------

st.markdown(
    """
    <div class="brand">
        ✦ ATLAS
        <span>AI RESEARCH STUDIO</span>
    </div>

    <div class="eyebrow">
        An intelligent research workspace
    </div>

    <div class="hero-title">
        From a question to <em>clarity.</em>
    </div>

    <div class="hero-copy">
        Explore any topic with four specialized
        AI stages. Find credible sources, read
        relevant webpages, synthesize the
        evidence, and receive a critical review.
    </div>
    """,
    unsafe_allow_html=True,
)


# -------------------------------------------
# RESEARCH INPUT
# -------------------------------------------

left, right = st.columns(
    [1.5, 1],
    gap="large"
)

with left:

    st.markdown(
        '<div class="section-label">Start New Research</div>',
        unsafe_allow_html=True,
    )

    with st.form(
        "research_form",
        clear_on_submit=False
    ):

        topic_input = st.text_area(
            "What would you like to research?",
            key="topic_input",
            height=100,
            placeholder=(
                "e.g. How are multimodal AI agents "
                "being used in healthcare?"
            )
        )

        submitted = st.form_submit_button(
            "✦ Generate Research Report",
            use_container_width=True,
            type="primary"
        )

    st.caption(
        "Need an idea? Choose a sample topic:"
    )

    for index, sample in enumerate(EXAMPLES):

        if st.button(
            sample,
            key=f"example_{index}",
            use_container_width=True
        ):

            st.session_state.topic_input = sample
            st.rerun()


with right:

    st.markdown(
        '<div class="section-label">How It Works</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        **01 · Search** — Discover relevant sources

        **02 · Read** — Extract important information

        **03 · Write** — Generate a structured report

        **04 · Review** — Evaluate the report critically
        """
    )

    st.caption(
        "Powered by LangChain agents and your "
        "configured LLM. Verify important claims."
    )


# -------------------------------------------
# PIPELINE DISPLAY
# -------------------------------------------

st.divider()

st.markdown(
    '<div class="section-label">Research Pipeline</div>',
    unsafe_allow_html=True,
)

pipeline_holder = st.empty()

draw_steps(pipeline_holder)

progress_holder = st.empty()


# -------------------------------------------
# EXECUTE PIPELINE
# -------------------------------------------

if submitted:

    cleaned_topic = topic_input.strip()

    if not cleaned_topic:

        st.warning(
            "Please enter a research topic."
        )

    else:

        run_research(
            cleaned_topic,
            pipeline_holder,
            progress_holder
        )


# -------------------------------------------
# ERROR DISPLAY
# -------------------------------------------

if st.session_state.error:

    st.error(st.session_state.error)

    st.info(
        "Completed stages are preserved below. "
        "Check your tools, model or API keys "
        "and try again."
    )


# -------------------------------------------
# RESULTS DASHBOARD
# -------------------------------------------

results = st.session_state.results

if results:

    st.divider()

    st.markdown(
        '<div class="section-label">Research Results</div>',
        unsafe_allow_html=True,
    )

    st.subheader(
        st.session_state.topic
    )

    # ---------------------------------------
    # METRICS
    # ---------------------------------------

    metric_cols = st.columns(3)

    metric_cols[0].metric(
        "Stages Completed",
        f"{len(results)} / 4"
    )

    metric_cols[1].metric(
        "Report Length",
        f"{len(results.get('writer', '').split()):,} words"
    )

    elapsed = st.session_state.finished_seconds

    metric_cols[2].metric(
        "Elapsed Time",
        (
            f"{elapsed:.1f}s"
            if elapsed is not None
            else "—"
        )
    )

    # ---------------------------------------
    # RESULT TABS
    # ---------------------------------------

    report_tab, critic_tab, evidence_tab = st.tabs([
        "📄 Research Report",
        "🛡️ Critic Review",
        "🔎 Research Evidence",
    ])

    # ---------------------------------------
    # RESEARCH REPORT
    # ---------------------------------------

    with report_tab:

        if "writer" in results:

            st.markdown(
                results["writer"]
            )

            timestamp = datetime.now().strftime(
                "%Y%m%d_%H%M"
            )

            st.download_button(
                label="⬇ Download Markdown Report",
                data=results["writer"],
                file_name=(
                    f"atlas_research_{timestamp}.md"
                ),
                mime="text/markdown",
                use_container_width=True,
            )

        else:

            st.info(
                "The research report will appear "
                "after the writing stage."
            )

    # ---------------------------------------
    # CRITIC REVIEW
    # ---------------------------------------

    with critic_tab:

        if "critic" in results:

            st.markdown(
                results["critic"]
            )

            st.download_button(
                label="⬇ Download Critic Feedback",
                data=results["critic"],
                file_name="atlas_critic_review.md",
                mime="text/markdown",
                use_container_width=True,
            )

        else:

            st.info(
                "The critic review is not available yet."
            )

    # ---------------------------------------
    # RESEARCH EVIDENCE
    # ---------------------------------------

    with evidence_tab:

        evidence_sections = [
            ("search", "Web Search Results"),
            ("reader", "Extracted Webpage Insights"),
        ]

        for key, label in evidence_sections:

            if key in results:

                with st.expander(
                    label,
                    expanded=(key == "search")
                ):

                    st.text(
                        results[key]
                    )

                    st.download_button(
                        label=f"Download {label}",
                        data=results[key],
                        file_name=f"atlas_{key}.txt",
                        mime="text/plain",
                        key=f"download_{key}",
                    )


# -------------------------------------------
# FOOTER
# -------------------------------------------

st.markdown(
    """
    <div class="footnote">
        ATLAS RESEARCH STUDIO
        · LANGCHAIN + STREAMLIT
        · VERIFY SOURCES BEFORE RELYING ON RESULTS
    </div>
    """,
    unsafe_allow_html=True,
)
