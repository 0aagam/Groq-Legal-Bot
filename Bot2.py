import streamlit as st
import groq
from duckduckgo_search import DDGS
import os
from typing import List

# Initialize session state for API key
if "api_key" not in st.session_state:
    st.session_state.api_key = None
if "client" not in st.session_state:
    st.session_state.client = None

# API Key input section
with st.sidebar:
    st.markdown("### API Key Configuration")
    api_key_input = st.text_input("Enter your Groq API Key:", 
                                 type="password",
                                 help="Enter your Groq API key. It should start with 'gsk_'")
    
    if api_key_input:
        if api_key_input.startswith("gsk_"):
            if api_key_input != st.session_state.api_key:
                try:
                    # Test the API key by initializing the client
                    client = groq.Groq(
                        api_key=api_key_input,
                        timeout=60.0
                    )
                    st.session_state.client = client
                    st.session_state.api_key = api_key_input
                    st.success("API key successfully configured!")
                except Exception as e:
                    st.error("Invalid API key. Please check and try again.")
                    st.session_state.client = None
                    st.session_state.api_key = None
        else:
            st.error("API key should start with 'gsk_'. Please check your key.")

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
        Get response from Groq API with Indian legal expertise
        """
        try:
            system_prompt = """You are an experienced Indian legal advocate with extensive knowledge of Indian law and jurisprudence. 
            Your expertise includes:

            1. Constitutional Law:
               - Fundamental Rights (Articles 12-35)
               - Directive Principles
               - Constitutional Remedies
               - Supreme Court and High Court jurisdiction

            2. Criminal Law:
               - Indian Penal Code (IPC)
               - Criminal Procedure Code (CrPC)
               - Evidence Act
               - Criminal jurisprudence

            3. Civil Law:
               - Civil Procedure Code (CPC)
               - Contract Act
               - Transfer of Property Act
               - Specific Relief Act

            4. Family Law:
               - Hindu Marriage Act
               - Muslim Personal Law
               - Special Marriage Act
               - Hindu Succession Act
               - Hindu Adoption and Maintenance Act
               - Domestic Violence Act

            5. Corporate and Commercial Law:
               - Companies Act
               - GST Laws
               - Banking Regulations
               - SEBI Guidelines
               - IBC (Insolvency and Bankruptcy Code)

            6. Labor and Employment Laws:
               - Industrial Disputes Act
               - Factories Act
               - Employee Provident Fund
               - Payment of Wages Act

            7. Property Laws:
               - Real Estate (Regulation and Development) Act
               - Registration Act
               - Indian Easements Act

            8. Consumer Protection:
               - Consumer Protection Act, 2019
               - Product Liability
               - Unfair Trade Practices

            When responding:
            1. First identify the relevant area of law for the query
            2. Cite specific sections, acts, and landmark judgments when applicable
            3. Explain legal concepts in clear, simple language
            4. Provide practical steps or procedures when relevant
            5. Reference recent amendments or changes in the law
            6. Include relevant Supreme Court or High Court judgments
            7. Mention limitation periods or deadlines if applicable
            8. Explain the rights and obligations under the law

            Important Guidelines:
            - Begin responses with a clear identification of the legal issue
            - Use proper legal terminology while explaining in simple terms
            - Always mention relevant statutes and sections
            - Include limitation periods where applicable
            - Reference landmark cases that set precedents
            - Explain both rights and remedies
            - Mention jurisdiction and appropriate legal forum
            - Provide practical next steps when relevant

            Mandatory Disclaimer:
            "While I provide legal information based on Indian law, this should be treated as general guidance. For specific legal matters, please consult a practicing advocate who can review your case details personally."

            Use the provided search results to supplement your knowledge and provide up-to-date information."""

            chat_completion = st.session_state.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Search results: {context}\n\nQuestion: {prompt}"}
                ],
                model="mixtral-8x7b-32768",
                temperature=0.7,
                timeout=30.0,
            )
            return chat_completion.choices[0].message.content
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