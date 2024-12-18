from flask import Flask, request, render_template, redirect, url_for
import speech_recognition as sr
import spacy
from collections import Counter
import os

app = Flask(__name__)

# Initialize spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Function to extract audio text
def audio_to_text(audio_file):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Audio could not be understood."
    except sr.RequestError:
        return "Error with the speech recognition service."

# Function to detect scam words
def detect_scam_words(text, scam_words_list):
    doc = nlp(text)
    words = [token.text.lower() for token in doc if token.is_alpha]
    word_count = Counter(words)
    scam_count = sum(word_count[word] for word in scam_words_list)
    return scam_count

# Function to calculate fraud detection score
def fraud_score(scam_count, total_words):
    if total_words == 0:
        return 0
    fraud_percentage = (scam_count / total_words) * 100
    return min(fraud_percentage, 100)

# Load scam words from file
def load_scam_words():
    with open("scam_words.txt", "r") as file:
        return file.read().splitlines()

# Flask routes
@app.route("/")
def index():
    return render_template("upload.html")

@app.route("/process", methods=["POST"])
def process_audio():
    if "audio_file" not in request.files:
        return redirect(url_for("index"))
    
    audio_file = request.files["audio_file"]
    if audio_file.filename == "":
        return redirect(url_for("index"))
    
    # Save the uploaded audio file
    audio_path = os.path.join("uploaded_audio.wav")
    audio_file.save(audio_path)
    
    # Process the audio file
    text = audio_to_text(audio_path)
    scam_words = load_scam_words()
    scam_count = detect_scam_words(text, scam_words)
    total_words = len(text.split())
    score = fraud_score(scam_count, total_words)
    
    # Render output page
    return render_template("output.html", text=text, score=score)

if __name__ == "__main__":
    app.run(debug=True)
