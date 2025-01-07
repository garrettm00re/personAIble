from flask import Flask, request, jsonify
from flask_cors import CORS
import os
print(os.getcwd())
from personAIble import *

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize the AI model
ai_model = load_initial_data()

@app.route('/api/ask', methods=['POST'])
def ask_question():
    try:
        data = request.json
        question = data.get('question')
        
        if not question:
            return jsonify({'error': 'No question provided'}), 400
        
        # Get answer from the model
        answer = ai_model.answer_question(question)
        
        return jsonify({
            'answer': answer
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)