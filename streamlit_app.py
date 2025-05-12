import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit.components.v1 import html
import json
from calendar import monthrange
import os

# Custom CSS and JavaScript with enhanced effects
def inject_custom_style():
    # استخدام مسار نسبي للصورة مع raw string (r قبل المسار)
    image_path = os.path.join("assets", "world1.jpg")
    
    st.markdown(f"""
    <style>
        .stApp {{
            background: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8)), 
                        url('{image_path}');
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}
        
        /* بقية أنماط CSS ... */
        .card {{
            transition: all 0.4s ease;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(0, 0, 0, 0.1);
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }}
        
        /* بقية الأنماط تبقى كما هي */
    </style>
    """, unsafe_allow_html=True)
    
    # بقية كود الجافاسكريبت يبقى كما هو
    html("""
    <script>
    // كود الجسيمات والمؤثرات يبقى كما هو
    </script>
    """)

# ... (بقية الكود يبقى كما هو بدون تغيير)
