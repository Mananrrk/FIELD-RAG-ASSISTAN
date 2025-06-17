from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import SentenceTransformerEmbeddings
import os

#Load all .txt files
docs = []
for filename in os.listdir("data"):
    if filename.endswith(".txt"):
        loader = TextLoader(os.path.join("data", filename))
        docs.extend(loader.load())

#Spliting documents into smaller chunks
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100
)
chunks = text_splitter.split_documents(docs)

embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

#Converted document chunks to vector embeddings using FAISS
db = FAISS.from_documents(chunks, embedding_model)

#Saving FAISS index 
db.save_local("faiss_index")

print("✅ FAISS index created and saved in 'faiss_index/' folder.")

