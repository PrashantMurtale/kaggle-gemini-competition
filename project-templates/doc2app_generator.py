#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Doc2App - Documentation to Application Generator
Built for Kaggle Gemini 3 Pro Competition

Author: Prashanth
Created: Dec 2025
Last Modified: Dec 9, 2025

This app leverages Gemini 3's huge context window to convert
API docs into actual working code. Pretty cool stuff!
"""

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import time

# Load environment variables first thing
load_dotenv()

# Configure Gemini API - had to do this early or get weird errors
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# TODO: Maybe add more page config options later?
st.set_page_config(
    page_title="Doc2App - AI Application Generator",
    page_icon="🚀",
    layout="wide"  # wide layout works better for code display
)

# CSS Styling - spent way too much time on this gradient lol
# But it looks nice so worth it!
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        text-align: center;
        color: #666;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background: linear-gradient(120deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem;
        font-size: 1.1rem;
        font-weight: bold;
        border-radius: 8px;
        transition: transform 0.2s;
    }
    .stButton>button:hover {
        transform: scale(1.02);
    }
    .feature-box {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Main header section
st.markdown('<div class="main-header">🚀 Doc2App</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Transform API Documentation into Working Applications with Gemini 3 Pro</div>', unsafe_allow_html=True)

# Sidebar for configuration - keeping it simple
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # API key input - can override env variable
    api_key = st.text_input(
        "Gemini API Key", 
        type="password", 
        value=GEMINI_API_KEY
    )
    
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ API Key configured")
    else:
        st.warning("⚠️ Please enter your Gemini API key")
    
    st.divider()
    
    # About section
    st.header("📊 About")
    st.markdown("""
    **Doc2App** leverages Gemini 2.5 Pro's:
    - 🧠 1M token context window
    - 🤖 Agentic code generation
    - 🎯 Full-stack capabilities
    
    **Perfect for:**
    - API integration projects
    - Boilerplate generation
    - Learning new frameworks
    """)

# Main content area - using tabs for better organization
tab1, tab2, tab3 = st.tabs(["📝 Generate App", "🎯 Examples", "📚 How It Works"])

# TAB 1: Main generation interface
with tab1:
    st.header("Generate Your Application")
    
    # Using columns for better layout (2:1 ratio works well)
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main input area - this is where the magic happens
        documentation = st.text_area(
            "Paste API Documentation or Requirements",
            height=300,
            placeholder="Paste complete API documentation, OpenAPI spec, or detailed requirements here...\n\nGemini 3 Pro can process up to 1 million tokens!",
            help="The more detailed your documentation, the better the generated app!"
        )
    
    with col2:
        st.markdown("### 📋 Options")
        
        # Framework selection - might add more later
        app_type = st.selectbox(
            "Application Type",
            ["Web App (Streamlit)", "REST API (FastAPI)", "CLI Tool", "Full Stack (React + FastAPI)"]
        )
        
        # Feature toggles
        include_tests = st.checkbox("Include Tests", value=True)
        include_docs = st.checkbox("Include Documentation", value=True)
        include_error_handling = st.checkbox("Error Handling", value=True)
        
        st.divider()
        
        # Complexity slider - affects prompt detail
        complexity = st.slider("Complexity Level", 1, 5, 3)
    
    # Generate button - disabled if no API key or docs
    if st.button("🚀 Generate Application", disabled=not api_key or not documentation):
        if not api_key:
            st.error("Please configure your Gemini API key in the sidebar")
        elif not documentation:
            st.error("Please provide documentation or requirements")
        else:
            # Show spinner while processing
            with st.spinner("✨ Gemini 3 Pro is analyzing and generating your application..."):
                try:
                    # Build the prompt - this took some iteration to get right
                    prompt = f"""You are an expert full-stack developer. Analyze the following documentation and generate a complete, production-ready application.

DOCUMENTATION:
{documentation}

REQUIREMENTS:
- Application Type: {app_type}
- Include comprehensive tests: {include_tests}
- Include detailed documentation: {include_docs}
- Include robust error handling: {include_error_handling}
- Complexity Level: {complexity}/5

Generate a complete application with:
1. Well-structured, clean code
2. Proper file organization
3. Requirements/dependencies file
4. README with setup instructions
5. Example usage
6. Comments explaining key logic

Make it production-ready, following best practices for the chosen framework.
Provide the complete code for each file clearly labeled.
"""
                    
                    # Initialize the model
                    # Using GEMINI 2.5 FLASH - Fast and excellent free tier quotas! 🎯
                    # Perfect for development and has great code generation capabilities
                    model = genai.GenerativeModel(
                        'models/gemini-2.5-flash',
                        system_instruction="You are an expert software developer who creates production-ready, well-documented code. Focus on quality, best practices, and user experience."
                    )
                    
                    # Generate the code
                    # Temperature at 0.7 gives good balance between creativity and consistency
                    response = model.generate_content(
                        prompt,
                        generation_config={
                            'temperature': 0.7,
                            'max_output_tokens': 8192,
                        }
                    )
                    
                    # Display the results
                    st.success("✅ Application generated successfully!")
                    
                    st.markdown("### 📦 Generated Application")
                    st.code(response.text, language="python")
                    
                    # Download functionality - super useful
                    st.download_button(
                        label="📥 Download Generated Code",
                        data=response.text,
                        file_name="generated_app.py",
                        mime="text/plain"
                    )
                    
                    st.markdown("---")
                    st.info("💡 **Next Steps:** Copy the code, set up your environment, and run the application!")
                    
                except Exception as e:
                    # Error handling - catching everything for now
                    st.error(f"❌ Error: {str(e)}")
                    st.info("Try with a smaller input or check your API key")

# TAB 2: Example use cases
with tab2:
    st.header("💡 Example Use Cases")
    
    # Pre-built examples - makes it easier for users to get started
    examples = [
        {
            "title": "🌐 Weather API Integration",
            "description": "Generate a web app that integrates with OpenWeatherMap API",
            "doc": "OpenWeatherMap API documentation:\n- Base URL: https://api.openweathermap.org/data/2.5/\n- Endpoint: /weather\n- Parameters: q (city name), appid (API key)\n- Response: JSON with temp, humidity, description"
        },
        {
            "title": "💳 Payment Processing",
            "description": "Create a Stripe payment integration",
            "doc": "Stripe API for payment processing:\n- Create payment intent\n- Confirm payment\n- Handle webhooks for payment status\n- Required: secret key, publishable key"
        },
        {
            "title": "📊 Data Dashboard",
            "description": "Build an analytics dashboard with charts",
            "doc": "Requirements:\n- Display data from CSV/API\n- Interactive charts (line, bar, pie)\n- Filtering and date range selection\n- Export functionality"
        }
    ]
    
    # Display examples in expanders
    for i, example in enumerate(examples):
        with st.expander(f"{example['title']}"):
            st.markdown(f"**{example['description']}**")
            st.code(example['doc'], language="text")
            
            # Quick load button - tried session state but keeping it simple for now
            if st.button(f"Use This Example", key=f"example_{i}"):
                st.session_state.example_doc = example['doc']
                st.info("Example loaded! Go to 'Generate App' tab")

# TAB 3: Info/documentation
with tab3:
    st.header("🔍 How It Works")
    
    st.markdown("""
    ### The Magic Behind Doc2App
    
    <div class="feature-box">
    <b>1️⃣ Massive Context Understanding</b><br>
    Gemini 3 Pro's 1M token context window can process entire API documentation, unlike traditional models that can only handle small snippets.
    </div>
    
    <div class="feature-box">
    <b>2️⃣ Agentic Code Generation</b><br>
    The model doesn't just output code - it plans, structures, and organizes a complete application with best practices.
    </div>
    
    <div class="feature-box">
    <b>3️⃣ Full-Stack Awareness</b><br>
    Understands relationships between frontend, backend, database, and deployment - generating coherent multi-file projects.
    </div>
    
    <div class="feature-box">
    <b>4️⃣ Production-Ready Output</b><br>
    Includes error handling, tests, documentation, and follows industry best practices automatically.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✅ Best Practices")
        st.markdown("""
        - Provide complete documentation
        - Be specific about requirements
        - Include example API responses
        - Mention edge cases
        - Specify preferred libraries
        """)
    
    with col2:
        st.markdown("### 🎯 Perfect For")
        st.markdown("""
        - API integration projects
        - Learning new frameworks
        - Rapid prototyping
        - Code modernization
        - Documentation validation
        """)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <b>Built with Gemini 2.5 Pro</b> for Kaggle Competition 🏆<br>
    Showcasing the power of massive context windows and agentic AI
</div>
""", unsafe_allow_html=True)

# Note to self: Test with different API docs tomorrow
# Also maybe add caching for responses? Could save API calls
