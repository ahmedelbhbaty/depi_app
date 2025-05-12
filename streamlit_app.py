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
        .stApp {
            background: linear-gradient(rgba(255,255,255,0.8), rgba(255,255,255,0.8));
            background-size: cover;
            background-position: center;
        }
        
        .card {
            transition: all 0.4s ease;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            background: linear-gradient(135deg, #FFF3B0, #FFD700);
            border: 2px solid #FFC107;
            color: #2F4F4F;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }
        
        .stButton>button {
            border: none;
            border-radius: 25px;
            padding: 12px 24px;
            background: linear-gradient(135deg, #4CAF50, #2E7D32);
            color: white !important;
            box-shadow: 0 4px 8px rgba(76, 175, 80, 0.3);
        }
    </style>
    """, unsafe_allow_html=True)
    
    html("""
    <script src="https://cdn.jsdelivr.net/particles.js/2.0.0/particles.min.js"></script>
    <div id="particles-js" style="position:fixed;top:0;left:0;z-index:-1;"></div>
    <script>
        particlesJS('particles-js', {
            particles: {
                number: { value: 80 },
                color: { value: "#4CAF50" },
                shape: { type: "circle" },
                opacity: { value: 0.7 },
                size: { value: 3 },
                move: { enable: true, speed: 3 }
            },
            interactivity: {
                events: {
                    onhover: { enable: true, mode: "repulse" },
                    onclick: { enable: true, mode: "push" }
                }
            }
        });
    </script>
    """)

@st.cache_resource
def load_model():
    return joblib.load("xgboost_model.pkl")

model = load_model()
inject_custom_style()

st.title("📈 Intelligent Sales Forecasting")
col1, col2 = st.columns([2, 1])

with col1:
    with st.expander("🔮 Select Prediction Date", expanded=True):
        col_year, col_month, col_day = st.columns(3)
        with col_year:
            year = st.slider("Year", 2020, 2030, datetime.now().year)
        with col_month:
            month = st.slider("Month", 1, 12, datetime.now().month)
        with col_day:
            _, last_day = monthrange(year, month)
            day = st.slider("Day", 1, last_day, datetime.now().day)
        
        if st.button("Generate Prediction"):
            st.session_state['predict'] = True
            st.session_state['date'] = datetime(year, month, day).date()

def get_date_features(date):
    return {
        'Year': date.year,
        'Month': date.month,
        'Quarter': (date.month-1)//3 + 1,
        'Day': date.day,
        'DayOfWeek': date.weekday(),
        'DayOfYear': date.timetuple().tm_yday,
        'WeekOfYear': date.isocalendar().week
    }

if 'predict' in st.session_state:
    date = st.session_state['date']
    features = get_date_features(date)
    df = pd.DataFrame([features])
    
    try:
        prediction = model.predict(df)[0]
        
        # Prediction Card
        card_html = f"""
        <div class='card' id='predictionCard'>
            <h3 style='color:#8B8000;'>📅 {date.strftime('%Y-%m-%d')}</h3>
            <h2 style='color:#B8860B;'>Predicted Sales: ${prediction:,.2f}</h2>
            <p>🗓️ {date.strftime('%A')} | 📅 Q{features['Quarter']}</p>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        
        # Download Button Script
        html(f"""
        <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
        <script>
            function downloadCard() {{
                setTimeout(() => {{
                    html2canvas(document.querySelector('#predictionCard'), {{
                        useCORS: true,
                        logging: true
                    }}).then(canvas => {{
                        const link = document.createElement('a');
                        link.download = 'sales-prediction-{date}.png';
                        link.href = canvas.toDataURL('image/png');
                        link.click();
                    }});
                }}, 500);
            }}
        </script>
        
        <button onclick="downloadCard()" style='
            background: #FFD700;
            color: #2F4F4F;
            border: none;
            padding: 12px 24px;
            border-radius: 30px;
            margin: 10px 0;
            cursor: pointer;
            font-weight: bold;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        '>
            ⬇️ Download as Image
        </button>
        """)
        
        # Sales Chart
        dates = pd.date_range(start=f"{year}-01-01", end=f"{year}-12-31")
        full_data = pd.DataFrame([get_date_features(d) for d in dates])
        full_data['Prediction'] = model.predict(full_data)
        
        fig = px.line(full_data, x=dates, y='Prediction',
                     labels={'y': 'Sales Prediction'},
                     template='plotly_white')
        fig.update_traces(line=dict(width=2.5, color='#4CAF50'))
        fig.add_vline(x=date, line_dash="dot", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")

with col2:
    st.markdown("### 🏆 Feature Importance")
    try:
        features = ['Year','Month','Quarter','Day','DayOfWeek','DayOfYear','WeekOfYear']
        importance = model.feature_importances_
        
        fig = px.bar(x=importance, y=features, orientation='h',
                    color=importance, color_continuous_scale='tealgrn')
        fig.update_layout(height=400, showlegend=False,
                         xaxis_title='Importance Score',
                         yaxis_title='Features')
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Feature importance not available")

html("""
<script>
document.querySelectorAll('.stButton button').forEach(btn => {
    btn.addEventListener('click', () => {
        window.scrollTo({
            top: document.documentElement.scrollHeight,
            behavior: 'smooth'
        });
    });
});
</script>
""")
