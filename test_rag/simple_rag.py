# -*- coding: utf-8 -*-
# USAGE: python simple_rag.py
# ENVS:
#   uv pip install -qU langchain-openai langchain-chroma langchain-text-splitters
#   uv pip install -qU langchain-community langgraph langchain_ollama


from langchain import hub
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma


BASE_URL='http://192.168.16.225:11435'
EMBEDDING_MODEL_PATH = '../model/BAAI/bge-m3'


# Qwen3 model inference server
llm = ChatOpenAI(
    model_name='Qwen3-0.6B-FP8',
    openai_api_base='http://localhost:8000/v1',
    openai_api_key='token-kcgyrk'
)

# Ollama bge-m3 client
embeddings = OllamaEmbeddings(
    model="bge-m3",
    base_url=BASE_URL
)

vector_store = Chroma(
    collection_name="rag_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

# Load and chunk contents of the blog
loader = WebBaseLoader(
    web_paths=("https://luochang212.github.io/posts/docker_command/",)
)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# Index chunks
_ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
prompt = hub.pull("rlm/rag-prompt")


# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"])
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

response = graph.invoke({"question": "如何启动容器"})
print(response["answer"])
