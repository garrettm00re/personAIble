from flask import Flask, render_template, request, jsonify
import os, sys
sys.path.append(os.getcwd())
from qaModel import *
import json

app = Flask(__name__)

# Initialize the AI model
ai_model = load_initial_data()
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/ask', methods=['POST'])
def ask():
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

@app.route('/api/how')
def get_how():
    try:
        with open('userModel/how.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        print(f"Error loading how.json: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/who')
def get_who():
    try:
        with open('userModel/who.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        print(f"Error loading who.json: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500

@app.route('/api/whereTo')
def get_where_to():
    try:
        with open('userModel/whereTo.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except Exception as e:
        print(f"Error loading whereTo.json: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)