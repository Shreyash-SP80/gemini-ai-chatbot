
import streamlit as st
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Page configuration
st.set_page_config(
    page_title="Gemini AI Assistant",
    page_icon="🤖",
    layout="wide"
)

def load_api_key():
  
    env_path = Path('.') / '.env'
    load_dotenv(env_path)
    
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        st.error("""
        ❌ Error: GOOGLE_API_KEY not found. 
        
        Please create a `.env` file in your project directory with:
        ```
        GOOGLE_API_KEY=your_actual_api_key_here
        ```
        """)
        st.stop()

    return api_key

def build_agent(api_key: str):
    """Initialize the Gemini chat model and agent executor."""
    model = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",  
        temperature=0,
        google_api_key=api_key
    )
    tools = []  
    return create_react_agent(model, tools)

def main():
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Settings")
        st.markdown("---")
        st.subheader("About")
        st.markdown("""
        This is a Gemini-powered AI assistant built with:
        - **Streamlit** for the UI
        - **LangGraph** for agent orchestration
        - **Google Gemini** as the AI model
        """)
        
        st.subheader("Instructions")
        st.markdown("""
        1. Type your message in the chat box
        2. Press Enter or click Send
        3. The assistant will respond in real-time
        4. Use 'Clear Chat' to start over
        """)
        
        if st.button("🔄 Clear Chat"):
            st.session_state.messages = []
            st.rerun()

    # Main content area
    st.title("🤖 Gemini AI Assistant")
    st.markdown("---")
    
   
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    # Initialize agent
    if "agent" not in st.session_state:
        with st.spinner("🔄 Initializing AI agent..."):
            try:
                api_key = load_api_key()
                st.session_state.agent = build_agent(api_key)
            except Exception as e:
                st.error(f"Failed to initialize agent: {e}")
                st.stop()
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                # Stream the response
                for chunk in st.session_state.agent.stream(
                    {"messages": [HumanMessage(content=prompt)]}
                ):
                    if "agent" in chunk and "messages" in chunk["agent"]:
                        for message in chunk["agent"]["messages"]:
                            full_response += message.content
                            message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
                
            except Exception as e:
                full_response = f"❌ Error: {str(e)}"
                message_placeholder.markdown(full_response)
        
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": full_response})

if __name__ == "__main__":
    main()

# CLI =>

# from langchain_core.messages import HumanMessage
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langgraph.prebuilt import create_react_agent
# from dotenv import load_dotenv
# import os
# import sys

# def load_api_key():
#     """Load Gemini API key from .env file."""
#     load_dotenv()
#     api_key = os.getenv("GOOGLE_API_KEY")

#     if not api_key:
#         sys.exit("❌ Error: GOOGLE_API_KEY not found in .env file")

#     return api_key


# def build_agent(api_key: str):
#     """Initialize the Gemini chat model and agent executor."""
#     model = ChatGoogleGenerativeAI(
#         model="gemini-1.5-flash",  
#         temperature=0,
#         google_api_key=api_key
#     )

#     tools = []  
#     return create_react_agent(model, tools)


# def run_chat(agent_executor):
#     """Run interactive chat loop with the AI assistant."""
#     print("\nWelcome! I'm your Gemini-powered AI assistant.")
#     print("Type 'quit' anytime to exit.\n")

#     while True:
#         try:
#             user_input = input("You: ").strip()

#             if user_input.lower() in {"quit", "exit"}:
#                 print("👋 Goodbye!")
#                 break

          
#             print("Assistant: Typing...", end="\r", flush=True)

#             response_started = False
#             for chunk in agent_executor.stream(
#                 {"messages": [HumanMessage(content=user_input)]}
#             ):
#                 if not response_started:
#                     print("Assistant: ", end="", flush=True)
#                     response_started = True

#                 if "agent" in chunk and "messages" in chunk["agent"]:
#                     for message in chunk["agent"]["messages"]:
#                         print(message.content, end="", flush=True)

#             print()  
#         except KeyboardInterrupt:
#             print("\n\n🛑 Interrupted by user. Exiting...")
#             break
#         except Exception as e:
#             print(f"\n⚠️ Error: {e}")


# def main():
#     api_key = load_api_key()
#     agent_executor = build_agent(api_key)
#     run_chat(agent_executor)


# if __name__ == "__main__":
#     main()
