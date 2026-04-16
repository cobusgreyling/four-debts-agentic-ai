# The Four Debts of Agentic AI

Your AI agent works. It answers questions, calls APIs, completes tasks. The demo was flawless, but ...

... why, three months into production, is it quietly destroying value?

The answer lies in a concept from a recent paper by Vera Vishnyakova...

...every layer of agent engineering you skip becomes debt that compounds until it breaks something you care about...

The paper introduces a cumulative four-level pyramid for agent engineering maturity.
But the most useful way to read it isn't as a maturity model...it's as a **debt model**.
Each missing layer is a specific category of debt, with specific consequences and a predictable moment of failure.

Here are the four debts...

---

## Debt 1: Prompt Debt

**What you skipped:** precision in how you instruct the model...

The Pyramid's Level 1 is prompt engineering...the craft of composing queries.
It's the base of everything.
A prompt sits at the heart of an AI Agent.
The paper is careful not to declare it dead ("To declare prompt engineering dead is a mistake").
But frames it as a craft that the industry wrapped in romantic mythology..."prompt whisperer,"
"10 magic prompts,"
"the art of talking to AI."

The problem isn't that prompting doesn't work. It's that most teams never move past it.
They mistake a successful demo for a production-ready solution.

**When this debt comes due:** the agent produces inconsistent outputs.
Edge cases multiply...
The team responds by adding more prompt variations, which creates a maintenance burden that grows with every new scenario.
You're patching a system that was never engineered.

---

## Debt 2: Context Debt

**What you skipped:** designing the informational environment in which the agent operates.

Context engineering is the paper's core contribution.
It's defined not as better prompting, but as **systems engineering**...managing what the agent sees at every step.
How information flows between sub-agents, what gets compressed and what gets discarded.

The paper proposes five quality criteria for context:
- relevance
- sufficiency
- isolation
- economy
- provenance

Most often teams satisfy zero of these intentionally.

**When this debt comes due:** the agent "gets lost in the middle" - at step 47 of a 50-step workflow, it fixates on stale data from step 3.
Or a sub-agent with payment system access receives an instruction from a compromised agent because visibility boundaries were never designed.
Context debt doesn't surface in testing. It surfaces at scale, under load, in production.

---

## Debt 3: Intent Debt

**What you skipped:** Encoding what the agent should actually optimise for.

This is the most expensive debt, and Klarna is the case study.

Klarna's AI agent handled two-thirds of all customer inquiries, performing work equivalent to 853 employees, saving ~$60 million.
It was, by every technical metric, a success.
Then the CEO publicly acknowledged that service quality had suffered.
Forrester called it an "AI overpivot."
The company began rehiring humans.

The paper's diagnosis? A **dual deficit**.
The context deficit meant the agent lacked access to customer history, brand tone and loyalty policies.
But the deeper failure was an intent deficit, the balance between cost savings and customer loyalty was never formalised.
The agent optimised cost per token, not the value of customer relationships.

As Huryn puts it: *"Context without intent is noise."*

An agent receiving all relevant data but lacking formalised priorities will optimise the most readable metric, call cost, response speed, task completion rate...rather than what truly matters: customer loyalty, brand perception, regulatory compliance.

**When this debt comes due...** the agent works technically but fails strategically.
Revenue metrics look good for two quarters while NPS quietly craters.
By the time leadership notices, the reputational damage is done.

---

## Debt 4: Specification Debt

**What you skipped:** Formalising corporate knowledge into machine-readable infrastructure.

The paper's highest level, specification engineering, addresses what happens when you scale from one agent to many.
An individual agent can operate with encoded intent.
A fleet of agents across departments, geographies and business units needs something more...a machine-readable corpus of corporate policies, quality standards, operational procedures, and organisational agreements.

Without this, every new agent team reinvents governance from scratch.
Compliance rules are encoded inconsistently.
Policy updates don't propagate. The multi-agent system becomes what the paper calls a "distributed monolith with an illusion of independence."

**When this debt comes due...** An agent in one division makes a decision that contradicts a policy another division depends on.
No single agent was wrong. The aggregate outcome was.
Formal responsibility rests with a human who had no real influence over what happened...what the literature calls a "moral crumple zone."

---

## The Principal Trap

The paper identifies what makes these debts so dangerous in 2026, the creation threshold has collapsed.

No-code tools compress the path from idea to deployed agent to hours.
What once required an engineering team now requires a browser tab.
The trap: *"every agent created without attention to the upper levels of the pyramid carries context debt and intent debt that will eventually come due."*

The paper's conclusion is ultimately about control:

- **Whoever controls the agent's context** controls its behaviour.
- **Whoever controls the agent's intent** controls its strategy.
- **Whoever controls the agent's specifications** controls its scale.

This isn't a transition from human control to machine autonomy.
It's a transition from the ad hoc to the engineered.
At each level, the human role becomes more strategic and less tactical, more architectural and less artisanal.

---

*Based on: Vishnyakova, V.V. (2026). "Context Engineering: From Prompts to Corporate Multi-Agent Architecture." [arXiv:2603.09619v2](https://arxiv.org/abs/2603.09619)*
