"""
Run:
streamlit run app.py

Backend:
python -m uvicorn backend:app --reload --port 8000
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv(".env")


API = os.getenv("BACKEND_URL", "http://localhost:8000")

EXPECTED_TOOLS = {
    "Weather server": [
        "get_weather",
        "get_current_date",
        "get_flights",
    ],
    "Airbnb server": [
        "airbnb_search",
        "airbnb_listing_details",
    ],
}


st.set_page_config(
    page_title="MCP Travel Desk",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)


st.markdown(
    """
    <style>
        .stApp {
            background: #f5f7fa;
        }

        [data-testid="stSidebar"] {
            background: #172b4d;
        }

        [data-testid="stSidebar"] * {
            color: #ffffff;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.4rem 0 1.2rem;
        }

        .brand {
            color: #172b4d;
            font-size: 1.25rem;
            font-weight: 800;
            letter-spacing: 0.02em;
        }

        .eyebrow {
            color: #68768a;
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }

        .hero {
            padding: 2.2rem 2.4rem;
            border-radius: 18px;
            color: white;
            background:
                linear-gradient(120deg, rgba(9, 73, 92, 0.96), rgba(28, 91, 132, 0.94)),
                #0b7285;
            box-shadow: 0 14px 32px rgba(23, 43, 77, 0.16);
            margin-bottom: 1.4rem;
        }

        .hero h1 {
            margin: 0;
            font-size: 2.35rem;
            line-height: 1.1;
        }

        .hero p {
            max-width: 650px;
            margin: 0.7rem 0 0;
            color: #d9f0f5;
            font-size: 1rem;
        }

        .metric {
            min-height: 105px;
            padding: 1rem 1.15rem;
            border: 1px solid #dce3eb;
            border-radius: 12px;
            background: #ffffff;
        }

        .metric-label {
            color: #68768a;
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
        }

        .metric-value {
            margin-top: 0.35rem;
            color: #172b4d;
            font-size: 1.7rem;
            font-weight: 800;
        }

        .tool-card {
            min-height: 125px;
            padding: 1rem;
            border: 1px solid #dce3eb;
            border-radius: 12px;
            background: white;
            box-shadow: 0 4px 12px rgba(23, 43, 77, 0.04);
        }

        .tool-name {
            color: #172b4d;
            font-weight: 750;
        }

        .tool-description {
            margin-top: 0.4rem;
            color: #68768a;
            font-size: 0.83rem;
            line-height: 1.4;
        }

        .status-pill {
            display: inline-block;
            margin-top: 0.65rem;
            padding: 0.25rem 0.6rem;
            border-radius: 999px;
            background: #e6fcf5;
            color: #087f5b;
            font-size: 0.75rem;
            font-weight: 700;
        }

        .empty-state {
            padding: 3.5rem 1rem;
            text-align: center;
            color: #68768a;
        }

        .empty-state h2 {
            color: #172b4d;
        }

        .stButton > button {
            border-radius: 9px;
            font-weight: 700;
        }

        [data-testid="stChatMessage"] {
            border-radius: 12px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(ttl=10)
def check_health():
    try:
        response = requests.get(f"{API}/health", timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False


@st.cache_data(ttl=15)
def load_tools():
    response = requests.get(f"{API}/tools", timeout=15)
    response.raise_for_status()
    return response.json()


def metric(label, value):
    st.markdown(
        f"""
        <div class="metric">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def tool_card(tool_name, description, available):
    status = "Connected" if available else "Unavailable"
    status_class = "status-pill" if available else "status-pill"
    color = "#e6fcf5" if available else "#fff4e6"
    text_color = "#087f5b" if available else "#d9480f"

    st.markdown(
        f"""
        <div class="tool-card">
            <div class="tool-name">{tool_name}</div>
            <div class="tool-description">{description}</div>
            <span class="{status_class}"
                  style="background:{color}; color:{text_color};">
                {status}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )


if "history" not in st.session_state:
    st.session_state.history = []


st.markdown(
    """
    <div class="topbar">
        <div>
            <div class="eyebrow">Operations workspace</div>
            <div class="brand">MCP Travel Desk</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
        <h1>Plan the next journey.</h1>
        <p>
            Search flights, check live weather, and discover Airbnb stays
            from one intelligent travel workspace.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


backend_connected = check_health()
available_tools = {}
tool_error_msg = None

if backend_connected:
    try:
        available_tools = load_tools()
    except requests.RequestException as e:
        tool_error_msg = str(e)
        if hasattr(e, "response") and e.response is not None:
            try:
                tool_error_msg = e.response.json().get("detail", str(e))
            except Exception:
                tool_error_msg = e.response.text or str(e)
        st.warning(f"Backend is online, but MCP tools could not be loaded: {tool_error_msg}")
else:
    st.warning(
        "The backend is offline. Start FastAPI to enable the travel tools."
    )


weather_tools = set(available_tools.get("weather", []))
airbnb_tools = set(available_tools.get("airbnb", []))
all_available_tools = weather_tools | airbnb_tools

metric_columns = st.columns(4)

with metric_columns[0]:
    metric("Backend", "Online" if backend_connected else "Offline")

with metric_columns[1]:
    metric("Tools online", len(all_available_tools))

with metric_columns[2]:
    metric("Conversations", len(st.session_state.history))

with metric_columns[3]:
    metric("Servers", len(available_tools))


with st.sidebar:
    st.markdown("## Travel Desk")
    st.caption("Connected MCP services")

    active_provider = os.getenv("LLM_PROVIDER", "ollama")
    active_model = (
        os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
        if active_provider == "ollama"
        else os.getenv("OPENAI_MODEL", "gpt-4o")
    )
    st.caption(f"🤖 LLM: `{active_model}` ({active_provider.title()})")

    if backend_connected:
        st.success("Backend connected")
    else:
        st.error("Backend unavailable")
        st.code("python -m uvicorn backend:app --reload --port 8000")

    st.divider()

    st.markdown("### Quick requests")

    quick_requests = [
        "Find flights from DEL to BOM on 16/09/2026",
        "What is the weather in Delhi?",
        "What is today's date?",
        "Find an Airbnb in Goa for 2 guests",
    ]

    for idx, req_text in enumerate(quick_requests):
        if st.button(req_text, key=f"quick_req_{idx}", use_container_width=True):
            st.session_state.pending_query = req_text
            st.rerun()

    st.divider()

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()


st.markdown("## Tool catalog")

tab_assistant, tab_tools, tab_status = st.tabs(
    ["Assistant", "Tool catalog", "System status"]
)


with tab_tools:
    st.caption("Tools discovered from the connected MCP servers.")

    tool_columns = st.columns(2)

    with tool_columns[0]:
        st.markdown("### Weather server")

        tool_card(
            "get_weather",
            "Returns current weather conditions for a city.",
            "get_weather" in weather_tools,
        )

        tool_card(
            "get_current_date",
            "Returns the current date and day of the week.",
            "get_current_date" in weather_tools,
        )

        tool_card(
            "get_flights",
            "Searches flight information between two locations.",
            "get_flights" in weather_tools,
        )

    with tool_columns[1]:
        st.markdown("### Airbnb server")

        tool_card(
            "airbnb_search",
            "Searches Airbnb accommodation by location and filters.",
            "airbnb_search" in airbnb_tools,
        )

        tool_card(
            "airbnb_listing_details",
            "Retrieves details for a selected Airbnb listing.",
            "airbnb_listing_details" in airbnb_tools,
        )


with tab_status:
    st.markdown("### Connection status")

    if backend_connected:
        st.success("FastAPI backend is responding.")
    else:
        st.error("FastAPI backend is not responding.")

    if available_tools:
        for server_name, tool_names in available_tools.items():
            st.markdown(f"**{server_name.title()} server**")
            st.write(", ".join(tool_names))
    else:
        st.info("No MCP tools are currently available.")


with tab_assistant:
    st.markdown("### Travel assistant")

    if not st.session_state.history:
        st.markdown(
            """
            <div class="empty-state">
                <h2>Where would you like to go?</h2>
                <p>
                    Ask a travel question below to start a conversation.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.history:
        with st.chat_message("user", avatar="🧑"):
            st.markdown(message["query"])

        with st.chat_message("assistant", avatar="✈️"):
            answer = message.get("answer", "")

            if answer:
                st.markdown(answer)
            else:
                st.warning("No readable answer was returned.")

            used_tools = message.get("tools_used", [])

            if used_tools:
                st.caption("Tools used: " + ", ".join(used_tools))

    query = st.chat_input(
        "Ask about flights, weather, or accommodation..."
    )

    # Use input query or query triggered from quick request button
    active_query = query or st.session_state.pop("pending_query", None)

    if active_query:
        with st.chat_message("user", avatar="🧑"):
            st.markdown(active_query)

        with st.chat_message("assistant", avatar="✈️"):
            with st.spinner("Searching connected travel tools..."):
                try:
                    response = requests.post(
                        f"{API}/chat",
                        json={"query": active_query},
                        timeout=180,
                    )
                    response.raise_for_status()

                    data = response.json()
                    answer = data.get("answer", "No answer was returned.")
                    tools_used = data.get("tools_used", [])

                    st.markdown(answer)
                    if tools_used:
                        st.caption("Tools used: " + ", ".join(tools_used))

                    st.session_state.history.append(
                        {
                            "query": active_query,
                            "answer": answer,
                            "tools_used": tools_used,
                        }
                    )

                except requests.RequestException as error:
                    err_msg = str(error)
                    if hasattr(error, "response") and error.response is not None:
                        try:
                            err_msg = error.response.json().get("detail", err_msg)
                        except Exception:
                            err_msg = error.response.text or err_msg
                    st.error(f"Request failed: {err_msg}")