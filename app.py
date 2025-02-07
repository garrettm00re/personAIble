from flask import Flask, render_template, request, jsonify
import os, sys
sys.path.append(os.getcwd())
from qaModel import *
import json
from supabase import create_client

app = Flask(__name__)

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_GOD_KEY") # probably not best practice but it works for now
supabase = create_client(supabase_url, supabase_key)

# Initialize the AI model, 
print("INIT MODEL AND LOAD DATA")
ai_model = load_initial_data()
print("MODEL LOADED")
@app.route('/')
def index():
    print("RENDERING INDEX")
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
    if request.method == 'GET':
        try:
            response = supabase.table('plans').select('subplans').eq('id', 1).execute()
            data = response.data[0]['subplans'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading how data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            result = supabase.table('plans').update({"subplans": new_data}).eq('id', 1).execute()
            print("RESULT: ", result)
            return jsonify({'message': 'Data updated successfully'})
        except Exception as e:
            print(f"Error updating how data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/who', methods=['GET', 'PUT'])
def handle_who():
    if request.method == 'GET':
        try:
            response = supabase.table('profiles').select('information').eq('id', 1).execute()
            data = response.data[0]['information'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading who data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            # Update data in Supabase
            result = supabase.table('profiles').update({"information": new_data}).eq('id', 1).execute()
            print("RESULT: ", result)
            return jsonify({'message': 'Data updated successfully'})
        except Exception as e:
            print(f"Error updating who data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

@app.route('/api/whereTo', methods=['GET', 'PUT'])
def handle_where_to():
    if request.method == 'GET':
        try:
            response = supabase.table('goals').select('desires').eq('id', 1).execute()
            data = response.data[0]['desires'] if response.data else {}
            return data
        except Exception as e:
            print(f"Error loading whereTo data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            new_data = request.json
            result = supabase.table('goals').update({"desires": new_data}).eq('id', 1).execute()
            print("RESULT: ", result)
            return jsonify({'message': 'Data updated successfully'})
        except Exception as e:
            print(f"Error updating whereTo data: {str(e)}", flush=True)
            return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)