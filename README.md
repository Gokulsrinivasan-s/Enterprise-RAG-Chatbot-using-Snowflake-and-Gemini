# 🤖 Enterprise RAG Chatbot

An AI-powered Enterprise Document Assistant that allows users to upload PDF documents and ask questions using natural language.

This project uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from documents using vector similarity search and generate accurate responses using Google's Gemini LLM.

---

# 🚀 Project Overview

Enterprise RAG Chatbot helps organizations interact with their documents intelligently.

Instead of manually searching through large PDF files, users can upload documents and ask questions. The system retrieves the most relevant document sections and provides context-aware answers.

---

# ✨ Features

## 📄 Document Processing
- Upload PDF documents
- Extract text from documents
- Split documents into smaller chunks
- Generate semantic embeddings

## 🔍 Intelligent Search
- Convert user questions into embeddings
- Perform vector similarity search
- Retrieve relevant document chunks

## 🧠 AI Question Answering
- Integrated with Google Gemini 2.5 Flash
- Generates answers based only on retrieved document context
- Reduces hallucination using RAG approach

## 💬 Chat Interface
- Interactive Streamlit web application
- Supports conversational questions
- Displays retrieved document sources

---

# 🏗️ Architecture


---

# 🛠️ Technologies Used

## Programming Language
- Python

## Frontend
- Streamlit

## AI / ML
- Sentence Transformers
- Google Gemini 2.5 Flash
- Retrieval-Augmented Generation (RAG)
- Natural Language Processing

## Database
- Snowflake
- Snowflake Vector Search

## Document Processing
- PDF Processing
- Text Chunking
- Embedding Generation

## Environment
- Python Virtual Environment
- dotenv

---

# 📂 Project Structure
enterprise_rag_chatbot/

│
├── app.py
│       Main Streamlit application
│
├── upload_processor.py
│       PDF extraction and chunk creation
│
├── snowflake_utils.py
│       Store embeddings into Snowflake
│
├── documents/
│       Uploaded PDF files
│
├── .env
│       API keys and database credentials
│
├── requirements.txt
│
└── README.md
