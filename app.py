# Import necessary libraries
import databutton as db
import streamlit as st
import openai
from brain import get_index_for_pdf
from langchain.chains import RetrievalQA
from langchain_community.chat_models import ChatOpenAI  # For chat models
import os

# Set the title for the Streamlit app
st.title("RAG enhanced Chatbot")

#if you want to use api_key directly
# openai.api_key = "api_key"

# Set up the OpenAI API key (API key is set in streamlit secrate)
openai.api_key = st.secrets["api_key"]

# Cached function to create a vectordb for the provided PDF and DOCX files
@st.cache_resource   
def create_vectordb(files, filenames):
    """
    Creates a vector database from the uploaded files.
    Args:
        files (List[BytesIO]): A list of uploaded files as byte streams.
        filenames (List[str]): A list of corresponding filenames.
    Returns:
        FAISS: The created FAISS vector index.
    """
    with st.spinner("Creating vector database..."):
        vectordb = get_index_for_pdf(
            [file.getvalue() for file in files], filenames, openai.api_key
        ) 
    return vectordb


# Upload PDF and DOCX files (collapsed for cleaner UI)
pdf_files = st.file_uploader("Upload PDF Files", type=["pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed")

# Create the vector database if files are uploaded
if pdf_files:
    pdf_file_names = [file.name for file in pdf_files]
    st.session_state["vectordb"] = create_vectordb(pdf_files, pdf_file_names)


# Define the prompt template for the LLM
prompt_template = """
You are an expert market researcher with 20 years of experience. For the last 10 years you have been doing research in the middle east region to understand consumer sentiment. 

You are a post graduate in psycology and have done your doctorate in emotions and culture. 
You  have an in depth understanding of consumer language culture and geography of the middle east. 
Please act as SixthFactor the consumer sentiment expert  bot and using the consumer comments we have captured please answer any questions with as much detail as possible.  
Please use the data in the attached files from 4 groups and 6 in depth interviews conducted in UAE The files labeled IDI are one on one in depth interviews and the files labeled Groups are focus group discussions. 
The groups were conducted among expat arabs and Nationals.  Please provide supporting quotes to the consumer group based on the file you use to answer the information. 
When providing the consumer quotes please label them with appropriate labels based on the file name you pick up. 
Please refer to all the files for information when you answer to the query. Please be professional and courteous when answering these queries.
The PDF content is:
{pdf_extract}

Carefully focus on the metadata specially 'filename' and 'page' whenever answering.
"""

# Get the current prompt from the session state or set a default
prompt = st.session_state.get("prompt", [{"role": "system", "content": "none"}])

# Display previous chat messages
for message in prompt:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# Get the user's question using Streamlit's chat input
question = st.chat_input("Ask anything")

# Handle the user's question
if question:
    vectordb = st.session_state.get("vectordb", None)
    if not vectordb:
        with st.chat_message("assistant"):
            st.write("You need to provide a PDF or DOCX file first.")
            st.stop()

    # Search the vectordb for similar content to the user's question
    search_results = vectordb.similarity_search(question, k=5)
    pdf_extract = "/n ".join([result.page_content for result in search_results])

    # Update the prompt with the pdf extract and user question
    prompt[0] = {
        "role": "system",
        "content": prompt_template.format(pdf_extract=pdf_extract),
    }
    prompt.append({"role": "user", "content": question})

    # Display the user's question
    with st.chat_message("user"):
        st.write(question)

    # Display an empty assistant message while waiting for the response
    with st.chat_message("assistant"):
        botmsg = st.empty()

    # Call ChatGPT with streaming and display the response as it comes
    response = []
    result = "" 
    for chunk in openai.chat.completions.create(
        model="gpt-4-turbo", messages=prompt, stream=True
    ):
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            text = chunk.choices[0].delta.content
            response.append(text)
            result = ''.join(response).strip()
            botmsg.write(result)

    # Add the assistant's response to the prompt
    prompt.append({"role": "assistant", "content": result})

    # Store the updated prompt in the session state
    st.session_state["prompt"] = prompt
