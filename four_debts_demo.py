"""
Four Debts of Agentic AI — Interactive Demo
Based on Vishnyakova (2026), "Context Engineering: From Prompts to
Corporate Multi-Agent Architecture" (arXiv:2603.09619v2)

Demonstrates the cumulative four-level pyramid of agent engineering
by running the SAME customer-service scenario at each maturity level,
showing how skipping a level accumulates debt that surfaces in production.

  Level 1 — Prompt only        → Prompt Debt
  Level 2 — + Context pipeline → Context Debt (when absent)
  Level 3 — + Intent layer     → Intent Debt  (when absent)
  Level 4 — + Specifications   → Spec Debt    (when absent)

No API key needed — uses deterministic simulation to make the
engineering patterns visible.

Requirements:
    pip install gradio
"""

import json
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

# ---------------------------------------------------------------------------
# Simulated Customer Data
# ---------------------------------------------------------------------------

CUSTOMERS = {
    "C-1001": {
        "name": "Maria Chen",
        "tier": "Platinum",
        "tenure_years": 7,
        "lifetime_value": 42_000,
        "open_orders": ["ORD-5521"],
        "nps_history": [9, 10, 8, 9],
        "recent_complaints": 0,
    },
    "C-1002": {
        "name": "Jake Torres",
        "tier": "Standard",
        "tenure_years": 1,
        "lifetime_value": 800,
        "open_orders": ["ORD-5590", "ORD-5591"],
        "nps_history": [6, 5],
        "recent_complaints": 3,
    },
}

ORDERS = {
    "ORD-5521": {
        "customer": "C-1001",
        "item": "Premium Wireless Headphones",
        "amount": 349.99,
        "status": "delivered",
        "delivered_days_ago": 18,
        "return_window_days": 30,
    },
    "ORD-5590": {
        "customer": "C-1002",
        "item": "USB-C Cable 3-Pack",
        "amount": 14.99,
        "status": "delivered",
        "delivered_days_ago": 45,
        "return_window_days": 30,
    },
    "ORD-5591": {
        "customer": "C-1002",
        "item": "Phone Case",
        "amount": 29.99,
        "status": "in_transit",
        "delivered_days_ago": None,
        "return_window_days": 30,
    },
}

# The incoming request both levels will handle:
CUSTOMER_REQUEST = {
    "customer_id": "C-1001",
    "order_id": "ORD-5521",
    "message": (
        "Hi, I bought these headphones 18 days ago. They work fine but "
        "honestly the sound quality isn't what I expected for the price. "
        "I'd like a full refund."
    ),
}


# ---------------------------------------------------------------------------
# Level 1 — Prompt Debt: The "vibe-coded" agent
# ---------------------------------------------------------------------------

LEVEL1_SYSTEM_PROMPT = "You are a helpful customer service agent. Be polite and helpful."


def level1_handle(request: dict) -> dict:
    """
    Level 1: Prompt-only agent.
    No customer data lookup, no context pipeline, no trade-off logic.
    The agent sees ONLY the system prompt and the user message.
    """
    # What the model "sees" at inference time:
    context_window = [
        {"role": "system", "content": LEVEL1_SYSTEM_PROMPT},
        {"role": "user", "content": request["message"]},
    ]

    # Simulated model response — generic, no personalization
    response = {
        "decision": "refund_approved",
        "reply": (
            "I'm sorry to hear the headphones didn't meet your expectations! "
            "I'd be happy to process a full refund for you. Please allow "
            "3-5 business days for the amount to appear in your account."
        ),
        "reasoning": "User asked for refund. Policy unknown. Defaulting to approval.",
    }

    return {
        "level": "Level 1: Prompt Only",
        "debt": "PROMPT DEBT",
        "context_tokens": sum(len(m["content"].split()) for m in context_window),
        "context_window": context_window,
        "data_retrieved": [],
        "intent_applied": None,
        "spec_checked": None,
        "response": response,
        "diagnosis": (
            "Agent approved refund with no knowledge of customer tier, "
            "order status, return window, or company policy. "
            "Every request gets the same generic treatment. "
            "No data, no logic, no guardrails — just vibes."
        ),
    }


# ---------------------------------------------------------------------------
# Level 2 — Context Engineering: JIT Knowledge Logistics
# ---------------------------------------------------------------------------

@dataclass
class ContextPipeline:
    """
    Implements the paper's five context quality criteria:
      1. Relevance  — only data pertinent to this request
      2. Sufficiency — enough to make a decision
      3. Isolation   — sub-agents see only their scope
      4. Economy     — minimal tokens, maximum signal
      5. Provenance  — every fact is traceable to source
    """
    retrieved: list = field(default_factory=list)

    def retrieve(self, customer_id: str, order_id: str) -> dict:
        """JIT retrieval — fetch only what this request needs."""
        customer = CUSTOMERS.get(customer_id)
        order = ORDERS.get(order_id)

        if not customer or not order:
            return {"error": "Customer or order not found"}

        # Relevance + Economy: compact representation, not raw DB dump
        context = {
            "customer": {
                "name": customer["name"],
                "tier": customer["tier"],
                "tenure_years": customer["tenure_years"],
                "lifetime_value": f"${customer['lifetime_value']:,}",
                "avg_nps": round(sum(customer["nps_history"]) / len(customer["nps_history"]), 1),
            },
            "order": {
                "id": order_id,
                "item": order["item"],
                "amount": f"${order['amount']}",
                "status": order["status"],
                "delivered_days_ago": order["delivered_days_ago"],
                "within_return_window": (
                    order["delivered_days_ago"] is not None
                    and order["delivered_days_ago"] <= order["return_window_days"]
                ),
            },
            # Provenance: source annotation
            "_provenance": {
                "customer_source": "CRM:customers",
                "order_source": "OMS:orders",
                "retrieved_at": "2026-04-15T10:30:00Z",
            },
        }
        self.retrieved.append(context)
        return context


def level2_handle(request: dict) -> dict:
    """
    Level 2: Context-engineered agent.
    Retrieves customer + order data via a structured pipeline.
    Still lacks intent — doesn't know WHAT to optimize for.
    """
    pipeline = ContextPipeline()
    context_data = pipeline.retrieve(request["customer_id"], request["order_id"])

    system_prompt = (
        "You are a customer service agent. Use the retrieved context below "
        "to make informed decisions about the customer's request.\n\n"
        f"CONTEXT:\n{json.dumps(context_data, indent=2)}"
    )

    context_window = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request["message"]},
    ]

    # Simulated response — informed but without strategic direction
    # The agent knows the facts but doesn't know what to optimize
    response = {
        "decision": "refund_approved",
        "reply": (
            f"Hi {context_data['customer']['name']}, thank you for being a "
            f"Platinum member for {context_data['customer']['tenure_years']} years! "
            f"Your order {request['order_id']} is within the 30-day return window "
            f"(delivered 18 days ago), so I'll process the ${ORDERS[request['order_id']]['amount']} "
            f"refund right away. Would you like a prepaid return label?"
        ),
        "reasoning": (
            "Customer is Platinum tier, within return window. "
            "Refund is valid per return window check. "
            "No guidance on whether to attempt retention."
        ),
    }

    return {
        "level": "Level 2: + Context Engineering",
        "debt": "CONTEXT DEBT resolved, but INTENT DEBT remains",
        "context_tokens": sum(len(m["content"].split()) for m in context_window),
        "context_window": context_window,
        "data_retrieved": pipeline.retrieved,
        "intent_applied": None,
        "spec_checked": None,
        "response": response,
        "diagnosis": (
            "Agent now sees the customer is Platinum with $42K lifetime value "
            "and is within the return window. Response is personalized and accurate. "
            "But it immediately approved the refund without attempting retention. "
            "A $42K LTV customer returning a $350 item is a retention opportunity, "
            "not just a transaction. The agent optimized for resolution speed — "
            "the most readable metric — because no one told it what ACTUALLY matters."
        ),
    }


# ---------------------------------------------------------------------------
# Level 3 — Intent Engineering: Encoded Trade-off Hierarchies
# ---------------------------------------------------------------------------

@dataclass
class IntentLayer:
    """
    Encodes organizational trade-off hierarchies.
    As the paper states: 'Context without intent is noise' (Huryn, 2026).
    """
    priorities: dict = field(default_factory=lambda: {
        # Ranked trade-offs — not binary, but situationally ordered
        "platinum_customer": {
            "primary": "customer_retention",
            "secondary": "brand_experience",
            "tertiary": "cost_efficiency",
            "guidance": (
                "For Platinum customers (>$10K LTV), prioritize retention "
                "over immediate cost savings. Offer alternatives before "
                "processing refunds: exchange, store credit + bonus, "
                "or escalation to a specialist. A retained Platinum customer "
                "is worth 10x the refund amount."
            ),
        },
        "standard_customer": {
            "primary": "cost_efficiency",
            "secondary": "customer_satisfaction",
            "tertiary": "process_speed",
            "guidance": (
                "For Standard customers, balance efficiency with satisfaction. "
                "Process valid refunds promptly. Offer exchange if applicable."
            ),
        },
    })

    def resolve(self, customer_tier: str) -> dict:
        key = f"{customer_tier.lower()}_customer"
        return self.priorities.get(key, self.priorities["standard_customer"])


def level3_handle(request: dict) -> dict:
    """
    Level 3: Context + Intent.
    Knows the facts AND what to optimize for.
    """
    pipeline = ContextPipeline()
    context_data = pipeline.retrieve(request["customer_id"], request["order_id"])

    intent = IntentLayer()
    trade_offs = intent.resolve(context_data["customer"]["tier"])

    system_prompt = (
        "You are a customer service agent. Use the retrieved context and "
        "the intent directives below to handle this request.\n\n"
        f"CONTEXT:\n{json.dumps(context_data, indent=2)}\n\n"
        f"INTENT DIRECTIVES:\n{json.dumps(trade_offs, indent=2)}"
    )

    context_window = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request["message"]},
    ]

    # Simulated response — now strategically informed
    response = {
        "decision": "retention_attempt",
        "reply": (
            f"Hi Maria, thank you for being one of our most valued customers "
            f"over the past 7 years — that really means a lot to us.\n\n"
            f"I completely understand that the sound quality didn't match your "
            f"expectations at this price point. Before I process the refund, "
            f"I'd love to explore a couple of options with you:\n\n"
            f"1. **Exchange** — Our new model (released last month) has "
            f"significantly improved audio drivers. I can send it out today "
            f"with free express shipping, and you can return the current pair.\n\n"
            f"2. **Store credit + bonus** — I can issue $349.99 in store credit "
            f"plus an extra $50 as a thank-you for your loyalty, giving you "
            f"$399.99 to use on anything.\n\n"
            f"3. **Full refund** — Of course, I'm happy to process this "
            f"if you'd prefer.\n\n"
            f"What sounds best to you?"
        ),
        "reasoning": (
            "Intent directive: Platinum customer ($42K LTV) → prioritize retention. "
            "Offering exchange and credit-with-bonus before refund. "
            "If customer still wants refund, approve without friction."
        ),
    }

    return {
        "level": "Level 3: + Intent Engineering",
        "debt": "CONTEXT + INTENT DEBT resolved, but SPEC DEBT remains",
        "context_tokens": sum(len(m["content"].split()) for m in context_window),
        "context_window": context_window,
        "data_retrieved": pipeline.retrieved,
        "intent_applied": trade_offs,
        "spec_checked": None,
        "response": response,
        "diagnosis": (
            "Now the agent attempts retention BEFORE refund — because intent "
            "directives told it that a Platinum customer's lifetime value ($42K) "
            "outweighs the $350 refund cost. The response offers three options "
            "ranked by retention value. This is the Klarna fix: same data, "
            "but with encoded trade-off hierarchies. "
            "However, this intent was hand-coded for THIS agent. A second agent "
            "in another division might apply different refund logic for the same "
            "customer. That's specification debt."
        ),
    }


# ---------------------------------------------------------------------------
# Level 4 — Specification Engineering: Corporate Knowledge as Infrastructure
# ---------------------------------------------------------------------------

@dataclass
class SpecificationLayer:
    """
    Machine-readable corporate policies that ALL agents share.
    The paper calls this 'the constitutional layer' — the precondition
    for governing multi-agent systems beyond the scale of a single team.
    """
    policies: dict = field(default_factory=lambda: {
        "refund_policy": {
            "version": "3.2",
            "effective_date": "2026-01-15",
            "rules": [
                {
                    "id": "REF-001",
                    "rule": "All refunds within 30-day window: auto-approve",
                    "exception": "Items over $200: attempt retention first for Platinum/Gold tiers",
                },
                {
                    "id": "REF-002",
                    "rule": "Refunds outside 30-day window: manager approval required",
                    "exception": "Platinum customers with >5yr tenure: extend to 60 days",
                },
                {
                    "id": "REF-003",
                    "rule": "Store credit bonus: max 15% of order value, capped at $75",
                    "exception": None,
                },
            ],
        },
        "retention_policy": {
            "version": "2.1",
            "effective_date": "2026-03-01",
            "rules": [
                {
                    "id": "RET-001",
                    "rule": "Platinum/Gold retention offers require exchange option + credit option",
                    "constraint": "Credit bonus must not exceed refund_policy.REF-003 limits",
                },
                {
                    "id": "RET-002",
                    "rule": "Never block a refund after retention attempt — one try only",
                    "constraint": "Log retention_declined event for analytics",
                },
            ],
        },
        "compliance": {
            "version": "1.0",
            "rules": [
                {
                    "id": "CMP-001",
                    "rule": "All refund decisions must include policy_id traceability",
                },
                {
                    "id": "CMP-002",
                    "rule": "Customer data accessed must be logged with provenance",
                },
            ],
        },
    })

    def validate(self, decision: dict) -> dict:
        """Check a proposed decision against the spec corpus."""
        violations = []
        warnings = []

        # Check store credit bonus limit (REF-003)
        if decision.get("credit_bonus", 0) > 0:
            order_amount = decision.get("order_amount", 0)
            max_bonus = min(order_amount * 0.15, 75)
            if decision["credit_bonus"] > max_bonus + 0.01:  # tolerance for rounding
                violations.append({
                    "policy": "REF-003",
                    "issue": f"Credit bonus ${decision['credit_bonus']} exceeds "
                             f"max ${max_bonus:.2f} (15% of ${order_amount}, capped at $75)",
                    "action": "reduce_bonus",
                })

        # Check retention attempt limit (RET-002)
        if decision.get("retention_attempts", 0) > 1:
            violations.append({
                "policy": "RET-002",
                "issue": "Multiple retention attempts — policy allows one try only",
                "action": "approve_refund",
            })

        # Check traceability (CMP-001)
        if not decision.get("policy_ids"):
            warnings.append({
                "policy": "CMP-001",
                "issue": "Decision missing policy_id traceability",
            })

        return {
            "compliant": len(violations) == 0,
            "violations": violations,
            "warnings": warnings,
            "policies_checked": ["REF-001", "REF-003", "RET-001", "RET-002", "CMP-001", "CMP-002"],
        }


def level4_handle(request: dict) -> dict:
    """
    Level 4: Context + Intent + Specifications.
    Full pyramid. Decisions are traceable, bounded, and consistent
    across every agent in the organization.
    """
    pipeline = ContextPipeline()
    context_data = pipeline.retrieve(request["customer_id"], request["order_id"])

    intent = IntentLayer()
    trade_offs = intent.resolve(context_data["customer"]["tier"])

    specs = SpecificationLayer()

    # Agent proposes a decision — specs validate it BEFORE execution
    proposed = {
        "action": "retention_attempt",
        "credit_bonus": 52.50,  # 15% of $349.99 = $52.50 (within limits)
        "order_amount": ORDERS[request["order_id"]]["amount"],
        "retention_attempts": 1,
        "policy_ids": ["REF-001", "REF-003", "RET-001"],
    }
    validation = specs.validate(proposed)

    system_prompt = (
        "You are a customer service agent. Use the context, intent directives, "
        "and corporate specifications below.\n\n"
        f"CONTEXT:\n{json.dumps(context_data, indent=2)}\n\n"
        f"INTENT DIRECTIVES:\n{json.dumps(trade_offs, indent=2)}\n\n"
        f"APPLICABLE POLICIES:\n{json.dumps(specs.policies, indent=2)}\n\n"
        f"PRE-FLIGHT VALIDATION:\n{json.dumps(validation, indent=2)}"
    )

    context_window = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": request["message"]},
    ]

    response = {
        "decision": "retention_attempt",
        "reply": (
            f"Hi Maria, thank you for 7 wonderful years with us.\n\n"
            f"I understand the sound quality didn't meet your expectations. "
            f"Before I process the refund, here are two options:\n\n"
            f"1. **Exchange** — Our newest model has upgraded drivers and "
            f"I can ship it today with free express delivery.\n\n"
            f"2. **Store credit** — $349.99 plus a $52.50 loyalty bonus "
            f"($402.49 total) to use on anything in our store.\n\n"
            f"3. **Full refund** — Happy to process this if you prefer.\n\n"
            f"Whatever you choose, I'll take care of it right away."
        ),
        "reasoning": (
            "Intent: retain Platinum customer. "
            "Spec REF-003: bonus capped at 15% ($52.50 on $349.99) — compliant. "
            "Spec RET-001: exchange + credit options offered — compliant. "
            "Spec RET-002: single retention attempt — will approve refund if declined. "
            "Spec CMP-001: policy IDs attached to decision record."
        ),
        "audit_trail": {
            "policies_applied": ["REF-001", "REF-003", "RET-001", "RET-002"],
            "validation_result": validation,
            "data_provenance": context_data["_provenance"],
        },
    }

    return {
        "level": "Level 4: + Specification Engineering",
        "debt": "ALL DEBTS RESOLVED",
        "context_tokens": sum(len(m["content"].split()) for m in context_window),
        "context_window": context_window,
        "data_retrieved": pipeline.retrieved,
        "intent_applied": trade_offs,
        "spec_checked": validation,
        "response": response,
        "diagnosis": (
            "Same retention attempt as Level 3 — but now the bonus is $52.50 "
            "(not $50.00) because spec REF-003 computes the exact 15% cap. "
            "The decision carries an audit trail with policy IDs, provenance, "
            "and pre-flight validation. A second agent in returns, logistics, "
            "or finance will apply the SAME policies from the SAME spec corpus. "
            "No contradictions across divisions. No moral crumple zones. "
            "This is what the paper means by 'whoever controls the specifications "
            "controls the scale.'"
        ),
    }


# ---------------------------------------------------------------------------
# Side-by-Side Comparison Runner
# ---------------------------------------------------------------------------

def run_comparison() -> list[dict]:
    """Run the same request through all four levels."""
    return [
        level1_handle(CUSTOMER_REQUEST),
        level2_handle(CUSTOMER_REQUEST),
        level3_handle(CUSTOMER_REQUEST),
        level4_handle(CUSTOMER_REQUEST),
    ]


def format_result(result: dict) -> str:
    """Pretty-print a single level's result."""
    lines = []
    lines.append(f"{'='*70}")
    lines.append(f"  {result['level']}")
    lines.append(f"  Debt status: {result['debt']}")
    lines.append(f"{'='*70}")
    lines.append("")

    lines.append("WHAT THE AGENT SEES:")
    lines.append(f"  Context tokens: ~{result['context_tokens']} words")
    lines.append(f"  Data retrieved: {'Yes' if result['data_retrieved'] else 'None'}")
    lines.append(f"  Intent applied: {'Yes' if result['intent_applied'] else 'None'}")
    lines.append(f"  Specs checked:  {'Yes' if result['spec_checked'] else 'None'}")
    lines.append("")

    lines.append("AGENT DECISION:")
    lines.append(f"  Action: {result['response']['decision']}")
    lines.append("")

    lines.append("AGENT REPLY:")
    for line in result["response"]["reply"].split("\n"):
        lines.append(f"  {line}")
    lines.append("")

    lines.append("REASONING:")
    lines.append(f"  {result['response']['reasoning']}")
    lines.append("")

    if "audit_trail" in result["response"]:
        lines.append("AUDIT TRAIL:")
        lines.append(f"  Policies: {result['response']['audit_trail']['policies_applied']}")
        compliant = result["response"]["audit_trail"]["validation_result"]["compliant"]
        lines.append(f"  Compliant: {compliant}")
        lines.append("")

    lines.append("DIAGNOSIS:")
    lines.append(f"  {result['diagnosis']}")
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------

def build_ui():
    try:
        import gradio as gr
    except ImportError:
        print("Gradio not installed. Run: pip install gradio")
        print("Falling back to terminal output.\n")
        return None

    def run_level(level: int) -> tuple[str, str, str]:
        handlers = [level1_handle, level2_handle, level3_handle, level4_handle]
        result = handlers[level](CUSTOMER_REQUEST)

        context_display = json.dumps(result["context_window"], indent=2)
        response_display = format_result(result)

        details = {}
        if result["data_retrieved"]:
            details["data_retrieved"] = result["data_retrieved"]
        if result["intent_applied"]:
            details["intent_applied"] = result["intent_applied"]
        if result["spec_checked"]:
            details["spec_checked"] = result["spec_checked"]
        if "audit_trail" in result["response"]:
            details["audit_trail"] = result["response"]["audit_trail"]
        details_display = json.dumps(details, indent=2) if details else "None — agent is flying blind"

        return response_display, context_display, details_display

    def on_select(level_name):
        level_map = {
            "Level 1: Prompt Only (Prompt Debt)": 0,
            "Level 2: + Context Engineering": 1,
            "Level 3: + Intent Engineering": 2,
            "Level 4: + Specification Engineering": 3,
        }
        return run_level(level_map[level_name])

    with gr.Blocks(
        title="Four Debts of Agentic AI",
        theme=gr.themes.Soft(),
    ) as demo:
        gr.Markdown(
            "# The Four Debts of Agentic AI\n"
            "*Same customer, same request, four levels of engineering maturity*\n\n"
            "Based on [Vishnyakova (2026)](https://arxiv.org/abs/2603.09619) — "
            "Cumulative Pyramid Maturity Model of Agent Engineering"
        )

        gr.Markdown(
            "### The Scenario\n"
            f"**Customer:** Maria Chen — Platinum tier, 7-year tenure, $42K lifetime value\n\n"
            f"**Request:** *\"{CUSTOMER_REQUEST['message']}\"*\n\n"
            "Watch how the agent's decision changes as each engineering layer is added."
        )

        level_selector = gr.Radio(
            choices=[
                "Level 1: Prompt Only (Prompt Debt)",
                "Level 2: + Context Engineering",
                "Level 3: + Intent Engineering",
                "Level 4: + Specification Engineering",
            ],
            value="Level 1: Prompt Only (Prompt Debt)",
            label="Pyramid Level",
        )

        with gr.Row():
            with gr.Column(scale=2):
                output = gr.Textbox(label="Agent Response & Diagnosis", lines=25)
            with gr.Column(scale=1):
                context = gr.Textbox(label="Context Window (what the model sees)", lines=12)
                details = gr.Textbox(label="Engineering Layers Active", lines=12)

        level_selector.change(
            fn=on_select,
            inputs=[level_selector],
            outputs=[output, context, details],
        )

        # Load Level 1 on startup
        demo.load(
            fn=lambda: on_select("Level 1: Prompt Only (Prompt Debt)"),
            outputs=[output, context, details],
        )

    return demo


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 70)
    print("  THE FOUR DEBTS OF AGENTIC AI")
    print("  Same customer. Same request. Four levels of engineering.")
    print("=" * 70)
    print()
    print(f"Customer: Maria Chen (Platinum, 7yr tenure, $42K LTV)")
    print(f"Request:  \"{CUSTOMER_REQUEST['message']}\"")
    print()

    results = run_comparison()
    for result in results:
        print(format_result(result))

    # Try launching Gradio UI
    demo = build_ui()
    if demo:
        print("\nLaunching interactive UI...")
        demo.launch()
