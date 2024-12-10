from QA import *
from langchain import PromptTemplate
import os
from datetime import datetime
from utils import *



# FRONTEND UTILS
# Function to get the current time in HH:MM format
def get_current_time():
    return datetime.now().strftime("%H:%M")

# Function to generate a bot response (customize this logic as needed)
def generate_bot_response(user_input, chain):

    response = get_response(user_input, chain)
    return response


# BACKEND UTILS
def process_documents(folder_path, embedding_model):
    file_paths = [
        os.path.join(root, file)
        for root, _, files in os.walk(folder_path)
        for file in files if file.endswith(".pdf")
    ]

    # Load and split documents from all PDFs
    all_documents = []
    for file_path in file_paths:
        try:
            docs = load_pdf_data(file_path=file_path)
            all_documents.extend(split_docs(docs))
        except ValueError as e:
            print(f"Error loading PDF {file_path}: {e}")
            continue

    print("Completed loading documents")
    print("Creating embeddings...")
    # Create vectorstore and retriever
    vectorstore = create_embeddings(all_documents, embedding_model)
    print("Embeddings created!")
    retriever = vectorstore.as_retriever()

    return retriever


def get_local_response(user_input, local_knowledge_space):

    template = """
    ### System:
    You are a respectful and honest research assistant to help professor. You have to answer the professor's questions using only the context provided. \
    If you don't know the answer, say "I don't know."

    ### Context:
    {context}

    ### User:
    {question}

    ### Response:
    """
    prompt = PromptTemplate.from_template(template)

    return
