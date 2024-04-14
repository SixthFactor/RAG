# Import necessary libraries
import databutton as db
import streamlit as st
import openai
from brain import get_index_for_pdf
from langchain.chains import RetrievalQA
# from langchain.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatOpenAI
import openai
import os

# Set the title for the Streamlit app
st.title("RAG enhanced Chatbot")

# Set up the OpenAI API key from databutton secrets
# os.environ["OPENAI_API_KEY"] = db.secrets.get("OPENAI_API_KEY")
# openai.api_key = db.secrets.get("OPENAI_API_KEY")

openai.api_key = st.secrets["api_key"]

# Cached function to create a vectordb for the provided PDF files
# @st.cache_data
@st.cache_resource   
def create_vectordb(files, filenames):
    # Show a spinner while creating the vectordb
    with st.spinner("Vector database"):
        vectordb = get_index_for_pdf(
            [file.getvalue() for file in files], filenames, openai.api_key
        ) 
    return vectordb


# Upload PDF files using Streamlit's file uploader
# pdf_files = st.file_uploader("", type="pdf", accept_multiple_files=True)
# Provide a meaningful label and use label_visibility if you wish to hide it visually
pdf_files = st.file_uploader("Upload PDF Files", type=["pdf", "docx"], accept_multiple_files=True, label_visibility="collapsed")

# If PDF files are uploaded, create the vectordb and store it in the session state
if pdf_files:
    pdf_file_names = [file.name for file in pdf_files]
    st.session_state["vectordb"] = create_vectordb(pdf_files, pdf_file_names)


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
Reply "Not applicable" if text is irrelevant.
Carefully focus on the metadata specially 'filename' and 'page' whenever answering.
"""

# Get the current prompt from the session state or set a default value
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
            st.write("You need to provide a PDF")
            st.stop()

    # Search the vectordb for similar content to the user's question
    search_results = vectordb.similarity_search(question, k=5)
    # search_results
    pdf_extract = "/n ".join([result.page_content for result in search_results])

    # Update the prompt with the pdf extract
    prompt[0] = {
        "role": "system",
        "content": prompt_template.format(pdf_extract=pdf_extract),
    }

    # Add the user's question to the prompt and display it
    prompt.append({"role": "user", "content": question})
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
    # prompt.append({"role": "assistant", "content": result})

    # Store the updated prompt in the session state
    st.session_state["prompt"] = prompt
    prompt.append({"role": "assistant", "content": result})

    # Store the updated prompt in the session state
    st.session_state["prompt"] = prompt
