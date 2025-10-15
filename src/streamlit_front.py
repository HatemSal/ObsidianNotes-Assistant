import streamlit as st
import requests

# ----------------- Configuration and Setup -----------------
# Ensure this matches the port you run your FastAPI app on
FASTAPI_URL = "http://127.0.0.1:8000/rag_query"

st.set_page_config(
    page_title="RAG Chain Demo (Streamlit + FastAPI)",
    layout="centered"
)

# ----------------- UI Elements and Functions -----------------
st.title("🧠 LangGraph RAG Q&A Demo")
st.markdown("Enter a question below. The Streamlit frontend will send it to the FastAPI backend, which simulates running your RAG/LangGraph chain.")

# Initialize session state for history and response
if 'history' not in st.session_state:
    st.session_state['history'] = []

def send_query(question: str):
    """Sends the question to the FastAPI backend and handles the response."""
    if not question.strip():
        st.error("Please enter a question.")
        return

    st.session_state.history.append({"role": "user", "text": question})
    
    with st.spinner("Processing query via FastAPI..."):
        try:
            # Prepare the request payload
            payload = {"question": question}
            
            # Make the POST request to the backend
            response = requests.post(FASTAPI_URL, json=payload, timeout=20)
            
            if response.status_code == 200:
                data = response.json()
                answer = data.get("answer", "No answer found.")
            else:
                answer = f"Error from backend (Status: {response.status_code}): {response.text}"
        
        except requests.exceptions.ConnectionError:
            answer = "Connection Error: Could not connect to the FastAPI backend. Ensure it is running at http://127.0.0.1:8000."
        except requests.exceptions.Timeout:
            answer = "Request Timeout: The backend took too long to respond."
        except Exception as e:
            answer = f"An unexpected error occurred: {e}"

    st.session_state.history.append({"role": "assistant", "text": answer})


# --- Main Application Layout ---

# Input box for the user query
user_input = st.text_input(
    "Your Question:", 
    key="user_question",
    placeholder="e.g., What is the sun?"
)

# Button to submit the query
if st.button("Ask RAG Chain", type="primary"):
    send_query(user_input)

st.markdown("---")

# Display the conversation history
st.subheader("Conversation History")

if not st.session_state.history:
    st.info("Start the conversation by asking a question!")
else:
    # Display history in reverse order (newest first)
    for message in reversed(st.session_state.history):
        if message["role"] == "user":
            st.chat_message("user").write(message["text"])
        else:
            st.chat_message("assistant").write(message["text"])