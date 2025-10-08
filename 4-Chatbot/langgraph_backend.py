from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver

CONFIG = {'configurable': {'thread_id': 'thread_1'}}

load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

class ChatState(TypedDict):
    history: Annotated[list[BaseMessage], add_messages]

def chat_node(state: ChatState):
    # take user query from state
    messages = state['history']
    # send to llm
    response = llm.invoke(messages)
    # response store state
    return {'history': [response]}

checkpointer = MemorySaver()
graph = StateGraph(ChatState)

# add nodes
graph.add_node('chat_node', chat_node)

# add edges
graph.add_edge(START, 'chat_node')
graph.add_edge('chat_node', END)

# run graph
chatbot = graph.compile(checkpointer=checkpointer)

# for message_chunk, metadata in chatbot.stream({'history': [HumanMessage(content='What is the recipe to make pasta')]},
#                 config=CONFIG,
#                 stream_mode='messages'
#                ):
#     if message_chunk:
#         print(message_chunk[-1].content, end='', flush=True)
