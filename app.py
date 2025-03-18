from flask import Flask, render_template, request, jsonify
import os, sys
sys.path.append(os.getcwd())
from qaModel import *
import json
from supabase import create_client
from datetime import datetime
import time
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Supabase client
supabase_url = os.environ.get("SUPABASE_URL")
supabase_key = os.environ.get("SUPABASE_GOD_KEY") # probably not best practice but it works for now
supabase = create_client(supabase_url, supabase_key)

# Initialize the AI model
print("INIT MODEL AND LOAD DATA")
ai_model = load_initial_data()
# Pass the database client to the model
ai_model.db_client = supabase
print("MODEL LOADED")

# for followup
answer = None
success = False

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

@app.route('/api/followup', methods=['POST'])
def handle_followup():
    global answer, success
    answer = None
    success = False
    
    print('handle followup')
    data = request.json
    QA = data.get('QA')
    if not QA:
        return jsonify({'error': 'No QA pairs provided'}), 400

    try:
        question, answers = QA
        question_id = str(time.time())
        # Send question to frontend
        socketio.emit('ask_followup', {
            'question': question,
            'question_id': question_id
        })

        print('waiting for answer')
        # Simple wait loop with timeout
        timeout = time.time() + 60 # 1 minute timeout
        while answer is None:
            if time.time() > timeout:
                return jsonify({'error': 'Response timeout'}), 408
            time.sleep(0.5)  # Small sleep to prevent CPU spinning
        if success:
            print('got answer', answer)
            answers = [answer]
            # update supabase
            result = supabase.table('QA').update({"answers": answers}).eq('id', 1).execute()
            print("RESULT: ", result)

            return jsonify({'answer': answer})

    except Exception as e:
        print(f"Error in handle_followup: {str(e)}", flush=True)
        return jsonify({'error': str(e)}), 500
    
@socketio.on('followup_response')
def handle_followup_response(data):
    print('handle followup response')
    global answer, success
    answer = data.get('answer')
    if answer != None:
        success = True

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)