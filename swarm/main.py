import os
import yfinance as yf
from openai import OpenAI
from supabase import create_client, Client

# 1. Setup (Using ZhipuAI / GLM-4)
client = OpenAI(
    api_key=os.environ["ZHIPU_API_KEY"],
    base_url="https://open.bigmodel.cn/api/paas/v4/"
)
supabase: Client = create_client(
    os.environ["SUPABASE_URL"], 
    os.environ["SUPABASE_KEY"]
)

TICKER = "AAPL" # Hardcoded for Alpha

def run_alpha():
    print(f"1. Fetching data for {TICKER}...")
    stock = yf.Ticker(TICKER)
    # Get last 2 days of history to simulate "technical data"
    hist = stock.history(period="5d").tail(2).to_string()
    
    # Get "News" (using yfinance's built-in search as a poor-man's news API)
    news = stock.news[:2] if stock.news else "No recent news."

    print("2. Thinking (GLM-4)...")
    prompt = f"""
    Analyze {TICKER}. 
    Market Data: {hist}
    News snippets: {news}
    
    Output a 2-sentence summary of the trend and a sentiment score (0.0 to 1.0).
    Format: JSON {{ "summary": "...", "score": 0.5 }}
    """
    
    completion = client.chat.completions.create(
        model="glm-4-flash",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"}
    )
    
    result = completion.choices[0].message.content
    import json
    data = json.loads(result)

    print("3. Saving to Database...")
    supabase.table("daily_reports").insert({
        "ticker": TICKER,
        "summary_markdown": data.get("summary"),
        "sentiment_score": data.get("score")
    }).execute()
    
    print("Done.")

if __name__ == "__main__":
    run_alpha()
