
import base64, os, json
from io import BytesIO
import streamlit as st
from PIL import Image
from openai import OpenAI

st.set_page_config(page_title="K-Tex Screenshot Signal Board", page_icon="📈", layout="centered")

st.title("📈 K-Tex Screenshot Signal Board")
st.caption("Screenshot-based market analysis. This is decision support, not a guarantee of the next candle.")

with st.sidebar:
    st.header("Settings")
    asset = st.text_input("Asset / pair", "CAD/CHF (OTC)")
    timeframe = st.selectbox("Candle timeframe", ["1m","2m","5m","15m","30m","1h","4h","1d"], index=2)
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        st.warning("Set OPENAI_API_KEY in the deployment environment.")

uploaded = st.file_uploader("Upload K-Tex chart screenshot", type=["png","jpg","jpeg"])

if uploaded:
    img = Image.open(uploaded)
    st.image(img, caption="Uploaded chart", use_container_width=True)

    if st.button("🔎 Analyze chart", type="primary", use_container_width=True):
        if not api_key:
            st.error("OPENAI_API_KEY is not configured. Add it in the app's deployment secrets.")
            st.stop()

        client = OpenAI(api_key=api_key)
        buf = BytesIO()
        img.convert("RGB").save(buf, format="JPEG", quality=90)
        b64 = base64.b64encode(buf.getvalue()).decode()

        prompt = f"""
You are a cautious technical-chart analysis assistant.
Analyze ONLY what is visible in this screenshot for {asset}, timeframe {timeframe}.
Do not claim certainty about the next candle. If essential indicators or candle details
are not visible, say so and lower confidence.

Return JSON with exactly:
{{
  "trend": "BULLISH|BEARISH|SIDEWAYS|UNCLEAR",
  "signal": "UP|DOWN|NO TRADE",
  "confidence": 0,
  "visible_indicators": ["..."],
  "reasons": ["..."],
  "risk_flags": ["..."],
  "data_needed": ["..."]
}}
Confidence must be an integer from 0 to 100 and represent confidence in the analysis,
NOT a guaranteed probability that the next candle will move that way.
"""

        response = client.responses.create(
            model="gpt-5.6",
            input=[{
                "role":"user",
                "content":[
                    {"type":"input_text","text":prompt},
                    {"type":"input_image","image_url":f"data:image/jpeg;base64,{b64}"}
                ]
            }]
        )

        text = response.output_text.strip()
        try:
            result = json.loads(text)
        except Exception:
            st.error("The analysis service returned an unexpected format.")
            st.code(text)
            st.stop()

        st.subheader("Analysis")
        c1,c2,c3 = st.columns(3)
        c1.metric("Trend", result.get("trend","UNCLEAR"))
        c2.metric("Signal", result.get("signal","NO TRADE"))
        c3.metric("Confidence", f'{result.get("confidence",0)}%')

        st.write("**Visible indicators**")
        for x in result.get("visible_indicators", []): st.write("• " + x)

        st.write("**Reasons**")
        for x in result.get("reasons", []): st.write("• " + x)

        if result.get("risk_flags"):
            st.write("**Risk flags**")
            for x in result["risk_flags"]: st.write("• " + x)

        if result.get("data_needed"):
            st.write("**Additional data needed**")
            for x in result["data_needed"]: st.write("• " + x)

        st.warning("Do not treat the signal as a guaranteed prediction. OTC charts may also have data limitations; verify the setup before acting.")
else:
    st.info("Take a screenshot of the K-Tex chart, upload it here, choose the candle timeframe, then tap Analyze chart.")
