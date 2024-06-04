import os
from pydub import AudioSegment
from pydub.utils import which
import langid
from gtts import gTTS
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Get the API key from the environment variable
api_key = os.getenv('API_KEY')

# Ensure pydub can find ffmpeg
AudioSegment.converter = which("ffmpeg")

# Text-to-speech function from stimme.py
def text_to_speech(text, filename='output.mp3'):
    # Split the text into lines
    sentences = text.strip().split('\n')
    
    # Initialize an empty list to hold the audio segments
    audio_segments = []
    pause = AudioSegment.silent(duration=3500)

    # Track the previous language to add pause if needed
    prev_lang = None

    # Process each sentence
    for sentence in sentences:
        sentence = sentence.strip()
        if not sentence:
            continue
        
        # Detect the language of the sentence
        lang, _ = langid.classify(sentence)
        
        if lang == 'en':
            tts = gTTS(text=sentence, lang='en', slow=True)
        elif lang == 'de':
            tts = gTTS(text=sentence, lang='de', slow=True)
        else:
            print(f"Skipping unrecognized language: {sentence}")
            continue

        # Save the temporary audio file
        temp_file = "temp.mp3"
        tts.save(temp_file)

        # Load the audio file and append it to the list
        audio_segment = AudioSegment.from_mp3(temp_file)
        #audio_segments.append(audio_segment)

        # Add a pause if the language changes from English to German or vice versa
        if prev_lang == 'en':
            audio_segments.append(pause)

        audio_segments.append(audio_segment)
        prev_lang = lang

        # Clean up the temporary file
        os.remove(temp_file)

    # Concatenate all audio segments
    if audio_segments:
        final_audio = sum(audio_segments)
        # Export the final audio to an MP3 file
        final_audio.export(filename, format="mp3")
        print(f"Audio file saved as {filename}")
    else:
        print("No valid sentences found to process.")

# Integrate index.py functionality
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.0-pro')

# Set up the model
generation_config = {
    "max_output_tokens": 1024,
}

# Ask the user for input
theme = input("Enter the theme: ")
language_level = input("Enter the German level: ")


# Generate content
response = model.generate_content(
    f"Create an advanced text of 50 sentences. Use short sentences; between 5 to 10 words per sentence. "
    f"Theme: {theme}. "
    f"Language level: {language_level}. "
    f"Provide each sentence in both German and English. "
    f"Follow the format: "
        "English: Sentence. '\n'"
        "German: Sentence. '\n'"
    "Don't write the words 'German' or 'English' or numbered the sentences, just provided the sentences."
)

print(response.text)

# Get the generated text
generated_text = response.text

# Define the filename using theme and language_level
filename = f"{theme}_{language_level}.mp3"
filenametext = f"{theme}_{language_level}.md"

# Saved the generated text into a .md file
Path(filenametext).write_text(generated_text, encoding='utf-8')

# Pass the generated text to the text_to_speech function
text_to_speech(generated_text, filename=filename)
