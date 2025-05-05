import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq
from langchain_chroma import Chroma
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_cohere.chat_models import ChatCohere
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# Initialize LLMs
chatmodel = ChatGroq(model="llama-3.1-8b-instant", temperature=0.15)
llm = ChatCohere(temperature=0.15)

# Setup embedding and vector database
embedF = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vectorDB = Chroma(embedding_function=embedF, persist_directory="data-ingestion-local")
kb_retriever = vectorDB.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Rephrasing Prompt
rephrasing_template = """
    TASK: Convert context-dependent questions into standalone queries.
    INPUT: 
    - chat_history: Previous messages
    - question: Current user query
    RULES:
    1. Replace pronouns (it/they/this) with specific referents
    2. Expand contextual phrases ("the above", "previous")
    3. Return original if already standalone
    4. NEVER answer or explain - only reformulate
    OUTPUT: Single reformulated question, preserving original intent and style.
"""

rephrasing_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", rephrasing_template),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}"),
    ]
)

history_aware_retriever = create_history_aware_retriever(
    llm=chatmodel,
    retriever=kb_retriever,
    prompt=rephrasing_prompt
)

# QA Prompt
system_prompt_template = (
    "As a Legal Assistant Chatbot specializing in legal queries, "
    "your primary objective is to provide accurate and concise information based on user queries. "
    "You will adhere strictly to the instructions provided, offering relevant context from the knowledge base. "
    "Keep responses to 4 sentences maximum. "
    "If a question falls outside the context, respond that you don't know. "
    "If asked about your creator, mention yash"
    "\nCONTEXT: {context}"
)

def process_chat(user_input):
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt_template),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ])

    qa_chain = create_stuff_documents_chain(chatmodel, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, qa_chain)

    chat_history = []
    response = rag_chain.invoke({
        "input": user_input,
        "chat_history": chat_history
    })

    return response["answer"].strip()