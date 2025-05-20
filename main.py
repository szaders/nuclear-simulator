import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objs as go
import streamlit.components.v1 as components


# ─── Page Config ──────────────────────────────────────────────────────────
st.set_page_config(page_title="Energy & Nuclear Simulator", layout="centered")

# ─── App Title ────────────────────────────────────────────────────────────
st.title("🌎 Energy Mix & Nuclear Simulation")

# ─── Sidebar: Cited Facts ─────────────────────────────────────────────────
st.sidebar.header("📚 Key Facts & Sources")
st.sidebar.markdown("""
**Energy Comparison Metrics**  
- Nuclear CF: 81.5% contentReference[oaicite:0]{index=0}  
- Solar CF: 23.5% contentReference[oaicite:1]{index=1}  
- Wind CF: 36% contentReference[oaicite:2]{index=2}  
- Hydro CF: 44% contentReference[oaicite:3]{index=3}  

- Nuclear CO₂: 12 g/kWh contentReference[oaicite:4]{index=4}  
- Solar CO₂: 48 g/kWh contentReference[oaicite:5]{index=5}  
- Wind CO₂: 11 g/kWh contentReference[oaicite:6]{index=6}  
- Hydro CO₂: 24 g/kWh contentReference[oaicite:7]{index=7}  

**Nuclear‑Specific Facts**  
1. Nuclear = ~19% U.S. power, no CO₂ in operation contentReference[oaicite:8]{index=8}  
2. 2024 capacity factor: nuclear 92%, wind 34%, solar 23% contentReference[oaicite:9]{index=9}  
3. Spent fuel: ~2,000 tons/year U.S. contentReference[oaicite:10]{index=10}  
4. Chernobyl long‑term deaths ~4,000 contentReference[oaicite:11]{index=11}  
5. Fukushima: 0 acute radiation deaths; ~2,313 evacuation‑related contentReference[oaicite:12]{index=12}  
6. Yucca site pending political approval contentReference[oaicite:13]{index=13}  
7. 56% Americans favor more nuclear; 47% oppose nearby plants contentReference[oaicite:14]{index=14}  
8. 8.5 M solar panels ≈ one reactor output contentReference[oaicite:15]{index=15}  
""")

# ─── Surveys ───────────────────────────────────────────────────────────────
st.header("📝 Pre‑Simulation Survey")
pre_url = "https://docs.google.com/forms/d/e/1FAIpQLSf_qWs5dId9c5FcPwE9LmQx_Wgxn7KISY6eFCrsUw10-7rzng/viewform?usp=header"
components.iframe(pre_url, width=700, height=800, scrolling=True)

# ─── Nuclear Simulation Controls ───────────────────────────────────────────
st.header("⚙️ Nuclear Simulation")
funding = st.slider("Government Funding ($ B)", 0, 100, 50)
regulation = st.slider("Oversight Strictness (0–10)", 0, 10, 5)
reactors = st.slider("Number of Reactors", 0, 200, 100)
green_pct = st.slider("Green Investment (%)", 0, 100, 20)

# ─── Simulation Logic ─────────────────────────────────────────────────────
co2_reduction = reactors * (1 - green_pct/100) * 0.5    # Mt CO₂
risk_index = max(0, 10 - regulation) * (reactors / 100) # %
energy_output = reactors * funding / 100               # TWh

# ─── Display Nuclear Results ──────────────────────────────────────────────
st.subheader("📊 Nuclear Simulation Results")
st.metric("Annual CO₂ ↓ (Mt)", f"{co2_reduction:.1f}")
st.metric("Disaster Risk Index (%)", f"{risk_index:.1f}")
st.metric("Energy Output (TWh)", f"{energy_output:.1f}")

fig_nuc = go.Figure()
fig_nuc.add_trace(go.Bar(name="CO₂ ↓", x=["Metric"], y=[co2_reduction]))
fig_nuc.add_trace(go.Bar(name="Risk×10", x=["Metric"], y=[risk_index * 10]))
fig_nuc.update_layout(barmode='group', title="Nuclear: CO₂ vs. Risk")
st.plotly_chart(fig_nuc, use_container_width=True)

# ─── Post‑Simulation Survey ────────────────────────────────────────────────
st.header("📝 Post‑Simulation Survey")
post_url = "https://docs.google.com/forms/d/e/1FAIpQLSf3NfrKHthVsFTCxol4lwclUE2e5rhOcJSUoqZyyTuEzg4TCQ/viewform?usp=header"
components.iframe(post_url, width=700, height=800, scrolling=True)

# ─── Energy Comparison Section ────────────────────────────────────────────
st.header("🔍 Compare Energy Sources")
metrics = {
    "Capacity Factor (%)": {"Nuclear":81.5,"Solar":23.5,"Wind":36.0,"Hydro":44.0},
    "CO₂ Emissions (g/kWh)": {"Nuclear":12,"Solar":48,"Wind":11,"Hydro":24}
}
choice = st.selectbox("Select a metric:", list(metrics.keys()))
df = pd.DataFrame.from_dict(metrics[choice], orient="index", columns=[choice]).reset_index()
df.rename(columns={"index":"Source"}, inplace=True)

fig_cmp = go.Figure([go.Bar(x=df["Source"], y=df[choice], text=df[choice], textposition="auto")])
fig_cmp.update_layout(title=f"{choice} by Source", yaxis_title=choice, xaxis_title="Source")
st.plotly_chart(fig_cmp, use_container_width=True)

# ─── Energy‑Mix Simulator ─────────────────────────────────────────────────
st.subheader("⚙️ Simulate an Energy Mix Impact")
st.markdown("Distribute 100% across sources and see weighted metrics:")

n_pct = st.slider("Nuclear (%)", 0, 100, 25)
s_pct = st.slider("Solar (%)", 0, 100-n_pct, 25)
w_pct = st.slider("Wind (%)", 0, 100-n_pct-s_pct, 25)
h_pct = 100 - n_pct - s_pct - w_pct
st.write(f"Hydro (%) = **{h_pct}**")

weights = {"Nuclear":n_pct,"Solar":s_pct,"Wind":w_pct,"Hydro":h_pct}
w_cf = sum(metrics["Capacity Factor (%)"][src]*pct/100 for src,pct in weights.items())
w_co2 = sum(metrics["CO₂ Emissions (g/kWh)"][src]*pct/100 for src,pct in weights.items())

st.metric("Weighted CF (%)", f"{w_cf:.1f}")
st.metric("Weighted CO₂ (g/kWh)", f"{w_co2:.1f}")

# ─── Example Survey Data ──────────────────────────────────────────────────
st.header("📈 Example Survey Results (n=147)")
np.random.seed(42)
df_demo = pd.DataFrame({
    "Age": np.random.choice(["18-29","30-49","50+"], 147, p=[0.4,0.33,0.27]),
    "Support": np.random.choice(["Yes","No","Unsure"], 147, p=[0.52,0.21,0.27]),
    "ViewChange": np.random.choice(["More fav","Unchanged","More skeptical"], 147, p=[0.54,0.35,0.11])
})
st.dataframe(df_demo.head(10), width=700)
st.bar_chart(df_demo["Support"].value_counts())

