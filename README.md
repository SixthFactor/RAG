link: https://h6jjzbhp2kjhb9azpqc2pu.streamlit.app/

RAG-enhanced Chatbot: Ask Your Documents Anything
[Badges (Optional)]
(Add badges from platforms like Travis CI, Coveralls, etc. if applicable)
Description:
This project implements a RAG-enhanced chatbot that allows users to ask questions based on the content of uploaded PDF documents. By leveraging the power of language models and vector databases, the chatbot can efficiently retrieve relevant information and provide insightful answers.
Installation:
Clone the repository:
git clone https://github.com/your-username/your-repository.git
Use code with caution.
Bash
Install the required dependencies:
pip install -r requirements.txt
Use code with caution.
Bash
Set your OpenAI API key as a Streamlit secret:
streamlit config set secrets.api_key YOUR_API_KEY
Use code with caution.
Bash
Usage:
Run the Streamlit application:
streamlit run app.py
Use code with caution.
Bash
Upload one or more PDF documents.
Ask a question in the chat interface.
The chatbot will provide an answer based on the content of the uploaded documents.
How it works:
PDF Processing: Uploaded PDFs are parsed and converted into text chunks. Each chunk is then embedded into a vector space using OpenAI's embedding model.
Vector Database: A FAISS vector database stores the embedded text chunks, allowing for efficient similarity search.
Chatbot Interaction: When a user asks a question, the chatbot searches the vector database for the most relevant text chunks. These chunks are then used as context for a prompt sent to ChatGPT.
Response Generation: ChatGPT generates a response based on the user's question and the retrieved context, providing insightful answers based on the uploaded documents.
Functionality Breakdown:
requirements.txt: Lists the required Python libraries and their versions.
brain.py: Contains functions for processing PDFs, creating document chunks, and building the vector database.
app.py: Builds the Streamlit application, handles user interaction, and displays the chat interface.
Potential Enhancements:
User authentication and personalized experiences.
Support for other document formats like text files or Word documents.
Improved user interface with interactive elements and visualizations.
Refine the prompt template for better control over response generation.
Contributing:
Contributions are welcome! Please feel free to submit pull requests or open issues for bug reports and feature requests.
License:
(Specify the license for your project)
