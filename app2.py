from flask import Flask, request, jsonify, render_template
from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import google.generativeai as genai
import textwrap

app = Flask(__name__)

# Load the fine-tuned model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("./fine-tuned-model")
model = AutoModelForSequenceClassification.from_pretrained("./fine-tuned-model")

# Create a pipeline for sentiment analysis
sentiment_analyzer = pipeline("sentiment-analysis", model=model, tokenizer=tokenizer)

GOOGLE_API_KEY = "AIzaSyDB5i8h8QV1BVgG-ZO9JDh1EicU8luhPrs"
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

def to_markdown(text):
    text = text.replace('•', '  *')
    return textwrap.indent(text, '> ', predicate=lambda _: True)

@app.route('/analyze', methods=['POST'])
def predict_sentiment():
    data = request.get_json()
    message = data.get('message')
    
    if not message:
        return jsonify({"error": "No message provided"}), 400

    # Perform sentiment analysis using the pipeline
    result = sentiment_analyzer(message)
    sentiment = result[0]['label']
    response_message = ""

    if sentiment == 'POSITIVE':
        try:
            response = model.generate_content(message)
            text = to_markdown(response.text)
            response_message = text
        except Exception as e:
            response_message = f"Error contacting Gemini: {str(e)}"
    else:
        response_message = "Warning: Negative sentiment detected. Message not forwarded."

    return jsonify({"response": response_message})

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

