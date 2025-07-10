# 📺 Clipr.ai API

A FastAPI-based backend service that summarizes YouTube videos and web pages using large language models (LLMs) via the Groq API. This is the backend powering Clipr.ai — a smart summarization tool.

---

## 🚀 Features

- 🔗 Accepts **YouTube** or **Web URLs**
- 🧠 Uses **LangChain** + **Groq (Gemma-2-9b-It)** to generate concise summaries
- 🧾 Automatically extracts and processes transcripts or web page content
- ⚡ RESTful API built with **FastAPI**
- ☁️ Deployable to Render, Railway, or any cloud service

---

## 🛠️ Tech Stack

- **FastAPI** – API backend
- **LangChain** – LLM orchestration
- **Groq** – LLM inference (via Gemma-2-9b-It)
- **YouTube Transcript API** – YouTube caption retrieval
- **UnstructuredURLLoader** – Load web content
- **Python 3.10+**

---

## 🔑 API KEY 
GROQ_API_KEY = your_groq_api_key

---

## 📦 Installation

```bash
git clone https://github.com/your-username/cliprai-api.git
cd cliprai-api
pip install -r requirements.txt

