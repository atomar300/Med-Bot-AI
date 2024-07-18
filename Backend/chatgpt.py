import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS

import openai
from langchain.chains import ConversationalRetrievalChain, RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain.document_loaders import DirectoryLoader, TextLoader
from langchain.embeddings import OpenAIEmbeddings
from langchain.indexes import VectorstoreIndexCreator
from langchain.indexes.vectorstore import VectorStoreIndexWrapper
from langchain.llms import OpenAI
from langchain.vectorstores import Chroma

import constants

os.environ["OPENAI_API_KEY"] = constants.APIKEY


# The free api key using this repo: "https://github.com/PawanOsman/ChatGPT"
# os.environ["pk-tWGBmNALpdknjuQsPOwzpgUarJwCXdlEhhoTtniVySfiRYHc"] = constants.APIKEY
app = Flask(__name__)
CORS(app)

# Enable to save to disk & reuse the model (for repeated queries on the same data)
PERSIST = False

query = None
if len(sys.argv) > 1:
  query = sys.argv[1]

if PERSIST and os.path.exists("persist"):
  print("Reusing index...\n")
  vectorstore = Chroma(persist_directory="persist", embedding_function=OpenAIEmbeddings())
  index = VectorStoreIndexWrapper(vectorstore=vectorstore)
else:
  loader = TextLoader("data/data.txt") # Use this line if you only need data.txt
#   loader = DirectoryLoader("data/")
  if PERSIST:
    index = VectorstoreIndexCreator(vectorstore_kwargs={"persist_directory":"persist"}).from_loaders([loader])
  else:
    index = VectorstoreIndexCreator(embedding=OpenAIEmbeddings()).from_loaders([loader])

chain = ConversationalRetrievalChain.from_llm(
  llm=ChatOpenAI(model="gpt-3.5-turbo"),
  retriever=index.vectorstore.as_retriever(search_kwargs={"k": 1}),
)


@app.route('/chat', methods=['POST'])
def chat():
    chat_history = []
    user_input = request.json.get('input')
    result = chain({"question": user_input, "chat_history": chat_history})
    chat_history.append((user_input, result['answer']))
    return jsonify({'response': result['answer']})


if __name__ == "__main__":
    app.run(debug=True)