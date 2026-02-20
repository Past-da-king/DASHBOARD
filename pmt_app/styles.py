import streamlit as st


def global_css():
    st.markdown(
        """
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        /* --- GLOBAL THEME --- */
        :root {
            --primary-color: #2c5aa0;
            --secondary-color: #5fa2e8;
            --bg-color: #f8f9fa;
            --text-color: #333333;
            --subtext-color: #666666;
            --card-bg: #ffffff;
        }

        /* Main Container */
        .stApp {
            background-color: var(--bg-color);
            font-family: 'Segoe UI', 'Inter', sans-serif;
        }

        /* --- TYPOGRAPHY --- */
        h1, h2, h3 {
            color: var(--primary-color) !important;
            font-weight: 600 !important;
        }
        
        p, div, span {
            color: var(--text-color);
        }

        /* --- COMPONENTS --- */
        
        /* Buttons (Pill shaped, premium feel) */
        .stButton > button {
            border-radius: 20px;
            background-color: white;
            color: var(--primary-color);
            border: 1px solid var(--primary-color);
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            background-color: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
            box-shadow: 0 4px 6px rgba(44, 90, 160, 0.2);
        }
        
        /* Primary Action Buttons */
        .stButton > button[kind="primary"] {
            background-color: var(--primary-color);
            color: white;
        }

        /* Login/Card Containers */
        .login-container {
            background-color: var(--card-bg);
            padding: 3rem;
            border-radius: 12px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.08);
            max-width: 450px;
            margin: auto;
        }
        
        .header {
            color: var(--primary-color);
            text-align: center;
            margin-bottom: 2rem;
            font-size: 2.5rem;
            letter-spacing: -0.5px;
        }

        /* Health Indicators */
        .health-container {
            display: flex;
            justify-content: space-around;
            align-items: center;
            padding: 1rem 0;
            background: white;
            border-radius: 12px;
            border: 1px solid #eee;
            box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        }
        .health-item {
            text-align: center;
            flex: 1;
        }
        .health-icon {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 0.5rem;
            font-weight: bold;
            font-size: 1.2rem;
            transition: transform 0.2s ease;
        }
        .health-item:hover .health-icon {
            transform: scale(1.1);
        }
        .health-label {
            font-size: 0.8rem;
            color: var(--subtext-color);
            font-weight: 500;
        }

        /* Icon Styles */
        .icon-btn {
            margin-right: 8px;
        }
        .icon-success { color: #4caf50; }
        .icon-warning { color: #ffc107; }
        .icon-danger { color: #f44336; }
        .icon-info { color: #2196f3; }
        .icon-primary { color: #2c5aa0; }
        
        /* Icon in buttons */
        .stButton > button i {
            margin-right: 6px;
        }
        
        /* Section icons */
        .section-icon {
            margin-right: 10px;
            color: var(--primary-color);
        }
        
        /* Export Button */
        .export-btn {
            background: linear-gradient(90deg, #4caf50 0%, #2e7d32 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: 500;
            transition: all 0.3s ease;
        }
        .export-btn:hover {
            box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
            transform: translateY(-2px);
        }
    </style>
    """,
        unsafe_allow_html=True,
    )
