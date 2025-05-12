import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit.components.v1 import html
from calendar import monthrange

def inject_custom_style():
    st.markdown("""
    <style>
        :root {
            --primary-color: #4CAF50;
            --secondary-color: #2196F3;
            --background-gradient: linear-gradient(135deg, #1a1a1a, #2d4059, #4CAF50);
        }
        
        .stApp {
            background: var(--background-gradient);
            background-size: 300% 300%;
            animation: gradient 30s ease infinite;
            min-height: 100vh;
            height: 100%;
        }
        
        .auto-moving-triangle {
            position: fixed;
            width: 150px;
            height: 150px;
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            background: rgba(76, 175, 80, 0.3);
            animation: autoMove 8s infinite linear;
            z-index: 9997;
            pointer-events: none;
        }
        
        @keyframes autoMove {
            0% { transform: translate(10vw, 10vh) rotate(0deg); }
            25% { transform: translate(80vw, 30vh) rotate(90deg); }
            50% { transform: translate(70vw, 70vh) rotate(180deg); }
            75% { transform: translate(20vw, 80vh) rotate(270deg); }
            100% { transform: translate(10vw, 10vh) rotate(360deg); }
        }
    </style>
    """, unsafe_allow_html=True)
    
    html("""
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <div id="particles-js" style="position:fixed;top:0;left:0;z-index:9998;"></div>
    <div class="auto-moving-triangle"></div>
    <script>
    let lastX = 0;
    let lastY = 0;
    let particleTimeout;
    
    particlesJS('particles-js', {
        particles: {
            number: { value: 40, density: { enable: true, value_area: 400 } },
            color: { value: "#4CAF50" },
            shape: { type: "circle" },
            opacity: { value: 0.7, random: true },
            size: { value: 3, random: true },
            move: {
                enable: true,
                speed: 2,
                direction: "none",
                random: true,
                straight: false,
                out_mode: "out",
                bounce: false,
                attract: { enable: true, rotateX: 600, rotateY: 1200 }
            }
        },
        interactivity: {
            detect_on: "canvas",
            events: {
                onhover: { enable: false },
                onclick: { enable: false },
                resize: true
            }
        },
        retina_detect: true
    });

    document.addEventListener('mousemove', function(e) {
        const particles = pJSDom[0].pJS.particles;
        const canvasWidth = pJSDom[0].pJS.canvas.w;
        const canvasHeight = pJSDom[0].pJS.canvas.h;
        
        // Check if mouse is in first quadrant
        if(e.clientX < canvasWidth/2 && e.clientY < canvasHeight/2) {
            particles.move.enable = true;
            
            // Add new particles
            for(let i = 0; i < 2; i++) {
                pJSDom[0].pJS.fn.modes.pushParticle(
                    e.clientX + Math.random()*20 -10,
                    e.clientY + Math.random()*20 -10
                );
            }
            
            // Clear timeout if existing
            if(particleTimeout) clearTimeout(particleTimeout);
            
            // Set timeout to stop particles
            particleTimeout = setTimeout(() => {
                particles.move.enable = false;
                pJSDom[0].pJS.particles.array = [];
            }, 1000);
        }
    });
    </script>
    """)

@st.cache_resource
def load_model():
    return joblib.load("xgboost_model.pkl")

# باقي الكود بدون تغيير ...
# ... [يتبع باقي الكود السابق بدون تعديل] ...
