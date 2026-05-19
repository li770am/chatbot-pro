# 🤖 ChatBot Pro — Streamlit + LangChain

A professional chatbot built with **Streamlit**, **LangChain**, and **Google Gemini**.
Streaming responses, configurable model, structured prompts, robust error handling.

---

## ✨ Features

- **Sidebar configuration**
  - Temperature slider (0.0 – 1.0)
  - Model selector: `gemini-2.5-flash`, `gemini-2.5-pro`, `gemini-2.0-flash`
- **`PromptTemplate`** (personality + history + user message)
- **LCEL chain**: `chain = prompt_template | llm`
- **Token-by-token streaming** with a `|` cursor (ChatGPT-style)
- **New Conversation** button to clear history and refresh the app
- **Error handling**: missing API key, empty input, model/API errors, generic exceptions

---

## 🚀 Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Provide your Google API key
Get a key at https://aistudio.google.com/apikey

**Option A — environment variable (macOS / Linux):**
```bash
export GOOGLE_API_KEY="your_key_here"
```

**Option A — environment variable (Windows PowerShell):**
```powershell
$env:GOOGLE_API_KEY="your_key_here"
```

**Option B — Streamlit secrets** (create `.streamlit/secrets.toml`):
```toml
GOOGLE_API_KEY = "your_key_here"
```

### 3. Run the app
```bash
streamlit run 3_streamlit_chatbot.py
```

Open the URL shown in the terminal (usually http://localhost:8501).

---

## 🗂 Project structure
```
.
├── 3_streamlit_chatbot.py   # main Streamlit app
├── requirements.txt         # Python dependencies
├── README.md                # this file
└── REPORT.md                # short project report
```

---

## 🧠 How it works (in 30 seconds)

1. The user types a message in the chat input.
2. The previous messages stored in `st.session_state.messages` are formatted into a history string.
3. The `PromptTemplate` is filled with `{history}` and `{message}`, then piped to the LLM via LCEL (`prompt_template | llm`).
4. `chain.stream(...)` yields chunks; the UI appends each chunk and shows a `|` cursor until the response is complete.
5. The new turn is stored, and the next interaction reuses the updated history.
