# Project Report — ChatBot Pro

## 1. Objective
Transform the basic LangChain + Streamlit chatbot into a robust, professional app with
dynamic configuration, structured prompting, streaming, and error handling.

## 2. Architecture
```
User → Streamlit UI → PromptTemplate ({history} + {message}) → LLM (Gemini) → stream → UI
                              │
                              └─ LCEL chain:  prompt_template | llm
```
- **State**: `st.session_state.messages` holds `HumanMessage` / `AIMessage` objects.
- **History injection**: serialized as plain text and passed as `{history}` to the template
  (instead of letting Gemini read the raw message list), so the prompt always has full
  context regardless of model.
- **Recreation of the LLM each run**: Streamlit reruns the whole script on every interaction,
  so `ChatGoogleGenerativeAI(...)` is rebuilt — that's exactly what makes the sidebar
  controls (temperature, model) take effect live.

## 3. Implementation Highlights
| Requirement | Implementation |
|---|---|
| Sidebar (temperature + model) | `st.slider`, `st.selectbox` inside `with st.sidebar` |
| `PromptTemplate` | personality + `{history}` + `{message}` |
| LCEL chain | `chain = prompt_template \| llm` |
| Streaming with cursor | `for chunk in chain.stream(...)` + `placeholder.markdown(full + "\|")` |
| New conversation | clears `messages` then calls `st.rerun()` |
| Missing API key | `st.error` + `st.stop()` |
| Empty input | `st.warning` + `st.stop()` |
| API / model errors | `try/except Exception` around init and stream |

## 4. Answers to the Reflective Questions

**Why recreate the model when parameters change?**
Streamlit reruns the script top-to-bottom on each interaction. Recreating `ChatGoogleGenerativeAI`
ensures the new `temperature` / `model_name` from the sidebar are actually applied — an
already-instantiated client would keep its original settings.

**What does the `|` character at the end of the partial response represent?**
A typing cursor — a visual cue that the model is still streaming. It's removed once the
final answer is rendered, mimicking ChatGPT's UX.

**Advantages of `PromptTemplate` over plain strings**
- Reusable and parameterized (no manual string concatenation).
- Declares `input_variables` explicitly → fails fast if a variable is missing.
- Cleanly composable with LCEL (`prompt | llm | parser | ...`).
- Easier to A/B test, version, and externalize.

**Why does streaming improve UX?**
- Perceived latency drops drastically — the user sees the first tokens within ~300 ms
  instead of waiting for the full response.
- Provides constant feedback that the system is alive and progressing.
- Allows the user to read while the model writes.

**Other errors worth handling in production**
- Network / timeout errors (`httpx.ConnectError`, `TimeoutError`)
- Rate limits & quota exceeded (HTTP 429)
- Auth errors (invalid / revoked key — HTTP 401/403)
- Content-policy / safety blocks from Gemini
- Context-length exceeded (very long histories)
- Invalid model name (e.g. typos, deprecated models)
- Empty / malformed streamed chunks
