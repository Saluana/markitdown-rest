from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import List
import os
import shutil
import tempfile
from markitdown import MarkItDown
from openai import OpenAI
from utils import load_environment

# Replace load_dotenv() with the new function
environment = load_environment()

app = FastAPI()
client = OpenAI()
converter = MarkItDown(llm_client=client, llm_model="gpt-4o-mini")

@app.post("/convert/")
async def convert_file(file: UploadFile = File(...)):
    try:
        # Save the uploaded file to a temporary location
        handle, temp_path = tempfile.mkstemp()
        with open(temp_path, "wb") as temp_file:
            shutil.copyfileobj(file.file, temp_file)
        
        # Convert the file
        result = converter.convert_local(temp_path, file_extension=os.path.splitext(file.filename)[1])
        
        # Clean up the temporary file
        os.close(handle)
        os.remove(temp_path)

        return JSONResponse(content={"title": result.title, "text_content": result.text_content })
    except markitdown._markitdown.FileConversionException as e:
        raise HTTPException(status_code=500, detail=f"File conversion error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/convert-url/")
async def convert_url(url: str = Form(...)):
    try:
        result = converter.convert_url(url)
        return JSONResponse(content={"title": result.title, "text_content": result.text_content})
    except Exception as e:
        # Add detailed error logging
        import traceback
        error_detail = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_detail)  # This will show in Docker logs
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/youtube/")
async def youtube_transcript(url: str = Form(...)):
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        video_id = url.split("watch?v=")[1]
        
        # Try multiple approaches to get the transcript
        try:
            # Try with just English
            proxy_url = environment.get("PROXY_URL")
            if proxy_url:
                proxies = {"https": proxy_url}
            else:
                proxies = {}

            transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies, languages=['en'])
        except Exception as e1:
            try:
                # Try with auto-generated captions
                transcript = YouTubeTranscriptApi.get_transcript(video_id, proxies=proxies, languages=['en-US', 'en-GB', 'en', 'a.en'])
            except Exception as e2:
                try:
                    # Try with all available languages
                    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
                    transcript = transcript_list.find_transcript(['en']).fetch()
                except Exception as e3:
                    error_detail = (
                        f"Failed to get transcript:\n"
                        f"Attempt 1 (en): {str(e1)}\n"
                        f"Attempt 2 (multiple en): {str(e2)}\n"
                        f"Attempt 3 (list transcripts): {str(e3)}"
                    )
                    print(error_detail)
                    raise HTTPException(status_code=500, detail=error_detail)

        # Create full transcript without timestamps
        full_transcript = " ".join([part["text"] for part in transcript])
        
        # Create timestamped transcript in markdown format
        timestamped_transcript = ""
        for part in transcript:
            minutes = int(part["start"] // 60)
            seconds = int(part["start"] % 60)
            timestamp = f"[{minutes:02d}:{seconds:02d}]"
            timestamped_transcript += f"{timestamp} {part['text']}\n"

        # Format as markdown
        markdown_transcript = f"""### Full Transcript
{full_transcript}

### Timestamped Transcript
{timestamped_transcript}"""

        # Create structured transcript
        structured_transcript = []
        for part in transcript:
            structured_transcript.append({
                "text": part["text"],
                "start": part["start"],
                "duration": part["duration"]
            })
        
        return JSONResponse(content={
            "transcript": full_transcript,
            "timestamped_transcript": timestamped_transcript,
            "markdown": markdown_transcript,
            "structured_transcript": structured_transcript
        })
    except Exception as e:
        import traceback
        error_detail = f"Error: {str(e)}\nTraceback: {traceback.format_exc()}"
        print(error_detail)
        raise HTTPException(status_code=500, detail=error_detail)