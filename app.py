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

@app.route('/api/how', methods=['GET', 'PUT'])
def handle_how():
    file_path = 'charlesRiverAssets/how.json'
    if request.method == 'GET':
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return jsonify(data)
        except Exception as e:
            print(f"Error loading how.json: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            with open(file_path, 'w') as file:
                json.dump(new_data, file, indent=2)
            return jsonify({'message': 'File updated successfully'})
        except Exception as e:
            print(f"Error updating how.json: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/who', methods=['GET', 'PUT'])
def handle_who():
    file_path = 'charlesRiverAssets/who.json'
    if request.method == 'GET':
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return jsonify(data)
        except Exception as e:
            print(f"Error loading who.json: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            with open(file_path, 'w') as file:
                json.dump(new_data, file, indent=2)
            return jsonify({'message': 'File updated successfully'})
        except Exception as e:
            print(f"Error updating who.json: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/whereTo', methods=['GET', 'PUT'])
def handle_where_to():
    file_path = 'charlesRiverAssets/whereTo.json'
    if request.method == 'GET':
        try:
            with open(file_path, 'r') as file:
                data = json.load(file)
            return jsonify(data)
        except Exception as e:
            print(f"Error loading whereTo.json: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            with open(file_path, 'w') as file:
                json.dump(new_data, file, indent=2)
            return jsonify({'message': 'File updated successfully'})
        except Exception as e:
            print(f"Error updating whereTo.json: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)