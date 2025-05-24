# nuclear_simulation_app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objs as go
import streamlit.components.v1 as components
import os

# ─── Page Config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Energy & Nuclear Simulator", layout="wide")

# ─── Sidebar: Informational Facts ─────────────────────────────────────────
st.sidebar.header("📚 Scientific Sources & Facts")
st.sidebar.markdown("""
**🔬 Nuclear Facts:**
- Capacity Factor: Nuclear 92%, Wind 34%, Solar 23% ([WNA 2023](https://world-nuclear.org))
- CO₂ Avoided: ~4.8 Mt per reactor/year ([WNA 2023](https://world-nuclear.org))
- Output: 8.2 TWh/reactor/year ([world-nuclear.org](https://world-nuclear.org))
- Waste: ~21.5 t/reactor/year ([energy.gov](https://www.energy.gov))
- Safety: Cumulative 18,500 reactor-years, only 2 major incidents ([world-nuclear.org](https://world-nuclear.org))

**🧾 Public Opinion:**
- 2024: 56% support building new nuclear ([pewresearch.org](https://pewresearch.org))
- 61% support using nuclear power ([Gallup](https://world-nuclear-news.org))

**📊 Energy Comparison:**
- Solar CF: 23.5%, Wind CF: 36%, Hydro CF: 44%
- CO₂ Emissions: Nuclear 12 g/kWh, Solar 48, Wind 11, Hydro 24
""")

# ─── Step 1: Learn ────────────────────────────────────────────────────────
st.title("🌎 Step 1: Learn About Nuclear Energy")

st.markdown("""
Nuclear power provides nearly **20% of electricity in the U.S.**, and produces **zero operational CO₂ emissions**. 
Modern reactors are highly efficient and safe. They have **capacity factors over 90%**, far more consistent than wind or solar.
""")

st.markdown("**Relevant Facts:**")
learn_col1, learn_col2 = st.columns(2)
with learn_col1:
    st.metric("US Nuclear Share", "~19%")
    st.metric("Typical CO₂ Avoided", "~4.8 Mt/year/reactor")
    st.metric("Avg Output", "8.2 TWh/reactor")
with learn_col2:
    st.metric("Spent Fuel/yr/reactor", "~21.5 tons")
    st.metric("Cumulative Reactors-Years", "18,500")
    st.metric("Accidents", "2 major incidents")

# ─── Pre-Simulation Survey ───────────────────────────────────────────────
st.header("📝 Step 2: Pre-Simulation Survey")
pre_url = "https://docs.google.com/forms/d/e/1FAIpQLSf_qWs5dId9c5FcPwE9LmQx_Wgxn7KISY6eFCrsUw10-7rzng/viewform"
components.iframe(pre_url, height=750, scrolling=True)

# ─── Step 3: Simulate ────────────────────────────────────────────────────
st.header("⚙️ Step 3: Energy Scenario Simulator")

scenario = st.selectbox("Choose a Scenario", ["Custom", "Green City", "Rapid Growth", "Drought Region"])
defaults = {
    "funding": 50, "regulation": 5, "reactors": 100,
    "green_pct": 20, "water_pct": 30, "pop_growth": 1.0
}
if scenario == "Green City":
    defaults = {"funding": 40, "regulation": 8, "reactors": 50, "green_pct": 80, "water_pct": 20, "pop_growth": 0.5}
elif scenario == "Rapid Growth":
    defaults = {"funding": 80, "regulation": 4, "reactors": 150, "green_pct": 30, "water_pct": 40, "pop_growth": 3}
elif scenario == "Drought Region":
    defaults = {"funding": 60, "regulation": 6, "reactors": 80, "green_pct": 40, "water_pct": 70, "pop_growth": 1.2}

# Sliders with sources
st.markdown("### Simulation Controls (with source links)")
funding = st.slider("Government R&D Funding ($B) [Source](https://energy.gov)", 0, 100, defaults["funding"])
regulation = st.slider("Oversight Strictness (0–10) [Source](https://world-nuclear.org)", 0, 10, defaults["regulation"])
reactors = st.slider("Number of Reactors [Source](https://world-nuclear.org)", 0, 200, defaults["reactors"])
green_pct = st.slider("Green Energy Investment (%) [Source](https://iea.org)", 0, 100, defaults["green_pct"])
water_pct = st.slider("Water Withdrawal (%) [Source](https://world-nuclear.org)", 0, 100, defaults["water_pct"])
pop_growth = st.slider("Population Growth Rate (%) [Source](https://worldbank.org)", 0.0, 5.0, float(defaults["pop_growth"]), step=0.1)

# Simulation Logic
co2_reduction = reactors * (1 - green_pct / 100) * 4.8
risk_index = max(0, 10 - regulation) * (reactors / 100)
energy_output = reactors * (funding / 100) * 8.2
biodiv_loss = water_pct * 0.8
proj_demand = 1000 * (1 + pop_growth / 100) ** 10

# Results Panel
st.subheader("📊 Results & Interpretation")
res1, res2, res3 = st.columns(3)
res1.metric("CO₂ Avoided (Mt)", f"{co2_reduction:.1f}")
res2.metric("Risk Index (%)", f"{risk_index:.1f}")
res3.metric("Energy Output (TWh)", f"{energy_output:.1f}")

st.markdown(f"- **Projected Demand in 10 Years:** {proj_demand:.0f} TWh")
st.markdown(f"- **Biodiversity Impact:** {biodiv_loss:.1f}%")

st.info(f"Based on current inputs: {reactors} reactors with {funding}B funding and regulation level {regulation}...")

# ─── Sankey Diagram ──────────────────────────────────────────────────────
st.subheader("🔀 Energy Flow (Sankey)")
labels = ["Demand", "Nuclear", "Solar", "Wind", "Hydro", "Surplus", "Shortfall"]
mix = {
    "Nuclear": energy_output * 0.4,
    "Solar": energy_output * 0.2,
    "Wind": energy_output * 0.2,
    "Hydro": energy_output * 0.2
}

demand = proj_demand
sources, targets, values = [], [], []
for src, val in mix.items():
    sources.append(labels.index(src))
    targets.append(labels.index("Demand"))
    values.append(val)

supplied = sum(mix.values())
if supplied > demand:
    sources.append(labels.index("Demand"))
    targets.append(labels.index("Surplus"))
    values.append(supplied - demand)
else:
    sources.append(labels.index("Shortfall"))
    targets.append(labels.index("Demand"))
    values.append(demand - supplied)

fig_sankey = go.Figure(go.Sankey(
    node=dict(label=labels, pad=15, thickness=20),
    link=dict(source=sources, target=targets, value=values)
))
fig_sankey.update_layout(title_text="Energy Flow Sankey Diagram", font_size=12)
st.plotly_chart(fig_sankey, use_container_width=True)

# ─── Step 4: Reflect ─────────────────────────────────────────────────────
st.header("📝 Step 4: Post-Simulation Survey")
post_url = "https://docs.google.com/forms/d/e/1FAIpQLSf3NfrKHthVsFTCxol4lwclUE2e5rhOcJSUoqZyyTuEzg4TCQ/viewform"
components.iframe(post_url, height=750, scrolling=True)

# ─── Survey Results Analysis ─────────────────────────────────────────────
st.subheader("📈 Survey Results & Reflection")
np.random.seed(42)
df_demo = pd.DataFrame({
    "Age": np.random.choice(["18–29", "30–49", "50+"], 147, p=[0.4, 0.35, 0.25]),
    "Support": np.random.choice(["Yes", "No", "Unsure"], 147, p=[0.56, 0.22, 0.22]),
    "Change": np.random.choice(["More Favorable", "No Change", "More Skeptical"], 147)
})
st.dataframe(df_demo.head(10))
st.bar_chart(df_demo["Support"].value_counts())

# ─── End ─────────────────────────────────────────────────────────────────
st.markdown("""
---
**Sources**: world-nuclear.org, energy.gov, pewresearch.org, gallup.com, iaea.org, nei.org
""")
