from flask import Flask, render_template, request, jsonify
from langchain.llms import Ollama
from datetime import datetime
import uuid
from utils import *

app = Flask(__name__)

messages = []


@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form['instruction']
        
        # Generate bot's response
        response = generate_bot_response(user_input, chain)
        
        # Store the messages (user and bot)
        id1 = str(uuid.uuid4())
        messages.append({"id": id1, "sender": "user", "text": user_input, "time": get_current_time()})
        id2 = str(uuid.uuid4())
        messages.append({"id": id2, "sender": "start", "text": response, "time": get_current_time()})

        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(messages=messages)  # Return the updated messages as JSON
        
    return render_template('index.html', messages=messages)

if __name__ == '__main__':

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

    app.run(debug=True)

    #
