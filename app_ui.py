import streamlit as st
from llm_agent import LlmAgent
from schema_loader import Database
import time
from viz_agent import VizChartAgent

st.set_page_config(
    page_title="Text → SQL",
    layout="wide",
    initial_sidebar_state="expanded",
)

@st.cache_resource
def get_agent():
    return LlmAgent(Database())

if "history" not in st.session_state:
    st.session_state.history = []
if "current" not in st.session_state:
    st.session_state.current = None

def main():
    st.title("Text-to-SQL")
    agent = get_agent()
    with st.spinner("Starting ollama..."):
        agent.start_ollama_if_not_running()
    st.subheader('Converter')
    prompt = st.text_input(
        "Ask a question about your data:",
        placeholder="e.g. What are the top 10 customers by total orders?",
        label_visibility="collapsed"
    )

    if prompt:
        with st.spinner("Generating SQL..."):
            start = time.perf_counter()
            result_set = agent.prompt_agent(prompt)
            elapsed = time.perf_counter() - start
            result_set["elapsed"] = elapsed
            st.session_state.current = result_set
            if "df" in result_set:
                st.subheader("Results")
                st.dataframe(result_set["df"])
                with st.spinner("Generating chart..."):
                    try:
                        fig = VizChartAgent(result_set["df"]).plot()
                        if fig:
                            st.subheader("Chart")
                            st.plotly_chart(fig, use_container_width=True)
                    except Exception as e:
                        print(e)
                        pass  # chart is best-effort, never blocks the result
                st.session_state.history.append({
                    "question": prompt,
                    "sql": result_set["sql"],
                })
            else:
                st.error("All attempts failed — see the **Failed Attempts** tab below for details.")

    if st.session_state.current:
        cur = st.session_state.current
        df = cur.get("df")
        st.markdown("---")
        if df is not None:
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Rows returned", f"{len(df):,}")
            m2.metric("Columns", len(df.columns))
            m3.metric("Execution Time", f"{cur['elapsed']:.3f}s")
        else:
            m1, m2 = st.columns(2)
            m1.metric("Execution Time", f"{cur['elapsed']:.3f}s")
            m2.metric("Status", "Failed")

        tabs = ["Failed Attempts"]
        if df is not None:
            tabs = ["SQL", "Explanation"] + tabs
        rendered_tabs = st.tabs(tabs)

        if df is not None:
            tab_sql, tab_explain, tab_failed_attempts = rendered_tabs
            with tab_sql:
                st.code(cur.get("sql", ""), language="sql")
            with tab_explain:
                st.markdown(cur.get("explanation", ""), unsafe_allow_html=True)
        else:
            tab_failed_attempts = rendered_tabs[0]

        with tab_failed_attempts:
            analysis_attempts = cur.get("analysis") or []
            if not analysis_attempts:
                st.success("No errors")
            else:
                st.warning(f"{len(analysis_attempts)} failed attempt(s)")
                for a in analysis_attempts:
                    with st.expander("Errors"):
                        if a:
                            st.markdown("**Error Agent Analysis**")
                            st.markdown(f"**Root cause:** {a.root_cause}")
                            st.markdown(f"**Explanation:** {a.explanation}")
                            st.markdown(f"**Suggested fix:** {a.suggested_fix}")

    with st.sidebar:
        st.markdown('<div class="header-title">Text → SQL</div>', unsafe_allow_html=True)
        st.markdown("---")

        with st.expander("Schema", expanded=False):
            for table in agent.db.get_all_tables():
                st.markdown(f"**{table}**")
                df_desc = agent.db.run_query(f"DESC {table}")[["column_name", "column_type"]]
                for _, row in df_desc.iterrows():
                    st.markdown(
                        f"`{row['column_name']}` "
                        f"{row['column_type']}",
                        unsafe_allow_html=True,
                    )

        st.markdown("---")
        st.subheader("Query History")
        if not st.session_state.history:
            st.caption("No queries yet.")
        else:
            for item in reversed(st.session_state.history):
                st.caption(item["question"])
                st.code(item["sql"], language="sql")

if __name__=="__main__":
    main()