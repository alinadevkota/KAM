from QA import *
from langchain.llms import Ollama
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
import os

def process_documents(doc_root):
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
    vectorstore = create_embeddings(all_documents, embed)
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

# Initialize LLM (Ollama) and Embedding Model
llm = Ollama(model="llama3.1", temperature=0)
embed = load_embedding_model(model_path="BAAI/bge-large-en-v1.5")





# Define the PDF folder path
folder_path = "documents"

# # Get all PDF file paths in the folder (and its subfolders)
# file_paths = [
#     os.path.join(root, file)
#     for root, _, files in os.walk(folder_path)
#     for file in files if file.endswith(".pdf")
# ]

# # Load and split documents from all PDFs
# all_documents = []
# for file_path in file_paths:
#     try:
#         docs = load_pdf_data(file_path=file_path)
#         all_documents.extend(split_docs(docs))
#     except ValueError as e:
#         print(f"Error loading PDF {file_path}: {e}")
#         continue

# # Create vectorstore and retriever
# vectorstore = create_embeddings(all_documents, embed)
# retriever = vectorstore.as_retriever()

retriever = process_documents(folder_path)


# Define the prompt template for Q&A
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

# Create the QA chain
chain = load_qa_chain(retriever, llm, prompt)

# Get responses for various questions
questions = [
    "What is large language model",
    "Give me a summary of the paper?",
    "Describe the quantization method in short",
    "What is federated learning",
    "Give me the summary of the paper: Federated Learning with Non-IID Data"
]

# for question in questions:
question = input('Enter question: ')
response = get_response(question, chain)
print(response)