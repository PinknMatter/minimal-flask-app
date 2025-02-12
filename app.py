from flask import Flask, render_template, request, url_for
import openai
import os
from dotenv import load_dotenv
import requests
from flask_pagedown import PageDown
from markdown import markdown

load_dotenv()  # Load environment variables from .env

app = Flask(__name__)
pagedown = PageDown(app)  # Initialize PageDown
openai.api_key = os.getenv("OPENAI_API_KEY")  # Securely load API key

def analyze_dream(dream_description):
    try:
        # Get Jungian interpretation
        interpretation_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are a Jungian dream analyst. Analyze dreams using Carl Jung's analytical psychology framework. 
                Focus on:
                1. Archetypal symbols and their universal meanings
                2. Personal and collective unconscious elements
                3. The dreamer's psychological journey
                Keep the analysis brief and insightful. Respond in markdown."""},
                {"role": "user", "content": f"Please analyze this dream from a Jungian perspective: {dream_description}"}
            ],
            temperature=0.7,
            max_tokens=250
        )
        
        interpretation = interpretation_response.choices[0].message.content
        # Convert interpretation to HTML using markdown
        interpretation_html = markdown(interpretation)
        
        # Generate image prompt based on dream and interpretation
        image_prompt_response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Create a brief, vivid image prompt based on the dream's key symbols and emotions."},
                {"role": "user", "content": f"Create a simple image prompt for this dream: {dream_description}"}
            ],
            temperature=0.7,
            max_tokens=100
        )
        
        image_prompt = image_prompt_response.choices[0].message.content
        
        # Generate image using DALL-E
        image_response = openai.images.generate(
            model="dall-e-3",
            prompt=image_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        return {
            'interpretation': interpretation_html,
            'image_prompt': image_prompt,
            'image_url': image_response.data[0].url
        }
        
    except Exception as e:
        return {
            'error': str(e),
            'interpretation': None,
            'image_url': None,
            'image_prompt': None
        }

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    if request.method == "POST":
        dream = request.form.get("dream_description")
        if dream:
            result = analyze_dream(dream)
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True)  # Run locally for testing