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
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(12px);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            margin-bottom: 1rem;
        }
        
        .stButton>button {
            background: rgba(76, 175, 80, 0.8);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .moving-shape {
            position: fixed;
            width: 120px;
            height: 120px;
            background: rgba(76, 175, 80, 0.15);
            clip-path: polygon(50% 0%, 0% 100%, 100% 100%);
            animation: shapeMove 12s infinite linear;
            z-index: 9998;
            pointer-events: none;
            transition: all 0.5s ease;
        }
        
        @keyframes shapeMove {
            0% { 
                transform: rotateY(0deg) translateZ(100px);
                opacity: 0.8;
            }
            50% { 
                transform: rotateY(180deg) translateZ(-150px);
                opacity: 0.4;
            }
            100% { 
                transform: rotateY(360deg) translateZ(100px);
                opacity: 0.8;
            }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Mouse particles and moving shape script
    html("""
    <script>
    document.addEventListener('DOMContentLoaded', () => {
        // Add moving shape
        const shape = document.createElement('div');
        shape.className = 'moving-shape';
        document.body.appendChild(shape);
        
        // Mouse move interaction
        document.addEventListener('mousemove', (e) => {
            const x = (e.clientX / window.innerWidth) * 50;
            const y = (e.clientY / window.innerHeight) * 50;
            shape.style.transform += `rotateX(${y}deg) rotateY(${x}deg)`;
        });
        
        // Particle effect setup
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.zIndex = '9999';
        canvas.style.pointerEvents = 'none';
        document.body.appendChild(canvas);
        
        let particles = [];
        const particleCount = 15;
        
        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = Math.random() * 8 + 4;
                this.speedX = Math.random() * 1.5 - 0.75;
                this.speedY = Math.random() * 1.5 - 0.75;
                this.opacity = 1;
                this.angle = Math.random() * Math.PI * 2;
            }
            
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                this.opacity -= 0.015;
                this.size *= 0.97;
                this.angle += 0.05;
            }
            
            draw() {
                ctx.save();
                ctx.translate(this.x, this.y);
                ctx.rotate(this.angle);
                ctx.fillStyle = `rgba(76, 175, 80, ${this.opacity})`;
                ctx.beginPath();
                ctx.moveTo(0, -this.size);
                ctx.lineTo(-this.size, this.size);
                ctx.lineTo(this.size, this.size);
                ctx.closePath();
                ctx.fill();
                ctx.restore();
            }
        }
        
        function animate() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            particles.forEach((particle, index) => {
                particle.update();
                particle.draw();
                if (particle.opacity <= 0) particles.splice(index, 1);
            });
            requestAnimationFrame(animate);
        }
        
        function resizeCanvas() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
        }
        
        window.addEventListener('resize', resizeCanvas);
        resizeCanvas();
        
        document.addEventListener('mousemove', (e) => {
            for (let i = 0; i < particleCount; i++) {
                particles.push(new Particle(e.clientX, e.clientY));
            }
        });
        
        animate();
    });
    </script>
    """)

@st.cache_resource
def load_model():
    return joblib.load("xgboost_model.pkl")

model = load_model()

inject_custom_style()
st.title("📈 Intelligent Sales Forecasting System")

# Main layout
col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    with st.container():
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("### 📆 Annual Sales Trend")
        
        # Date selection
        date_cols = st.columns(3)
        with date_cols[0]:
            selected_year = st.slider("Year", 2020, 2030, datetime.now().year)
        with date_cols[1]:
            selected_month = st.slider("Month", 1, 12, datetime.now().month)
        with date_cols[2]:
            _, last_day = monthrange(selected_year, selected_month)
            selected_day = st.slider("Day", 1, last_day, datetime.now().day)
        
        date_input = datetime(selected_year, selected_month, selected_day).date()
        
        if st.button("Generate Prediction"):
            st.session_state['predict'] = True
        st.markdown("</div>", unsafe_allow_html=True)

def get_date_features(date):
    return {
        'Year': date.year,
        'Month': date.month,
        'Quarter': (date.month - 1) // 3 + 1,
        'Day': date.day,
        'DayOfWeek': date.weekday(),
        'DayOfYear': date.timetuple().tm_yday,
        'WeekOfYear': date.isocalendar().week
    }

if 'predict' in st.session_state:
    date_features = get_date_features(date_input)
    input_df = pd.DataFrame([date_features])
    
    try:
        prediction = model.predict(input_df)[0]
        
        # Prediction Card
        with col1:
            st.markdown(f"""
            <div class='glass-card'>
                <h3 style='color: #4CAF50;'>📅 {date_input.strftime('%Y-%m-%d')}</h3>
                <h2 style='color: #2196F3;'>Predicted Sales: ${prediction:,.2f}</h2>
                <p>🗓️ {date_input.strftime('%A')} | 📅 Q{date_features['Quarter']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Annual Trend Plot
            st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
            months = pd.date_range(start=f"{selected_year}-01-01", end=f"{selected_year}-12-31")
            data = [get_date_features(d) for d in months]
            df = pd.DataFrame(data)
            df['Prediction'] = model.predict(df)
            
            fig = px.line(df, x=months, y='Prediction', 
                         labels={'y': 'Predicted Sales'},
                         line_shape='spline')
            fig.update_traces(line=dict(width=3, color='#4CAF50'))
            fig.add_vline(x=date_input, line_dash="dot", line_color="red")
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Feature Importance
        with col2:
            st.markdown("<div class='glass-card' style='height: fit-content;'>", unsafe_allow_html=True)
            st.markdown("### 🏆 Feature Impact")
            try:
                features = ['Year', 'Month', 'Quarter', 'Day', 'DayOfWeek', 'DayOfYear', 'WeekOfYear']
                importances = model.feature_importances_
                
                fig = px.bar(x=importances, y=features, orientation='h',
                            color=importances, color_continuous_scale='Teal')
                fig.update_layout(showlegend=False, 
                                xaxis_title='Importance Score',
                                yaxis_title='Features',
                                height=500)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning("Feature importance not available")
            st.markdown("</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Prediction Error: {str(e)}")

# Hide scrollbar
html("""
<style>
    .st-emotion-cache-1dp5vir { display: none; }
    section.main { overflow: hidden !important; }
    .stScrollable { overflow: visible !important; }
</style>
""")
