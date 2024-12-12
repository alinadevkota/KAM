from flask import Flask, render_template, request, jsonify
from langchain.llms import Ollama
from datetime import datetime
import uuid
from utils import *
from werkzeug.utils import secure_filename
import re

app = Flask(__name__)

messages = []


UPLOAD_FOLDER = 'documents'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def format_message(message):
    # Replace **text** with <strong>text</strong>
    message = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', message)

    # Replace * text with <li>text</li> for bullet points
    message = re.sub(r'^\* (.+)$', r'<li>\1</li>', message, flags=re.MULTILINE)
    
    # Wrap all <li> elements with a single <ul>, ensuring proper list structure
    if '<li>' in message:
        message = re.sub(r'(<li>.*?</li>(?:\n|$))+', lambda m: f'<ul>{m.group(0).strip()}</ul>', message, flags=re.DOTALL)

    return message

@app.route('/', methods=['GET', 'POST'])
def chat():
    global chain, llm, embedding_model, retriever  # Declare global variables

    if request.method == 'POST':
        user_input = request.form.get('instruction', '')
        file = request.files.get('file')

        # Debugging print statements
        print("User Input: ", user_input)
        if file:
            print("File Uploaded: ", file.filename)

        # Case 0: Invalid filetype
        if file and not allowed_file(file.filename):
            filename = file.filename

            # Add user message indicating file upload
            user_message = f"Uploaded file: {filename}"
            id1 = str(uuid.uuid4())
            messages.append({"id": id1, "sender": "user", "text": user_message, "time": get_current_time()})

            # Add bot message confirming the file upload and reindex
            bot_message = f"Invalid file type. Only PDF files are allowed."
            id2 = str(uuid.uuid4())
            messages.append({"id": id2, "sender": "start", "text": bot_message, "time": get_current_time()})

        # Case 1: Only a file is uploaded (no instruction)
        elif file and allowed_file(file.filename) and user_input.strip() == '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"Embedding generation completed after file '{filename}' upload.")

            # Reindex the file and update retriever
            retriever = process_documents(app.config['UPLOAD_FOLDER'], embedding_model)
            print(f"File '{filename}' indexed.")
            chain = load_qa_chain(retriever, llm, prompt)

            # Add user message indicating file upload
            user_message = f"Uploaded file: {filename}"
            id1 = str(uuid.uuid4())
            messages.append({"id": id1, "sender": "user", "text": user_message, "time": get_current_time()})

            # Add bot message confirming the file upload and reindex
            bot_message = f"File '{filename}' has been successfully uploaded and reindexed."
            id2 = str(uuid.uuid4())
            messages.append({"id": id2, "sender": "start", "text": bot_message, "time": get_current_time()})

        # Case 2: Only an instruction is provided (no file)
        elif user_input.strip() != '' and not file:
            # Follow user instruction without file
            response = generate_bot_response(user_input, chain)

            # Add user message with the instruction
            id1 = str(uuid.uuid4())
            messages.append({"id": id1, "sender": "user", "text": user_input, "time": get_current_time()})

            # Add bot response to the instruction
            id2 = str(uuid.uuid4())
            messages.append({"id": id2, "sender": "start", "text": response, "time": get_current_time()})

        # Case 3: Both a file and an instruction are provided
        elif file and allowed_file(file.filename) and user_input.strip() != '':
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            print(f"Embedding generation completed after file '{filename}' upload.")

            # Reindex the file and process based on the instruction
            retriever = process_documents(app.config['UPLOAD_FOLDER'], embedding_model)
            print(f"File '{filename}' indexed.")
            chain = load_qa_chain(retriever, llm, prompt)

            # Add user message indicating file upload and instruction
            user_message = f"Uploaded file: {filename} with instruction: {user_input}"
            id1 = str(uuid.uuid4())
            messages.append({"id": id1, "sender": "user", "text": user_message, "time": get_current_time()})

            # Generate the bot's response based on the file content and user instruction
            response = generate_bot_response(user_input, chain)

            # Add bot response
            id2 = str(uuid.uuid4())
            messages.append({"id": id2, "sender": "start", "text": response, "time": get_current_time()})

        for message in messages:
            message["text"] = format_message(message["text"])

        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(messages=messages)  # Return the updated messages as JSON

    return render_template('index.html', messages=messages)




if __name__ == '__main__':
    global llm, embedding_model, retriever, chain

    folder_path = 'documents'

    llm = Ollama(model="llama3.1", temperature=0)
    embedding_model = load_embedding_model(model_path="BAAI/bge-large-en-v1.5")
    retriever = process_documents(folder_path, embedding_model)

    template = """
    ### System:

    You are a respectful and honest research assistant to help professor. You have to answer the professor's questions using only the context provided (local knowledge based). \
    If you don't know the answer, say "I don't know", then attempt to answer from your global knowledge base. \
    
    For all answers, clearly specify if you answer was based on your local knowledge base or global knowledge base:

    ### Context:
    {context}

    ### User:
    {question}

    ### Response:
    """
    prompt = PromptTemplate.from_template(template)
    chain = load_qa_chain(retriever, llm, prompt)

    app.run(host="0.0.0.0", port=5000)

    #
