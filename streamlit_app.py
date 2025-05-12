import pandas as pd
import streamlit as st
import joblib
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit.components.v1 import html
import json
from calendar import monthrange

# Custom CSS with dark/light mode compatibility
def inject_custom_style():
    st.markdown("""
    <style>
        /* Dynamic background based on theme */
        [data-testid="stAppViewContainer"] {
            background-color: var(--background-color);
        }
        
        .stApp {
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }
        
        /* Enhanced card with theme compatibility */
        .card {
            transition: all 0.4s ease;
            border-radius: 15px;
            padding: 20px;
            margin: 10px 0;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            box-shadow: 0 4px 15px var(--card-shadow);
        }
        
        .card:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 10px 25px var(--card-shadow-hover);
        }
        
        /* Modern button with theme compatibility */
        .stButton>button {
            border: none;
            border-radius: 25px;
            padding: 12px 28px;
            transition: all 0.4s;
            background: linear-gradient(135deg, var(--button-gradient-start), var(--button-gradient-end));
            color: var(--button-text) !important;
            font-weight: 600;
            box-shadow: 0 4px 8px var(--button-shadow);
            position: relative;
            overflow: hidden;
        }
        
        .stButton>button:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 15px var(--button-shadow-hover);
        }
        
        /* Slider styling */
        .stSlider .thumb {
            width: 20px !important;
            height: 20px !important;
        }
        
        /* Date input styling */
        .stDateInput>div>div>input {
            border-radius: 15px !important;
            padding: 12px !important;
        }
        
        /* Theme variables */
        :root {
            --background-color: #ffffff;
            --card-bg: rgba(255, 255, 255, 0.95);
            --card-border: rgba(0, 0, 0, 0.1);
            --card-shadow: rgba(0, 0, 0, 0.1);
            --card-shadow-hover: rgba(0, 0, 0, 0.2);
            --button-gradient-start: #4CAF50;
            --button-gradient-end: #2E7D32;
            --button-text: white;
            --button-shadow: rgba(76, 175, 80, 0.3);
            --button-shadow-hover: rgba(76, 175, 80, 0.4);
        }
        
        @media (prefers-color-scheme: dark) {
            :root {
                --background-color: #0e1117;
                --card-bg: rgba(30, 30, 30, 0.95);
                --card-border: rgba(255, 255, 255, 0.1);
                --card-shadow: rgba(0, 0, 0, 0.3);
                --card-shadow-hover: rgba(0, 0, 0, 0.5);
                --button-gradient-start: #2E7D32;
                --button-gradient-end: #1B5E20;
                --button-text: white;
                --button-shadow: rgba(46, 125, 50, 0.3);
                --button-shadow-hover: rgba(46, 125, 50, 0.5);
            }
        }
    </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def load_model():
    return joblib.load("xgboost_model.pkl")

model = load_model()

inject_custom_style()
st.title("📈 Intelligent Sales Forecasting System")
st.markdown("Explore future sales predictions with our AI-powered forecasting engine")

col1, col2 = st.columns([2, 1])

with col1:
    with st.expander("🔮 Prediction Controls", expanded=True):
        col_year, col_month, col_day = st.columns(3)
        
        with col_year:
            selected_year = st.slider(
                "Year",
                min_value=2020,
                max_value=2030,
                value=datetime.now().year,
                key="year_slider"
            )
        
        with col_month:
            selected_month = st.slider(
                "Month",
                min_value=1,
                max_value=12,
                value=datetime.now().month,
                key="month_slider"
            )
        
        with col_day:
            _, last_day = monthrange(selected_year, selected_month)
            selected_day = st.slider(
                "Day",
                min_value=1,
                max_value=last_day,
                value=datetime.now().day,
                key="day_slider"
            )
        
        date_input = datetime(selected_year, selected_month, selected_day).date()
        
        if st.button("Generate Prediction", key="main_btn"):
            st.session_state['predict'] = True

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
        
        st.markdown(f"""
        <div class='card' style='animation: fadeIn 1s;'>
            <h3 style='color: var(--button-gradient-start);'>📅 {date_input.strftime('%Y-%m-%d')}</h3>
            <h2 style='color: #2196F3;'>Predicted Sales: ${prediction:,.2f}</h2>
            <p>🗓️ {date_input.strftime('%A')} | 📅 Q{date_features['Quarter']}</p>
        </div>
        """, unsafe_allow_html=True)

        # Generate full year data for visualizations
        months = pd.date_range(start=f"{selected_year}-01-01", end=f"{selected_year}-12-31")
        data = [get_date_features(d) for d in months]
        df = pd.DataFrame(data)
        df['Prediction'] = model.predict(df)

        # Time Series Animation
        st.markdown("### 🎥 Sales Evolution")
        fig = px.line(df, x=months, y='Prediction', 
                     labels={'y': 'Predicted Sales'},
                     hover_data={'date': months.strftime("%Y-%m-%d")})
        fig.update_traces(line=dict(width=3, color='#4CAF50'))
        fig.add_vline(x=date_input, line_dash="dot", line_color="red")
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Prediction Error: {str(e)}")

with col2:
    st.markdown("### 🏆 Feature Impact")
    try:
        features = ['Year', 'Month', 'Quarter', 'Day', 'DayOfWeek', 'DayOfYear', 'WeekOfYear']
        importances = model.feature_importances_
        
        fig = px.bar(x=importances, y=features, orientation='h',
                    color=importances, color_continuous_scale='Bluered')
        fig.update_layout(showlegend=False, 
                         xaxis_title='Importance Score',
                         yaxis_title='Features',
                         height=400)
        st.plotly_chart(fig, use_container_width=True)
    except:
        st.warning("Feature importance not available for this model")
