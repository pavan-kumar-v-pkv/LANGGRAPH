# cd /Users/pavankumarv/dev/ml/LangGraph/4-Chatbot && source ../venv/bin/activate && python -m streamlit run streamlit_frontend_streaming.py

import streamlit as st
from langgraph_backend import chatbot
from langchain_core.messages import HumanMessage
import uuid

##### utility functions #####
def generate_uuid():
    return str(uuid.uuid4())

def reset_chat():
    st.session_state['message_history'] = []
    st.session_state['thread_id'] = generate_uuid()
    add_thread(st.session_state['thread_id'])

def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    try:
        state = chatbot.get_state(config={'configurable': {'thread_id': thread_id}})
        return state.values.get('history', [])  # Return empty list if no history exists
    except Exception:
        return []  # Return empty list if thread doesn't exist yet

def set_conversation_title(thread_id, user_input):
    """ Set conversation title based on first message """
    if thread_id not in st.session_state['conversation_titles']:
        # Use first 30 characters of first message as title
        title = user_input[:30]
        if len(user_input) > 30:
            title += "..."
        st.session_state['conversation_titles'][thread_id] = title

##### Session State #####
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_uuid()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'conversation_titles' not in st.session_state:
    st.session_state['conversation_titles'] = {}

add_thread(st.session_state['thread_id'])

##### Sidebar UI #####
st.sidebar.title("LangGraph Chatbot")

if st.sidebar.button("New Chat"):
    reset_chat()
st.sidebar.header("My Conversations")

for thread in st.session_state['chat_threads'][::-1]:  # Show latest threads on top
    # get title from stored titles or fallback to new chat
    conversation_title = st.session_state['conversation_titles'].get(thread, "New Chat")

    if st.sidebar.button(conversation_title, key=f"thread_{thread}s"):
        messages = load_conversation(thread)
        st.session_state['thread_id'] = thread

        temp_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                temp_messages.append({"role": "user", "content": msg.content})
            else:
                temp_messages.append({"role": "assistant", "content": msg.content})
        st.session_state['message_history'] = temp_messages

##### Main UI #####

# loading the conversation history
for message in st.session_state["message_history"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input =st.chat_input("Type your message here...")

if user_input:
    # set conversation title
    if not st.session_state['message_history']:
        set_conversation_title(st.session_state['thread_id'], user_input)

    st.session_state["message_history"].append({"role": "user", "content": user_input})
    with st.chat_message('user'):
        st.text(user_input)


    CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in chatbot.stream({'history': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
               )
        )
        st.session_state["message_history"].append({"role": "assistant", "content": ai_message})