from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    StorageContext,
    load_index_from_storage,
)
from llama_index.core.postprocessor import LLMRerank
from llama_index.llms.openai import OpenAI
from IPython.display import display , HTML
from llama_index.core import Settings
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core import QueryBundle
import pandas as pd
import os
import openai
import uvicorn
from fastapi import FastAPI
import nest_asyncio

nest_asyncio.apply()

pd.set_option("display.max_colwidth", None)
openai.api_key = os.getenv("OPENAI_API_KEY")

app = FastAPI()

Settings.llm = OpenAI(temperature=0, model="gpt-3.5-turbo")
Settings.chunk_size = 512
Settings.max_tokens = 256

# load documents
PERSIST_DIR = "./storage"
if not os.path.exists(PERSIST_DIR):
    documents = SimpleDirectoryReader("data").load_data()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=PERSIST_DIR)
else:
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)


def get_retrieved_nodes(
    query_str, vector_top_k=10, reranker_top_n=3, with_reranker=False
):
    query_bundle = QueryBundle(query_str)
    # configure retriever
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=vector_top_k,
    )
    retrieved_nodes = retriever.retrieve(query_bundle)

    if with_reranker:
        # configure reranker
        reranker = LLMRerank(
            choice_batch_size=5,
            top_n=reranker_top_n,
        )
        retrieved_nodes = reranker.postprocess_nodes(
            retrieved_nodes, query_bundle
        )

    return retrieved_nodes

def pretty_print(df):
    return display(HTML(df.to_html().replace("\\n", "")))


def visualize_retrieved_nodes(nodes) -> None:
    result_dicts = []
    for node in nodes:
        result_dict = {"Score": node.score, "Text": node.node.get_text()}
        result_dicts.append(result_dict)

    pretty_print(pd.DataFrame(result_dicts))

query_engine = index.as_chat_engine(
    similarity_top_k=5,
    node_postprocessors=[
        LLMRerank(
            choice_batch_size=5,
            top_n=3,
        )
    ],
    response_mode="tree_summarize",
)

@app.get("/")
def send_query_get_response(query_str):
    response = query_engine.query(query_str)
    if response.response == "Empty Response":
        response.response = "I'm sorry, I'm only a Large language model that answers questions about utilities ,and I don't have an answer for your question."
    return response.response

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)