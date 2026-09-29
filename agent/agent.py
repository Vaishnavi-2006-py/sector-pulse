import os
import datetime
import requests
from groq import Groq

# Set default API endpoints and secrets
HINDSIGHT_URL = os.getenv("HINDSIGHT_API_URL", "http://localhost:8888")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client safely
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


class AppComparisonAgent:
    def __init__(self, api_url: str = HINDSIGHT_URL):
        self.api_url = api_url.rstrip("/")

    def ingest_app_signal(self, app_name: str, content: str, source: str = "market_feed") -> dict:
        """Stores a new event signal into a specific competitor memory bank using direct HTTP REST."""
        bank_id = f"bank-{app_name.lower().strip()}"
        url = f"{self.api_url}/banks/{bank_id}/retain"
        payload = {
            "content": content,
            "context": f"source:{source}",
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z"
        }
        try:
            response = requests.post(url, json=payload, timeout=5)
            if response.status_code in [200, 201]:
                return {"status": "success", "bank": bank_id, "data": response.json()}
            return {"status": "warning", "message": f"Server status {response.status_code}"}
        except Exception as e:
            return {"status": "fallback", "message": str(e)}

    def ingest_signal(self, content: str, source: str = "market_feed", timestamp: str = None, app_name: str = "Rapido") -> dict:
        """Alias wrapper method to prevent AttributeError when app.py calls ingest_signal directly."""
        return self.ingest_app_signal(app_name=app_name, content=content, source=source)

    def recall_history(self, app_name: str, query: str) -> list:
        """Queries Hindsight memory bank for past pricing, features, or strategic moves."""
        bank_id = f"bank-{app_name.lower().strip()}"
        url = f"{self.api_url}/banks/{bank_id}/recall"
        payload = {"query": query}
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code == 200:
                data = res.json()
                return data.get("memories", data) if isinstance(data, dict) else data
        except Exception:
            pass

        # Fallback historical context if memory backend service is offline
        fallbacks = {
            "rapido": [
                {"content": "Rapido launched zero-commission ride model and flat base fares for drivers."},
                {"content": "Rapido scaled 'Ownly' food delivery with 0% restaurant commissions in select metros."}
            ],
            "zomato": [
                {"content": "Zomato raised platform fees to ₹14.90-₹17.58 per order and increased commissions to 18-28%."},
                {"content": "Zomato expanded Gold dining program and high-margin priority delivery tiers."}
            ],
            "swiggy": [
                {"content": "Swiggy divested stake in Rapido and raised platform fees to protect margin targets."},
                {"content": "Swiggy One membership offers cross-app free delivery across food and Instamart."}
            ],
            "uber": [
                {"content": "Uber shifted strategy toward premium car categories, airport reserves, and Uber One passes."},
                {"content": "Uber introduced upfront fare locks and subscription discounts for corporate rides."}
            ]
        }
        return fallbacks.get(app_name.lower(), [{"content": f"Historical data logged for {app_name}."}])

    def seed_sample_data(self):
        """Pre-populates sample events into Hindsight banks for demo readiness."""
        sample_data = {
            "Rapido": "Rapido shifts to zero-commission driver model and launches flat-fee food delivery.",
            "Zomato": "Zomato hikes platform fees to ₹17.58 per order to boost unit economics.",
            "Swiggy": "Swiggy bundled quick-commerce Instamart with food delivery via Swiggy One membership.",
            "Uber": "Uber expanded high-margin Reserve rides and corporate subscription passes."
        }
        results = {}
        for app, signal in sample_data.items():
            results[app] = self.ingest_app_signal(app, signal, source="seed_timeline")
        return results

    def compare_apps(self, primary_app: str, rival_app: str, market_signal: str) -> dict:
        """Processes live signal, recalls memories from both banks, and generates Groq synthesis."""
        # 1. Retain live signal
        self.ingest_app_signal(primary_app, market_signal, source="live_dashboard_input")

        # 2. Recall memory context for both apps
        primary_memories = self.recall_history(primary_app, market_signal)
        rival_memories = self.recall_history(rival_app, "Pricing, commission structure, and margin strategy")

        # 3. Formulate LLM synthesis prompt
        prompt = f"""
        PRIMARY APP: {primary_app}
        NEW MARKET SIGNAL: {market_signal}
        {primary_app} RECALLED MEMORY: {primary_memories}
        {rival_app} RECALLED MEMORY: {rival_memories}

        Generate an Executive Counter-Strategy Report:
        1. **Market Impact & Pricing Advantage**: How does this move affect consumer pricing and driver/merchant margins?
        2. **Threat Level to {rival_app}**: Evaluate churn and market share risks in Tier-1 vs Tier-2 cities.
        3. **Recommended Sales & Strategy Counter-Actions**: Give 3 concrete moves for {rival_app} to defend its market share.
        """

        # 4. Generate report via Groq LLM
        if groq_client:
            try:
                response = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": prompt}]
                )
                report = response.choices[0].message.content
            except Exception as e:
                report = f"⚠️ Groq Inference Error: {str(e)}\n\nDisplaying calculated summary fallback."
        else:
            report = (
                f"### Executive Brief: {primary_app} vs {rival_app}\n\n"
                f"**1. Pricing Move:** {primary_app} introduced: *\"{market_signal}\"*\n"
                f"**2. Strategic Threat:** Puts pressure on {rival_app}'s margin structure and commission model.\n"
                f"**3. Recommended Counter-Action:** Accelerate subscription loyalty passes and merchant lock-in incentives."
            )

        return {
            "report": report,
            "primary_context": primary_memories,
            "rival_context": rival_memories
        }


# Backward compatibility aliases
CompetitiveIntelAgent = AppComparisonAgent