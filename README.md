
# K-Tex Screenshot Signal Board

## What it does
1. Open K-Tex on your iPhone.
2. Take a screenshot of the chart.
3. Upload the screenshot to this board.
4. Select the candle timeframe.
5. Tap **Analyze chart**.
6. The board returns Trend, UP/DOWN/NO TRADE, confidence, visible indicators, reasons, and risk flags.

## Important
This is analysis/decision support. It does not place trades and cannot guarantee the next candle.

## Deploy
Deploy `app.py` on Streamlit Community Cloud or another Python hosting service.
Set the deployment secret/environment variable:
`OPENAI_API_KEY=your_key_here`

Then open the generated web URL on your iPhone and optionally add it to the Home Screen.

## Local test
pip install -r requirements.txt
streamlit run app.py
