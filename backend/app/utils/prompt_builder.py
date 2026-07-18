from typing import Dict, Any, List

class PromptBuilder:
    def __init__(self):
        pass

    def build_system_context(self, company_profile: Dict[str, Any], metrics: Dict[str, Any]) -> str:
        """
        Builds the baseline system instruction injection for Gemma, anchoring its identity
        to the specific company and metrics.
        """
        company_name = company_profile.get("name", "our company")
        industry = company_profile.get("industry", "general SME")
        cash_balance = company_profile.get("cash_balance", 0.0)
        
        ar = metrics.get("accounts_receivable", 0.0)
        ap = metrics.get("accounts_payable", 0.0)
        
        return (
            f"You are the Core Intelligence Agent of Stratify (SME OS), specifically configured for '{company_name}' (Industry: {industry}).\n"
            f"Financial Baseline:\n"
            f"- Current Cash Balance: ${cash_balance:,.2f}\n"
            f"- Accounts Receivable (AR): ${ar:,.2f}\n"
            f"- Accounts Payable (AP): ${ap:,.2f}\n"
            f"Your role is to analyze inputs and provide mathematically grounded, context-aware operational suggestions."
        )

    def build_chat_prompt(self, user_question: str, context: Dict[str, Any]) -> str:
        """
        Consolidates recent business events, relevant entities (customers, suppliers, products),
        and the user's question into one optimized prompt.
        """
        recent_events = context.get("recent_events", [])
        customers = context.get("customers", [])
        suppliers = context.get("suppliers", [])
        products = context.get("products", [])
        
        # Build section for events
        events_str = ""
        if recent_events:
            events_str = "\n".join([f"- [{e.get('timestamp')}] {e.get('severity')}: {e.get('description')}" for e in recent_events])
        else:
            events_str = "- No recent events logged."
            
        # Build section for customers
        cust_str = ""
        if customers:
            cust_str = "\n".join([f"- {c.get('name')} (CLV: ${c.get('clv'):,.2f}, Credit score: {c.get('credit_score')})" for c in customers[:5]])
        else:
            cust_str = "- No active customer records."
            
        # Build section for suppliers
        supp_str = ""
        if suppliers:
            supp_str = "\n".join([f"- {s.get('name')} (Reliability: {s.get('reliability_score')*100:.1f}%)" for s in suppliers[:5]])
        else:
            supp_str = "- No active supplier records."
            
        # Build section for products
        prod_str = ""
        if products:
            prod_str = "\n".join([f"- SKU: {p.get('sku')} | {p.get('name')} (Price: ${p.get('price'):,.2f}, Stock: {p.get('stock_level')})" for p in products[:5]])
        else:
            prod_str = "- No product records."

        return (
            f"### Dynamic Context Profile\n\n"
            f"#### Recent Business Events:\n{events_str}\n\n"
            f"#### Key Customers:\n{cust_str}\n\n"
            f"#### Key Suppliers:\n{supp_str}\n\n"
            f"#### Stock & Product Catalog:\n{prod_str}\n\n"
            f"### User Question:\n\"{user_question}\"\n\n"
            f"Answer the user's question clearly. Reference items in the context profile when relevant."
        )

    def build_brief_prompt(self, metrics: Dict[str, Any], recent_events: List[Dict[str, Any]]) -> str:
        """
        Creates the prompt context for generating the morning executive brief.
        """
        events_str = "\n".join([f"- {e.get('severity')}: {e.get('description')}" for e in recent_events[:10]])
        return (
            f"Generate a structured Morning Executive Brief for the business.\n"
            f"Current Stats:\n"
            f"- Total Sales Volume: ${metrics.get('total_sales_volume', 0.0):,.2f}\n"
            f"- Accounts Receivable: ${metrics.get('accounts_receivable', 0.0):,.2f}\n"
            f"- Accounts Payable: ${metrics.get('accounts_payable', 0.0):,.2f}\n\n"
            f"Recent Events:\n{events_str}\n\n"
            f"Format the response as pure JSON matching this exact structure:\n"
            f"{{\n"
            f"  \"morning_summary\": \"(Paragraph summary of the business health)\",\n"
            f"  \"critical_alerts\": [\"(alert 1)\", \"(alert 2)\"],\n"
            f"  \"top_opportunities\": [\"(opportunity 1)\", \"(opportunity 2)\"],\n"
            f"  \"business_health_summary\": \"(Stable/Improving/Declining)\",\n"
            f"  \"top_5_actions\": [\"(action 1)\", \"(action 2)\", \"(action 3)\", \"(action 4)\", \"(action 5)\"]\n"
            f"}}\n"
            f"Output ONLY valid JSON. No markdown wrappers like ```json."
        )
