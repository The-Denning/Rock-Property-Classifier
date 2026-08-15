"""
 
AI DEVELOPMENT DOCUMENTATION (Project 8)
 
AI Tools Used: ChatGPT & Gemini

Key Prompts Used:
1. "Generate a Streamlit dashboard that classifies reservoir rock quality based 
   on porosity and permeability inputs."
2. "Add an interactive Plotly scatter plot showing porosity vs permeability with 
   reservoir quality cutoff zones."
3. "Include dynamic error handling using st.warning for non-physical inputs 
   (e.g., negative porosity or zero permeability)."

Manual Fixes & Verification Required:
- Fixed a bug where negative porosity values caused log-scale plotting errors.
- Added explicit boundary condition checks to display st.warning() alerts 
  instead of letting the app crash with Python Traceback errors.
- Standardized rock classification thresholds (Tight, Fair, Good, Excellent) 
  to align with standard petroleum reservoir engineering conventions.
 
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Rock Property Classifier",
    page_icon="🪨",
    layout="wide"
)

# --- TITLE & INSTRUCTIONS ---
st.title("Rock Property Classifier & Reservoir Quality Dashboard")
st.subheader("Interactive Petrophysical Assessment Tool")
st.markdown("""
Welcome! This app helps petroleum engineers evaluate reservoir rock quality. 
**Instructions:** Use the sidebar on the left to input core sample parameters. The dashboard will instantly update the rock classification, summary metrics, and visual comparison chart!
""")

# --- SIDEBAR INPUT CONTROLS ---
st.sidebar.header(" Core Sample Inputs")

# Control 1: Number Input / Slider for Porosity
porosity = st.sidebar.slider("Porosity, ϕ (%)", min_value=-5.0, max_value=40.0, value=18.0, step=0.5)

# Control 2: Number Input for Permeability
permeability = st.sidebar.number_input("Permeability, k (mD)", min_value=-10.0, max_value=5000.0, value=120.0, step=10.0)

# Control 3: Selectbox for Lithology
lithology = st.sidebar.selectbox("Lithology Type", ["Sandstone", "Limestone", "Dolomite", "Shale"])

# --- ERROR HANDLING & VALIDATION ---
has_error = False

if porosity < 0:
    st.error("⚠️ **Invalid Input:** Porosity cannot be negative! Please enter a value between 0% and 40%.")
    has_error = True
elif porosity > 35:
    st.warning("⚠️ **High Porosity Alert:** Porosity above 35% is uncommonly high for consolidated oil reservoirs.")

if permeability <= 0:
    st.error("⚠️ **Invalid Input:** Permeability must be greater than 0 mD for fluid flow calculations.")
    has_error = True

# Proceed only if inputs are physically valid
if not has_error:
    
    # --- CLASSIFICATION LOGIC ---
    if porosity < 5 or permeability < 0.1:
        quality = "Non-Reservoir / Tight"
        color = "red"
    elif porosity < 10 or permeability < 1.0:
        quality = "Poor Quality"
        color = "orange"
    elif porosity < 15 or permeability < 50.0:
        quality = "Fair Quality"
        color = "gold"
    elif porosity < 22 or permeability < 500.0:
        quality = "Good Quality"
        color = "green"
    else:
        quality = "Excellent Quality"
        color = "darkgreen"

    # --- DISPLAY METRICS ---
    col1, col2, col3 = st.columns(3)
    col1.metric("Lithology", lithology)
    col2.metric("Porosity", f"{porosity:.1f} %")
    col3.metric("Permeability", f"{permeability:.1f} mD")

    st.markdown(f"### Reservoir Classification: **:{color}[{quality}]**")
    
    # --- PANDAS SUMMARY TABLE ---
    st.markdown("### Sample Summary Table")
    
    # Calculate estimated Hydraulic Radius / Flow Zone Indicator proxy
    fzi_proxy = np.sqrt(permeability / (porosity + 1e-6))
    
    sample_data = pd.DataFrame({
        "Property": ["Lithology Type", "Porosity (ϕ)", "Permeability (k)", "Quality Rating", "Flow Indicator Proxy"],
        "Value": [lithology, f"{porosity}%", f"{permeability} mD", quality, f"{fzi_proxy:.2f}"],
        "Unit": ["Category", "%", "mD", "Category", "Index"]
    })
    
    st.dataframe(sample_data, use_container_width=True)

    # --- INTERACTIVE PLOTLY CHART ---
    st.markdown("### Porosity vs Permeability Trend")
    
    # Generate background comparison dataset
    np.random.seed(42)
    sample_porosity = np.random.uniform(5, 30, 50)
    sample_perm = 10 ** (0.15 * sample_porosity + np.random.normal(0, 0.5, 50))
    
    df_chart = pd.DataFrame({"Porosity (%)": sample_porosity, "Permeability (mD)": sample_perm, "Type": "Reference Samples"})
    
    fig = px.scatter(
        df_chart, 
        x="Porosity (%)", 
        y="Permeability (mD)", 
        log_y=True,
        title="Sample Position vs Core Reference Database",
        opacity=0.5
    )
    
    # Overlay the current user's input sample as a big star
    fig.add_scatter(
        x=[porosity], 
        y=[permeability], 
        mode="markers", 
        marker=dict(size=18, color="red", symbol="star"),
        name="Your Core Sample"
    )
    
    st.plotly_chart(fig, use_container_width=True)
