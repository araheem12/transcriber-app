import streamlit as st
import whisper
import tempfile
import os
import subprocess
import sys
import shutil
import requests
import zipfile

# Function to download and setup FFmpeg automatically
def setup_ffmpeg():
    ffmpeg_dir = os.path.join(os.getcwd(), "ffmpeg_bin")
    ffmpeg_path = os.path.join(ffmpeg_dir, "ffmpeg.exe")

    if not os.path.exists(ffmpeg_path):
        st.write("Downloading FFmpeg... ⏳")

        # Download FFmpeg Windows binary
        url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
        zip_path = "ffmpeg.zip"

        with open(zip_path, "wb") as f:
            f.write(requests.get(url, stream=True).content)

        # Extract FFmpeg
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            zip_ref.extractall("ffmpeg_temp")

        # Move extracted binaries
        extracted_dir = [d for d in os.listdir("ffmpeg_temp") if os.path.isdir(os.path.join("ffmpeg_temp", d))][0]
        shutil.move(os.path.join("ffmpeg_temp", extracted_dir, "bin"), ffmpeg_dir)

        # Clean up
        os.remove(zip_path)
        shutil.rmtree("ffmpeg_temp")

        st.write("FFmpeg setup complete ✅")

    return ffmpeg_dir

# Ensure FFmpeg is available
ffmpeg_dir = setup_ffmpeg()
os.environ["PATH"] += os.pathsep + ffmpeg_dir

# Load Whisper model
@st.cache_resource
def load_model():
    return whisper.load_model("small")

model = load_model()

# Streamlit UI
st.title("Whisper AI Transcriber")
st.write("Upload an audio file, and the AI will transcribe it for you.")

uploaded_file = st.file_uploader("Upload Audio", type=["mp3", "wav", "m4a", "ogg"])

if uploaded_file:
    st.audio(uploaded_file, format="audio/mp3")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        temp_audio.write(uploaded_file.read())
        temp_audio_path = temp_audio.name

    # Transcribe using Whisper
    st.write("Transcribing... ⏳")
    result = model.transcribe(temp_audio_path)
    st.subheader("Transcription:")
    st.write(result["text"])

    # Clean up temp file
    os.remove(temp_audio_path)
