import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit.components.v1 import html
from calendar import monthrange

# Custom CSS with smoke effect and gradient background
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
            background-size: 400% 400%;
            animation: gradient 15s ease infinite;
            min-height: 100vh;
            height: 100%;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .main-container {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            height: 100vh;
            padding: 1rem;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            backdrop-filter: blur(10px);
            border-radius: 15px;
            padding: 1.5rem;
            border: 1px solid rgba(255, 255, 255, 0.2);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-5px);
        }
        
        .stButton>button {
            background: rgba(76, 175, 80, 0.8);
            color: white;
            border: none;
            border-radius: 8px;
            padding: 12px 24px;
            font-size: 16px;
            transition: all 0.3s ease;
        }
        
        .stButton>button:hover {
            background: rgba(76, 175, 80, 1);
            transform: scale(1.05);
        }
        
        .stSlider .thumb {
            background-color: var(--primary-color) !important;
        }
        
        .stDateInput>div>div>input {
            background: rgba(255, 255, 255, 0.1) !important;
            color: white !important;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Smoke mouse effect
    html("""
    <script>
    document.addEventListener('DOMContentLoaded', () => {
        const canvas = document.createElement('canvas');
        const ctx = canvas.getContext('2d');
        canvas.style.position = 'fixed';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.zIndex = '9999';
        canvas.style.pointerEvents = 'none';
        document.body.appendChild(canvas);
        
        let particles = [];
        const particleCount = 20;
        
        class Particle {
            constructor(x, y) {
                this.x = x;
                this.y = y;
                this.size = Math.random() * 10 + 5;
                this.speedX = Math.random() * 3 - 1.5;
                this.speedY = Math.random() * 3 - 1.5;
                this.opacity = 1;
            }
            
            update() {
                this.x += this.speedX;
                this.y += this.speedY;
                this.opacity -= 0.03;
                this.size *= 0.97;
            }
            
            draw() {
                ctx.fillStyle = `rgba(76, 175, 80, ${this.opacity})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
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

# Main container with grid layout
main_col1, main_col2 = st.columns([2, 1], gap="medium")

with main_col1:
    with st.container():
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        col_year, col_month, col_day = st.columns(3)
        
        with col_year:
            selected_year = st.slider("Year", 2020, 2030, datetime.now().year)
        
        with col_month:
            selected_month = st.slider("Month", 1, 12, datetime.now().month)
        
        with col_day:
            _, last_day = monthrange(selected_year, selected_month)
            selected_day = st.slider("Day", 1, last_day, datetime.now().day)
        
        date_input = datetime(selected_year, selected_month, selected_day).date()
        
        if st.button("Generate Prediction", key="predict_btn"):
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
        
        with main_col1:
            st.markdown(f"""
            <div class='card' style='margin-top: 1rem;'>
                <h3 style='color: #4CAF50;'>📅 {date_input.strftime('%Y-%m-%d')}</h3>
                <h2 style='color: #2196F3;'>Predicted Sales: ${prediction:,.2f}</h2>
                <p>🗓️ {date_input.strftime('%A')} | 📅 Q{date_features['Quarter']}</p>
            </div>
            """, unsafe_allow_html=True)

        with main_col2:
            st.markdown("<div class='card' style='height: 400px;'>", unsafe_allow_html=True)
            st.markdown("### 🏆 Feature Impact")
            try:
                features = ['Year', 'Month', 'Quarter', 'Day', 'DayOfWeek', 'DayOfYear', 'WeekOfYear']
                importances = model.feature_importances_
                
                fig = px.bar(x=importances, y=features, orientation='h',
                            color=importances, color_continuous_scale='Teal')
                fig.update_layout(showlegend=False, 
                                xaxis_title='Importance Score',
                                yaxis_title='Features',
                                height=350)
                st.plotly_chart(fig, use_container_width=True)
            except:
                st.warning("Feature importance not available")
            st.markdown("</div>", unsafe_allow_html=True)

        with main_col1:
            st.markdown("<div class='card' style='margin-top: 1rem;'>", unsafe_allow_html=True)
            st.markdown("### 📆 Annual Sales Trend")
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

    except Exception as e:
        st.error(f"Prediction Error: {str(e)}")

html("""
<style>
    .st-emotion-cache-1dp5vir { display: none; }
    .stScrollable { overflow: visible !important; }
    section.main { overflow: visible !important; }
</style>
""")
