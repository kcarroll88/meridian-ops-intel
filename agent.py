import os
from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import chromadb
import voyageai

load_dotenv()

from tavily import TavilyClient
tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def tavily_search(query: str) -> str:
    response = tavily_client.search(query, max_results=3)
    results = response.get("results", [])
    if not results:
        return "No results found."
    output = ""
    for r in results:
        output += f"Title: {r['title']}\n{r['content']}\n\n"
    return output

# ── CLIENTS ───────────────────────────────────────────────────────────────────
voyage_client = voyageai.Client()
chroma_client = chromadb.PersistentClient(path="chroma_db")
collection = chroma_client.get_or_create_collection(name="documents")
llm = ChatAnthropic(model="claude-haiku-4-5-20251001", max_tokens=1000)

# ── 1. LOAD + INDEX DOCS ──────────────────────────────────────────────────────
def index_documents(folder_path="docs"):
    if collection.count() > 0:
        print(f"Knowledge base already indexed with {collection.count()} chunks")
        return

    docs = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(folder_path, filename))
            pages = loader.load()
            docs.extend(pages)
            print(f"Loaded: {filename}")

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(docs)

    texts = [c.page_content for c in chunks]
    sources = [c.metadata.get("source", "unknown") for c in chunks]

    batch_size = 50
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i+batch_size]
        batch_sources = sources[i:i+batch_size]
        batch_ids = [f"chunk_{i+j}" for j in range(len(batch_texts))]

        response = voyage_client.embed(batch_texts, model="voyage-3")
        collection.add(
            documents=batch_texts,
            embeddings=response.embeddings,
            metadatas=[{"source": s} for s in batch_sources],
            ids=batch_ids
        )
    print(f"Indexed {len(chunks)} chunks")

# ── 2. TOOLS ──────────────────────────────────────────────────────────────────
def search_knowledge_base(query: str) -> str:
    """Search the internal knowledge base for information from uploaded documents."""
    query_embedding = voyage_client.embed([query], model="voyage-3").embeddings[0]
    results = collection.query(query_embeddings=[query_embedding], n_results=3)
    
    if not results["documents"][0]:
        return "No relevant information found in the knowledge base."
    
    chunks = results["documents"][0]
    sources = [os.path.basename(m["source"]) for m in results["metadatas"][0]]
    
    output = ""
    for chunk, source in zip(chunks, sources):
        output += f"[Source: {source}]\n{chunk}\n\n"
    
    return output

tools = [
    Tool(
        name="KnowledgeBase",
        func=search_knowledge_base,
        description="Search internal documents and knowledge base. Use this for questions about our products, documentation, policies, or anything that might be in uploaded files."
    ),
    Tool(
    name="WebSearch",
    func=tavily_search,
    description="""Search the web for current information, news, or anything not in internal documents.
    Use this for recent events, general knowledge, or external information.
    Always include the current year 2026 in search queries for recent news."""
    )
]

# ── 3. AGENT ──────────────────────────────────────────────────────────────────
_SYSTEM_INSTRUCTIONS = """You are a professional enterprise research assistant for Meridian Analytics.
You help employees answer questions about internal company knowledge, market intelligence,
industry trends, and business strategy. Today's date is April 2026. Always use 2026 when searching for current news.

Only assist with topics related to:
- Meridian Analytics internal knowledge, policies, and operations
- Business strategy, market research, and competitive intelligence
- Industry news and professional topics

Decline any requests that are unrelated to professional business research, or that ask for
inappropriate, harmful, or personal content. For off-topic requests, politely explain that
you are scoped to business and professional research only.

"""

_REACT_BASE = """Answer the following questions as best you can. You have access to the following tools:

{tools}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}"""

def build_agent():
    prompt = PromptTemplate(
        input_variables=["input", "agent_scratchpad", "tools", "tool_names"],
        template=_SYSTEM_INSTRUCTIONS + _REACT_BASE,
    )
    agent = create_react_agent(llm, tools, prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )

# ── MAIN ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    index_documents()
    agent_executor = build_agent()

    questions = [
        "What is Nexus and how do I reset a password?",
        "What is the latest news about AI agents?",
        "What does our documentation say about refunds, and what are people saying about SaaS refund policies online?"
    ]

    for question in questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        print('='*60)
        result = agent_executor.invoke({"input": question})
        print(f"\nFinal Answer: {result['output']}")