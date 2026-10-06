import os
import csv
import tempfile
import streamlit as st
from pypdf import PdfReader

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction

import ollama

# -------------------------------
# Streamlit Page
# -------------------------------

st.set_page_config(
    page_title="AI Financial Expense Analyzer",
    page_icon="💰",
    layout="wide"
)

st.title("💰 AI Financial Expense Analyzer")
st.write(
    "Upload your bank statement (CSV or PDF) and ask financial questions."
)

# -------------------------------
# ChromaDB
# -------------------------------

EMBEDDING = SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)

client = chromadb.PersistentClient(path="./finance_db")

collection = client.get_or_create_collection(
    name="finance",
    embedding_function=EMBEDDING
)

# -------------------------------
# Helpers
# -------------------------------

def read_pdf(file):
    reader = PdfReader(file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return text


def read_csv(file):
    text = ""

    decoded = file.read().decode("utf-8").splitlines()

    reader = csv.reader(decoded)

    for row in reader:
        text += ", ".join(row) + "\n"

    return text


def split_text(text, chunk_size=500):

    chunks = []

    for i in range(0, len(text), chunk_size):
        chunks.append(text[i:i + chunk_size])

    return chunks


def store_chunks(chunks):

    try:
        collection.delete(ids=collection.get()["ids"])
    except:
        pass

    ids = []

    for i, chunk in enumerate(chunks):
        ids.append(str(i))

    collection.add(
        documents=chunks,
        ids=ids
    )


def search(query):

    results = collection.query(
        query_texts=[query],
        n_results=5
    )

    docs = results["documents"][0]

    return "\n".join(docs)


def ask_llm(question):

    context = search(question)

    prompt = f"""
You are an expert financial assistant.

Financial Data:

{context}

Question:
{question}

Answer clearly.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response["message"]["content"]


# -------------------------------
# Upload
# -------------------------------

uploaded = st.file_uploader(
    "Upload CSV or PDF",
    type=["csv", "pdf"]
)

if uploaded:

    with st.spinner("Reading file..."):

        if uploaded.name.endswith(".csv"):
            text = read_csv(uploaded)

        else:
            text = read_pdf(uploaded)

        chunks = split_text(text)

        store_chunks(chunks)

    st.success("File Indexed Successfully!")

    st.subheader("Preview")

    st.text_area(
        "",
        text[:3000],
        height=250
    )

    st.divider()

    st.subheader("Ask Questions")

    question = st.text_input(
        "Example: How much did I spend on shopping?"
    )

    if st.button("Analyze"):

        if question.strip():

            with st.spinner("Thinking..."):

                answer = ask_llm(question)

            st.markdown("### AI Answer")

            st.write(answer)

            st.divider()

            st.markdown("### Suggested Questions")

            suggestions = [
                "What are my highest expenses?",
                "Where can I save money?",
                "Summarize my spending.",
                "Which month had maximum expenses?",
                "List all food expenses.",
                "List all UPI transactions.",
                "How much salary was credited?",
                "Show shopping expenses."
            ]

            for s in suggestions:
                st.write("•", s)