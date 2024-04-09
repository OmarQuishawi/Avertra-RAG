"""This script is just a POC that uses streamlit to create a web app 
that uses the RAG system to get answers from a given query."""

import streamlit as st
from utility_RAG import send_query_get_response

st.title("Utility RAG")
st.write("This is a POC that uses the RAG system to get answers from a given query.")

query_str = st.text_input("Enter your query here:")
if st.button("Get Response"):
    response = send_query_get_response(query_str)
    st.write(response)

# To run this script, you need to install streamlit:
# pip install streamlit

# Then run the script:
# streamlit run app.py