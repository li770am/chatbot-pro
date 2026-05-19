# 3_streamlit_chatbot.py
# ChatBot Pro — Streamlit + LangChain (Google Gemini)
# Features: sidebar config, PromptTemplate, LCEL chain, streaming, error handling.

import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import PromptTemplate


# ---------- Page setup ----------
st.set_page_config(page_title="ChatBot Pro", page_icon="🤖")
st.title("🤖 ChatBot Pro")
st.markdown("LangChain + Streamlit chatbot with streaming responses.")


# ---------- Session state (keeps history across Streamlit reruns) ----------
if "messages" not in st.session_state:
    st.session_state.messages = []  # list of HumanMessage / AIMessage


# ---------- Helper: read API key from env or st.secrets ----------
def get_api_key() -> str | None:
    key = os.getenv("GOOGLE_API_KEY")
    if key:
        return key
    try:
        return st.secrets["GOOGLE_API_KEY"]  # .streamlit/secrets.toml
    except Exception:
        return None


# ---------- Sidebar (dynamic configuration) ----------
with st.sidebar:
    st.header("⚙️ Configuration")
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    model_name = st.selectbox(
        "Model",
        ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash"],
        index=0,
    )
    st.caption("Lower temperature = more deterministic. Higher = more creative.")

    # Reset conversation: clear history + refresh the app
    if st.button("🧹 New conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# ---------- API key check ----------
api_key = get_api_key()
if not api_key:
    st.error("❌ Missing GOOGLE_API_KEY.")
    st.info(
        "Set it as an environment variable\n"
        "`export GOOGLE_API_KEY=\"your_key\"`\n"
        "or in `.streamlit/secrets.toml`.\n"
        "Get a key at https://aistudio.google.com/apikey"
    )
    st.stop()


# ---------- Build the LLM (recreated on every run so sidebar changes apply) ----------
try:
    llm = ChatGoogleGenerativeAI(
        model=model_name,
        temperature=temperature,
        google_api_key=api_key,
    )
except Exception as e:
    st.error(f"❌ Could not initialize model '{model_name}': {e}")
    st.stop()


# ---------- PromptTemplate: personality + history + user message ----------
prompt_template = PromptTemplate(
    input_variables=["message", "history"],
    template=(
        "You are ChatBot Pro, a helpful, friendly, and concise assistant.\n"
        "Always reply in the same language as the user.\n"
        "Use the conversation history below to stay coherent and avoid repeating yourself.\n\n"
        "Conversation history:\n{history}\n\n"
        "User: {message}\n"
        "ChatBot Pro:"
    ),
)


# ---------- LCEL chain: prompt -> llm ----------
chain = prompt_template | llm


def format_history(messages: list) -> str:
    """Turn the stored messages into a readable history block for the prompt."""
    if not messages:
        return "(no previous messages)"
    lines = []
    for m in messages:
        role = "User" if isinstance(m, HumanMessage) else "ChatBot Pro"
        lines.append(f"{role}: {m.content}")
    return "\n".join(lines)


# ---------- Render previous turns ----------
for msg in st.session_state.messages:
    role = "assistant" if isinstance(msg, AIMessage) else "user"
    with st.chat_message(role):
        st.markdown(msg.content)


# ---------- Chat input + streaming response ----------
question = st.chat_input("Type your message…")

if question is not None:
    # Reject empty / whitespace-only messages
    if not question.strip():
        st.warning("⚠️ Please type a non-empty message.")
        st.stop()

    # Show the user message immediately
    with st.chat_message("user"):
        st.markdown(question)

    try:
        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_answer = ""

            # Streaming: append chunks and show a "|" cursor while typing
            for chunk in chain.stream({
                "message": question,
                "history": format_history(st.session_state.messages),
            }):
                full_answer += chunk.content or ""
                placeholder.markdown(full_answer + "|")

            # Final render without the cursor
            placeholder.markdown(full_answer if full_answer else "_(empty response)_")

        # Persist the turn only after a successful generation
        st.session_state.messages.append(HumanMessage(content=question))
        st.session_state.messages.append(AIMessage(content=full_answer))

    except Exception as e:
        # Catches API errors, quota issues, network problems, invalid model, etc.
        st.error(f"❌ Error generating response: {e}")
        st.info("Check your GOOGLE_API_KEY, internet connection, and the selected model.")
