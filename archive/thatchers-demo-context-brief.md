# Signals Demo Context Brief (Thatchers)

## Purpose
Provide a concise context brief for Notebook LLM to recommend which trend documents (from a larger library of ~30) should be pulled into the demo project. The demo uses a fictional hotel use case that is backed by real, anonymized hospitality research data.

## Product Context
Signals is a platform that connects multiple knowledge bases and synthesizes insights across them. It supports traceability to sources and can apply a specific lens (for example, jobs to be done) across mixed qualitative inputs.

## Demo Scenario
We will show a hospitality-focused demo to illustrate Signals capabilities for Thatchers. The demo is a proxy for how Signals could help Thatchers synthesize cross-functional knowledge and align on decisions. We will also ask Thatchers about their current business challenges to evaluate Signals fit.

## Data Sources (Use These)
- Trend reports library (about 30 documents; select a subset)
- Anonymized interview transcripts (primary): `customer interviews/*.anonymized.md`
- Memory stories (short narratives): `stories.md`
- Optional synthesis of stories: `stories-synthesis.md`
- Optional synthetic inputs for richer demo context: concierge notes, marketing director perspective
- Optional reference material: `platform-overview.md`, `prompt-system-overview.md`

## Anonymization Notes
- The interview data is already anonymized.
- Trend documents do not need additional anonymization. If a trend report mentions real brands, that is acceptable.

## Output Intent (Notebook LLM)
Recommend which trend documents to import into the demo project. Provide brief reasons for each pick, focusing on documents that best illuminate near-term hospitality trends and create interesting contrast with the interview stories. The result should help us decide what files to drag into our project for a compelling demo.
