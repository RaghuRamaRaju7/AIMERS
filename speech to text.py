import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

# Initialize the speech recognizer and text-to-speech engine
recognizer = sr.Recognizer()
tts_engine = pyttsx3.init()

# Configure the Google Generative AI with your API key
genai.configure(api_key="AIzaSyAK_EeB3ps3KP6HjUdjUKT3SWxz4k6nP_U")

# Create the model configuration
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

# Start a chat session
chat_session = model.start_chat(
    history=[
        {"role": "user", "parts": ["hello"]},
        {"role": "model", "parts": ["Hello! How can I help you today?\n"]},
    ]
)

def listen_to_speech():
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(f"Recognized: {text}")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service")
            return None

def generate_response(prompt):
    response = chat_session.send_message(prompt)
    return response.text

def speak_text(text):
    tts_engine.say(text)
    tts_engine.runAndWait()

def chatbot():
    print("Chatbot is ready. Ask your questions by speaking...")
    while True:
        question = listen_to_speech()
        if question:
            response = generate_response(question)
            print(f"Response: {response}")
            speak_text(response)

if __name__ == "__main__":
    chatbot()
