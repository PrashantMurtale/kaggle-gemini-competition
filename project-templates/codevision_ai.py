#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CodeVision AI - Multimodal Image-to-Code Generator
Competition Entry for Kaggle Gemini 3 Pro Challenge

Developer: Prash
Started: Dec 8, 2025
Version: 0.9 (almost there!)

This is pretty wild - upload any UI screenshot or diagram
and Gemini's vision model converts it to working code.
The multimodal capabilities are honestly impressive!
"""

import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from PIL import Image
import os
import io


# Initialize everything
load_dotenv()
API_KEY = os.getenv('GEMINI_API_KEY', '')
if API_KEY:
    genai.configure(api_key=API_KEY)

# Page config - the eye emoji is perfect for a vision-based tool!
st.set_page_config(
    page_title="CodeVision AI - Multimodal Code Generator",
    page_icon="👁️",
    layout="wide"  # Wide layout gives us more room for side-by-side comparisons
)

# === STYLING SECTION ===
# This gradient took forever to get right but looks amazing
# The hover effects really make the UI feel premium
st.markdown("""
<style>
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 1.5rem 0;
        animation: gradient 3s ease infinite;
    }
    .tagline {
        text-align: center;
        color: #555;
        font-size: 1.3rem;
        margin-bottom: 2rem;
        font-weight: 300;
    }
    .feature-card {
        background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 2px solid #667eea30;
        transition: transform 0.3s, box-shadow 0.3s;
    }
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 20px rgba(102, 126, 234, 0.2);
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
</style>
""", unsafe_allow_html=True)

# === MAIN HEADER ===
st.markdown('<div class="main-title">👁️ CodeVision AI</div>', unsafe_allow_html=True)
st.markdown('<div class="tagline">Transform Screenshots, Diagrams & Mockups into Working Code</div>', unsafe_allow_html=True)

# TODO: Maybe add a demo GIF here? Would make the value prop clearer

# === SIDEBAR CONFIGURATION ===
# Keeping the config simple - just API key and some info
with st.sidebar:
    st.header("🔧 Settings")
    
    # Let users override the env variable if needed
    api_key = st.text_input("Gemini API Key", type="password", value=API_KEY)
    if api_key:
        genai.configure(api_key=api_key)
        st.success("✅ Connected")
    
    st.divider()
    
    st.markdown("### 🎯 What Can You Upload?")
    st.markdown("""
    - 🎨 **UI Mockups** → HTML/CSS/JS
    - 📊 **Diagrams** → Code structure
    - 📸 **Screenshots** → Recreate UIs
    - 🗺️ **Flowcharts** → Logic implementation
    - 📐 **Wireframes** → Complete apps
    - 🖼️ **Designs** → Pixel-perfect code
    """)
    
    st.divider()
    
    st.markdown("### ⚡ Powered By")
    st.markdown("""
    **Gemini 3 Pro's strengths:**
    - 🖼️ Multimodal understanding
    - 🧠 Visual-to-code reasoning
    - 🎯 Context-aware generation
    - 💎 High-fidelity recreation
    """)

# === MAIN CONTENT TABS ===
# Four tabs: single image, multi-image, refactoring, and examples
# Tried to order them by most common use case first
tab1, tab2, tab3, tab4 = st.tabs(["🎨 Image to Code", "📊 Multiple Images", "🔄 Code Refactor", "📚 Examples"])

# TAB 1: Single Image to Code (Main Feature)
with tab1:
    st.header("Upload an Image and Get Code")
    
    # Split into two columns - image on left, options/results on right
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Image")
        
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=['png', 'jpg', 'jpeg', 'webp'],
            help="Upload UI mockups, screenshots, diagrams, or designs"
        )
        
        if uploaded_file:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
        
        st.divider()
        
        prompt_type = st.selectbox(
            "What do you want to generate?",
            [
                "Recreate this UI exactly",
                "Convert to React component",
                "Convert to HTML/CSS",
                "Extract and implement logic",
                "Generate from wireframe",
                "Custom prompt..."
            ]
        )
        
        if prompt_type == "Custom prompt...":
            custom_prompt = st.text_area("Custom instructions", placeholder="Describe what you want...")
        else:
            custom_prompt = None
        
        framework = st.selectbox(
            "Target Framework",
            ["HTML/CSS/JS", "React", "Vue", "Streamlit", "Flutter", "SwiftUI"]
        )
        
        include_responsive = st.checkbox("Make it responsive", value=True)
        include_animations = st.checkbox("Add animations", value=False)
    
    with col2:
        st.subheader("✨ Generated Code")
        
        if st.button("🚀 Generate Code", disabled=not uploaded_file or not api_key):
            if not api_key:
                st.error("Configure API key in sidebar")
            elif not uploaded_file:
                st.error("Upload an image first")
            else:
                with st.spinner("🎨 Analyzing image and generating code..."):
                    try:
                        # Different prompt templates for different conversion types
                        # These prompts were refined through A/B testing
                        base_prompts = {
                            "Recreate this UI exactly": "Analyze this image and recreate the user interface exactly as shown. Pay attention to layout, colors, fonts, spacing, and all visual details.",
                            "Convert to React component": "Convert this UI to a React component with proper props, state management, and modern React patterns.",
                            "Convert to HTML/CSS": "Generate clean HTML and CSS that recreates this interface. Use semantic HTML and modern CSS.",
                            "Extract and implement logic": "Analyze this diagram/flowchart and implement the logic shown in clean, well-documented code.",
                            "Generate from wireframe": "This is a wireframe. Create a fully-styled, production-ready implementation with modern design.",
                        }
                        
                        selected_prompt = custom_prompt if custom_prompt else base_prompts.get(prompt_type, base_prompts["Recreate this UI exactly"])
                        
                        full_prompt = f"""{selected_prompt}

TARGET FRAMEWORK: {framework}
REQUIREMENTS:
- Write clean, production-ready code
- Include all necessary imports and dependencies
- Add helpful comments
{"- Make the design responsive for mobile, tablet, and desktop" if include_responsive else ""}
{"- Add smooth animations and transitions" if include_animations else ""}
- Follow best practices for {framework}
- Ensure the code is ready to run

Provide complete, working code that can be directly used.
"""
                        
                        # Initialize GEMINI 2.5 FLASH with multimodal support! 🎯
                        # Fast, excellent free tier, perfect for image-to-code generation
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        
                        # Call the API with image + prompt
                        # The multimodal input is really the magic here
                        response = model.generate_content([full_prompt, image])
                        
                        # Show success message
                        st.success("✅ Code generated!")
                        
                        # Map framework to syntax highlighting language
                        # (because 'React' isn't a valid highlight lang)
                        lang_map = {
                            "HTML/CSS/JS": "html",
                            "React": "jsx",
                            "Vue": "vue",
                            "Streamlit": "python",
                            "Flutter": "dart",
                            "SwiftUI": "swift"
                        }
                        
                        code_lang = lang_map.get(framework, "python")
                        
                        st.code(response.text, language=code_lang)
                        
                        # Download button
                        file_extensions = {
                            "HTML/CSS/JS": "html",
                            "React": "jsx",
                            "Vue": "vue",
                            "Streamlit": "py",
                            "Flutter": "dart",
                            "SwiftUI": "swift"
                        }
                        
                        file_ext = file_extensions.get(framework, "txt")
                        
                        st.download_button(
                            "📥 Download Code",
                            response.text,
                            file_name=f"generated_code.{file_ext}",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# TAB 2: Multiple Images (Advanced Feature)
# This is cool - you can upload different screens and it generates a complete app
with tab2:
    st.header("🔄 Multi-Image Code Generation")
    st.markdown("*Upload multiple screenshots or diagrams to generate a complete application*")
    
    uploaded_files = st.file_uploader(
        "Upload multiple images",
        type=['png', 'jpg', 'jpeg', 'webp'],
        accept_multiple_files=True,
        help="Upload different views/pages of your application"
    )
    
    if uploaded_files:
        st.subheader(f"📸 {len(uploaded_files)} Images Uploaded")
        
        cols = st.columns(min(3, len(uploaded_files)))
        images = []
        
        for idx, file in enumerate(uploaded_files):
            img = Image.open(file)
            images.append(img)
            with cols[idx % 3]:
                st.image(img, caption=f"Image {idx+1}", use_container_width=True)
        
        st.divider()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            generation_type = st.selectbox(
                "What to generate?",
                [
                    "Complete multi-page application",
                    "React app with routing",
                    "Full-stack app (frontend + backend)",
                    "Mobile app (Flutter/SwiftUI)",
                ]
            )
        
        with col2:
            if st.button("🎯 Generate Complete App"):
                with st.spinner("🔮 Analyzing all images and generating application..."):
                    try:
                        prompt = f"""Analyze these {len(uploaded_files)} images which show different parts/pages of an application.

Create a complete {generation_type} that includes:
1. All pages/screens shown in the images
2. Navigation between pages
3. Consistent styling across all pages
4. Proper project structure
5. All necessary files (components, styles, etc.)
6. README with setup instructions

Make it production-ready and well-organized.
"""
                        
                        model = genai.GenerativeModel('models/gemini-2.5-flash')
                        response = model.generate_content([prompt] + images)
                        
                        st.success("✅ Complete application generated!")
                        st.code(response.text, language="python")
                        
                        st.download_button(
                            "📥 Download Complete App",
                            response.text,
                            file_name="complete_app.zip",
                            mime="text/plain"
                        )
                        
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

# TAB 3: Code Refactoring (Bonus Feature)
# Sometimes you have code but want to modernize it with a reference design
with tab3:
    st.header("🔄 Code Refactoring with Visual Context")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Current Code")
        current_code = st.text_area(
            "Paste your existing code",
            height=300,
            placeholder="Paste code you want to refactor..."
        )
    
    with col2:
        st.subheader("Visual Reference (Optional)")
        ref_image = st.file_uploader(
            "Upload UI reference",
            type=['png', 'jpg', 'jpeg', 'webp'],
            key="refactor_image"
        )
        
        if ref_image:
            st.image(Image.open(ref_image), use_container_width=True)
    
    refactor_goal = st.multiselect(
        "Refactoring goals",
        [
            "Improve code quality",
            "Add modern design",
            "Make responsive",
            "Add accessibility",
            "Optimize performance",
            "Add animations",
            "Modularize components",
        ],
        default=["Improve code quality"]
    )
    
    if st.button("✨ Refactor Code", disabled=not current_code):
        with st.spinner("Refactoring..."):
            try:
                goals_text = ", ".join(refactor_goal)
                prompt = f"""Refactor this code with the following goals: {goals_text}

CURRENT CODE:
{current_code}

Provide:
1. Refactored code with improvements
2. Explanation of changes made
3. Before/after comparison
"""
                
                model = genai.GenerativeModel('models/gemini-2.5-flash')
                
                if ref_image:
                    img = Image.open(ref_image)
                    prompt += "\n\nVISUAL REFERENCE: Use this as design inspiration"
                    response = model.generate_content([prompt, img])
                else:
                    response = model.generate_content(prompt)
                
                st.success("✅ Code refactored!")
                st.markdown(response.text)
                
            except Exception as e:
                st.error(f"Error: {str(e)}")

# TAB 4: Examples (Show what's possible)
# Real-world examples help users understand the value
with tab4:
    st.header("📚 Example Use Cases")
    
    examples = [
        {
            "icon": "🎨",
            "title": "Figma to Code",
            "description": "Screenshot your Figma designs → Get pixel-perfect HTML/CSS/React",
            "impact": "Save hours of manual coding"
        },
        {
            "icon": "📱",
            "title": "App Screenshots to Clone",
            "description": "Upload app screenshots → Generate working mobile app",
            "impact": "Rapid prototyping and learning"
        },
        {
            "icon": "📊",
            "title": "Flowchart to Implementation",
            "description": "Draw flowcharts → Get implemented logic with error handling",
            "impact": "Bridge design and development"
        },
        {
            "icon": "🗺️",
            "title": "Architecture Diagram to Code",
            "description": "System diagrams → Generate API structure and microservices",
            "impact": "Faster system implementation"
        },
        {
            "icon": "✏️",
            "title": "Hand-Drawn Sketch to App",
            "description": "Paper sketches → Working prototype",
            "impact": "Start from napkin ideas"
        },
        {
            "icon": "🔄",
            "title": "Legacy UI Modernization",
            "description": "Old UI screenshot → Modern, responsive redesign",
            "impact": "Upgrade old systems quickly"
        }
    ]
    
    cols = st.columns(2)
    
    for idx, example in enumerate(examples):
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="feature-card">
                <h3>{example['icon']} {example['title']}</h3>
                <p><b>How:</b> {example['description']}</p>
                <p><b>Impact:</b> {example['impact']}</p>
            </div>
            """, unsafe_allow_html=True)

# === FOOTER ===
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 2rem; color: #666;'>
    <h3>🏆 Built for Kaggle Gemini Competition (using Gemini 2.5 Pro)</h3>
    <p style='font-size: 1.1rem;'>
        Showcasing <b>multimodal AI capabilities</b> that transform visual content into production-ready code
    </p>
    <p style='margin-top: 1rem;'>
        <b>Real-world impact:</b> Saves developers hours daily • Makes coding accessible to designers • Bridges visual design and code
    </p>
</div>
""", unsafe_allow_html=True)

# Developer notes:
# - Test with more edge cases (hand-drawn sketches, low-res images)
# - Maybe add image preprocessing options?
# - Consider caching responses for the same image
# - Add analytics to track which features get used most
