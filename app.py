import streamlit as st
import uuid
import boto3

def qry_kb(agent_client, session_id, qry):
    response = agent_client.invoke_agent(
        agentId="3I5GFPHSQW",                    # <-- Replace
        agentAliasId="JVTGJYYIJO",              # <-- Usually "DRAFT" or your published alias
        sessionId=session_id,
        inputText=qry
    )
    agent_response = ''
    for event in response["completion"]:
        if "chunk" in event:
            chunk = event["chunk"]["bytes"].decode()
            print(chunk, end="", flush=True)
            agent_response += chunk
    return agent_response

st.set_page_config(page_title="Simple Chatbot", page_icon="🤖")
st.title("🤖 Simple Chatbot UI")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_user_input" not in st.session_state:
    st.session_state.pending_user_input = None

# Display existing chat
for message in st.session_state.messages:
    role = message["role"]
    content = message["content"]
    st.markdown(f"**{'You' if role == 'user' else 'Bot'}:** {content}")

# Input form
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Type your message:", key="input_text")
    submitted = st.form_submit_button("Send")

# Handle new user message
if submitted and user_input:
    # Add user message immediately
    st.session_state.messages.append({"role": "user", "content": user_input})
    # Store pending input for bot to respond to
    st.session_state.pending_user_input = user_input
    # Rerun to display message first
    st.rerun()

# If we have a pending message, get bot response
if st.session_state.pending_user_input:
    session_id = str(uuid.uuid4())
    session = boto3.Session()
    agent_client = session.client("bedrock-agent-runtime", region_name='us-east-1')

    user_input = st.session_state.pending_user_input
    bot_response = qry_kb(agent_client, session_id, user_input)

    # Append bot response
    st.session_state.messages.append({"role": "bot", "content": bot_response})
    # Clear the pending input
    st.session_state.pending_user_input = None
    # Rerun to display new response
    st.rerun()
