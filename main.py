import os
import re
import validators
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")
scraper_api = os.getenv("SCRAPER_API")

app = FastAPI()

# Request body model
class SummaryRequest(BaseModel):
    url: str

def extract_video_id(url: str) -> str:
    regex = r"(?:v=|\/|embed\/|shorts\/)([0-9A-Za-z_-]{11})"
    match = re.search(regex, url)
    return match.group(1) if match else None

# Get YouTube transcript
def get_youtube_transcript_as_doc(video_url: str) -> list[Document]:
    video_id = extract_video_id(video_url)
    if not video_id:
        raise ValueError("Invalid YouTube video URL")
    proxy = {
        "https": f"http://scraperapi:{scraper_api}@proxy-server.scraperapi.com:8001"
    }
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'],proxies=proxy)
    except NoTranscriptFound:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        try:
            transcript = transcript_list.find_transcript(['en-IN'])
        except NoTranscriptFound:
            try:
                transcript = transcript_list.find_transcript(['hi']).translate('en')
            except Exception as e:
                raise NoTranscriptFound(
                    f"No English-like transcript available for this video: {video_id}"
                ) from e
        if hasattr(transcript, "fetch"):
            transcript = transcript.fetch()

    full_text = " ".join([segment['text'] for segment in transcript])
    return [Document(page_content=full_text)]

# Prompt
prompt_template = """
Provide a concise, accurate summary of the following content in around 300 words:
Content:
{text}
"""
prompt = PromptTemplate(template=prompt_template, input_variables=["text"])

# LLM model
llm = ChatGroq(groq_api_key=api_key, model_name="Gemma2-9b-It")

@app.post("/summary")
async def generate_summary(req: SummaryRequest):
    url = req.url

    if not url.strip():
        return {"error": "URL is empty"}
    elif not validators.url(url):
        return {"error": "Invalid URL"}

    try:
        if "youtube.com" in url or "youtu.be" in url:
            docs = get_youtube_transcript_as_doc(url)
        else:
            loader = UnstructuredURLLoader(
                urls=[url],
                ssl_verify=False,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            docs = loader.load()

        splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
        split_docs = splitter.split_documents(docs)

        chain = load_summarize_chain(
            llm=llm,
            chain_type="map_reduce",
            map_prompt=prompt,
            combine_prompt=prompt,
            verbose=False
        )

        output = chain.run(split_docs)
        return {"summary": output}

    except Exception as e:
        return {"error": f"Something went wrong: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
