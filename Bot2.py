import streamlit as st
import groq
from duckduckgo_search import DDGS
import os
from typing import List
from dotenv import load_dotenv
from groq.types import ChatCompletion

# Load environment variables
load_dotenv()

# Initialize session state for API key
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "client" not in st.session_state:
    st.session_state.client = None

# API Key input section
with st.sidebar:
    st.markdown("### API Key Configuration")
    api_key_input = st.text_input(
        "Enter your Groq API Key:", 
        type="password",
        help="Enter your Groq API key. It should start with 'gsk_'"
    )
    
    if api_key_input:
        if api_key_input.startswith("gsk_"):
            if api_key_input != st.session_state.api_key:
                try:
                    # Test the API key by initializing the client
                    client = groq.Client(api_key=api_key_input)
                    # Verify the API key works by making a small test request
                    test_response = client.chat.completions.create(
                        messages=[{"role": "user", "content": "test"}],
                        model="mixtral-8x7b-32768",
                        temperature=0.7,
                        max_tokens=10
                    )
                    st.session_state.client = client
                    st.session_state.api_key = api_key_input
                    st.success("API key successfully configured!")
                except Exception as e:
                    if "authentication" in str(e).lower():
                        st.error("Authentication failed. Please check your API key.")
                    else:
                        st.error(f"Error: {str(e)}")
                    st.session_state.client = None
                    st.session_state.api_key = None
        else:
            st.error("API key should start with 'gsk_'. Please check your key.")
            st.info("You can find your API key in your Groq dashboard: https://console.groq.com/keys")

# Only show the main interface if API key is configured
if st.session_state.client:
    def search_duckduckgo(query: str, num_results: int = 3) -> List[str]:
        """
        Search DuckDuckGo and return results
        """
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=num_results))
                return [f"{r['title']}: {r['link']}\n{r['body']}" for r in results]
        except Exception as e:
            return [f"Error performing search: {str(e)}"]

    def get_groq_response(prompt: str, context: str = "") -> str:
        """
        Get response from Groq API with Indian legal context
        """
        try:
            system_prompt = """You are an Indian legal assistant with expertise in Indian law. 
            Your role is to:
            1. Provide accurate information about Indian laws, regulations, and legal procedures
            2. Explain legal concepts in simple terms
            3. Reference relevant sections of Indian laws and court judgments when applicable
            4. Clarify that you're providing general information, not legal advice
            5. Suggest consulting a qualified lawyer for specific legal matters
            
            Use the provided search results to answer questions accurately."""

            completion: ChatCompletion = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Search results: {context}\n\nQuestion: {prompt}"}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error getting response: {str(e)}"

    # Streamlit UI
    st.title("⚖️ Indian Legal Assistant")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask your legal question about Indian law..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Search DuckDuckGo
        with st.spinner("Researching Indian legal sources..."):
            search_results = search_duckduckgo(prompt)
            search_context = "\n\n".join(search_results)

        # Get Groq response
        with st.chat_message("assistant"):
            with st.spinner("Analyzing legal information..."):
                response = get_groq_response(prompt, search_context)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

    # Add sidebar with info and disclaimers
    with st.sidebar:
        st.markdown("""
        ### Indian Legal Advocate Assistant
        This AI-powered legal assistant is equipped with comprehensive knowledge of:

        📜 **Core Laws**
        - Constitutional Law
        - Criminal Law (IPC, CrPC)
        - Civil Law (CPC)
        - Family Law
        
        💼 **Business Laws**
        - Corporate Law
        - Tax Laws
        - Banking Laws
        - SEBI Regulations
        
        👥 **Personal Laws**
        - Property Laws
        - Family Laws
        - Succession Laws
        - Consumer Rights
        
        👷 **Special Laws**
        - Labor Laws
        - Environmental Laws
        - Cyber Laws
        - Intellectual Property Rights

        ### How to Use
        1. Ask specific legal questions
        2. Mention relevant details
        3. Specify the jurisdiction if applicable
        4. Ask for relevant case laws if needed
        
        ### Important Disclaimer
        This assistant provides:
        - General legal information
        - References to relevant laws
        - Citations of important cases
        - Procedural guidance
        
        ⚠️ **Please Note:**
        While this assistant has extensive legal knowledge, it should not replace professional legal counsel. For specific legal matters, please consult a practicing advocate.
        """)
else:
    st.title("⚖️ Indian Legal Assistant")
    st.warning("Please enter your Groq API key in the sidebar to start using the assistant.")
    st.markdown("""
    ### How to get a Groq API key:
    1. Visit [Groq's website](https://groq.com)
    2. Sign up for an account
    3. Navigate to your API settings
    4. Generate a new API key
    5. Copy and paste the key here
    
    Your API key will be stored only for this session and will need to be entered again if you refresh the page.
    """) 