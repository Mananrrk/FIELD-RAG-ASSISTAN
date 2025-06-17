import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain_community.llms import HuggingFaceHub
from langchain.prompts import PromptTemplate

#Hugging Face Hub token
import os
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN")

# Loading and split documents
data_folder = "data"
documents = []
for file_name in os.listdir(data_folder):
    if file_name.endswith(".txt"):
        loader = TextLoader(os.path.join(data_folder, file_name))
        documents.extend(loader.load())

text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = text_splitter.split_documents(documents)

# Generating embeddings and building FAISS index
embedding = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
db = FAISS.from_documents(texts, embedding)

# Loading the LLM
llm = HuggingFaceHub(
    repo_id="HuggingFaceH4/zephyr-7b-beta",
    task="text-generation",
    model_kwargs={"temperature": 0.5, "max_new_tokens": 512}
)

# Defining a custom prompt to control answer format
custom_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a helpful assistant. Use ONLY the following pieces of context to answer the single question at the end. 
Do not invent or assume anything outside of the context.

Context:
{context}

Question: {question}

Helpful Answer:
"""
)


# Creating RetrievalQA chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=db.as_retriever(),
    chain_type="stuff",
    chain_type_kwargs={"prompt": custom_prompt}
)

# Main CLI loop
if __name__ == "__main__":
    print("\n💡 Ask your questions (type 'exit' to quit):")
    while True:
        query = input(">> ")
        if query.strip().lower() == "exit":
            break
        try:
            retrieved_docs = db.similarity_search(query, k=2)

            if not retrieved_docs or retrieved_docs[0].page_content.strip() == "":
                print("\n🤖 I'm sorry, I don't have enough information to answer that.")
            else:
                result = qa_chain.invoke({"query": query})
                print("\n✅ Answer:\n", result["result"])

        except Exception as e:
            print("❌ Error:", str(e))








