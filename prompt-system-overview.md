# Prompt and Specifications System Overview

This document explains where prompts/specifications live, how they are assembled, and how they flow through the system.

## 1) Where prompts/specifications are stored

### A. Per-iteration specifications (primary user-editable prompt source)
- **Storage**: `ai_generation_iteration.specifications` in the database.
- **Used by**: Knowledge Curator iterations and Strategic Synthesis iterations.
- **Why it matters**: This is the main “prompt text” that users edit and the system later injects into LLM prompts.

### B. Knowledge Curator default specifications (node-level default)
- **Storage**: `workflow_node.data.defaultSpecifications` for Knowledge Curator nodes.
- **Fallback**: `DEFAULT_SPECIFICATIONS` constant in `apps/server/src/workflows/types/knowledge-curator.ts`.
- **Used by**: Initial Knowledge Curator iteration creation when a file is ingested.

### C. Framework Specialist specifications (type + node overrides)
- **Type defaults**: `framework_specialist.defaultSpecifications`.
- **Node-specific supplements**: `workflow_node.data.supplementalSpecifications`.
- **Used by**: Strategic Synthesis prompt assembly (as methodological context).

### D. Strategic Synthesis default first-iteration specs
- **Storage**: In-code string `defaultFirstIterationSpecs` inside `StrategicSynthesisService`.
- **Used by**: Creating the very first Strategic Synthesis iteration if no prior iteration exists.

### E. Prompt-related artifacts (outputs, not inputs)
- **Digest outputs**: `ArtifactType.KNOWLEDGE_ITEM_DIGEST` stores generated markdown plus metadata.
- **Strategic Synthesis outputs**: `ArtifactType.STRATEGIC_SYNTHESIS_OUTPUT` stores final synthesis content.
- **Process summaries**: `ArtifactType.STRATEGIC_SYNTHESIS_PROCESS_SUMMARY` stores a generated narrative of the generation steps.

`ArtifactType.KNOWLEDGE_ITEM_SPECIFICATION` exists as a type, but the current job flow does not create specification artifacts; iteration specifications live on the `ai_generation_iteration` row.

## 2) How prompts are assembled and used

### Knowledge Curator: file → embeddings → digest

1. **File upload** creates a Knowledge Item + File Artifact.
2. **Embedding job** splits the document, embeds chunks, stores chunk IDs in a RAG artifact.
3. **Initial iteration** is created with specifications from:
   - node’s `defaultSpecifications` if present, otherwise
   - the `DEFAULT_SPECIFICATIONS` template.
4. **Interpretation job** builds a prompt per chunk batch and calls the LLM:
   - Prompt builder: `KnowledgeItemInterpretationHandler.buildRefinementPrompt()`
   - Inputs:
     - current digest (if not the first batch)
     - new chunk batch content
     - iteration specifications
     - up to 5 prior iterations’ specs + digests
5. **LLM output** becomes a Knowledge Item Digest artifact.

### Strategic Synthesis: digests + framework specs → synthesis output

1. **Iteration creation** uses:
   - latest iteration specs if present, or
   - `defaultFirstIterationSpecs` if this is the first iteration.
2. **Inputs collected** from upstream Knowledge Curator digests and RAG documents.
3. **System prompt is assembled** by `StrategicSynthesisOutputGenerator.buildSystemPrompt()` using:
   - iteration specifications (primary prompt)
   - framework specialist default + supplemental specs
   - knowledge digests
4. **Planning phase** uses a separate planning prompt but includes the system prompt as `systemInstruction` (Gemini).
5. **Research + synthesis phases** use the system prompt + research findings to generate final output.
6. **Outputs stored** as artifacts:
   - `STRATEGIC_SYNTHESIS_OUTPUT` (final document)
   - `STRATEGIC_SYNTHESIS_PROCESS_SUMMARY` (process report)

## 3) Hardcoded prompt text (current code)

### Knowledge Curator default specifications template
Source: `apps/server/src/workflows/types/knowledge-curator.ts`

```
# Specifications

## Overview
Define how AI should generate the initial digest for new knowledge items.

## Output Format
- Structured summary with clear sections
- Key insights and main points
- Professional tone and clarity

## Template
- Executive summary
- Key findings
- Important conclusions
```

### Strategic Synthesis default first-iteration specs
Source: `apps/server/src/workflows/services/strategic-synthesis.service.ts`

```
# Strategic Synthesis — Initial Specifications

## Objective
Create a clear, actionable synthesis by combining all relevant inputs from upstream Knowledge Curator items and Framework Specialists. The synthesis should align with the overall workflow objectives and be immediately useful for downstream consumption.

## Inputs
- Knowledge Curator Item Digests (all related upstream items)
- Framework Specialist Specifications (all related upstream specialists)

## Method
1. Extract key insights and constraints from each input.
2. Identify overlaps, dependencies, and contradictions.
3. Resolve conflicts with reasoned judgments and cite sources when needed.
4. Produce a cohesive plan and narrative that is traceable to inputs.

## Use of Retrieval (RAG)
When additional detail or clarification is needed, perform targeted retrieval-augmented generation over the linked knowledge artifacts. Prefer precise queries; summarize and cite retrieved context succinctly.
```

### Knowledge Curator digest refinement prompt (template)
Source: `apps/server/src/jobs/job-handlers/workflows-queue/knowledge-item-interpretation.ts`

```
You are an expert knowledge curator. Create a high-quality, well-structured markdown digest based on the provided content.

Context from previous iterations (up to last 5):
---
Iteration 1 Specifications:
{specifications}

Iteration 1 Digest:
{digest}
---

Specifications (follow these guidelines):
---
{specifications}
---

Output requirements:
- Strictly valid Markdown formatting; use appropriate headings, lists, tables, and code fences as needed.
- Do not include instructions or meta-comments in the output.
- Do not include a manifest or any JSON metadata (e.g., a 'manifest' object); output only Markdown.
- Communicate clearly within the model’s available output token budget, prioritizing structure and clarity over verbosity.
- The digest must be complete and not truncated; if you are approaching output token limits, conclude sections succinctly and end with a brief closing summary so nothing is cut off mid-sentence.

Content to analyze:
---
{batchContent}
---
```

For follow-on batches, the template includes a “Current digest” section and instructions to refine and merge new content instead of creating the initial digest.

### Strategic Synthesis system prompt (template)
Source: `apps/server/src/jobs/job-handlers/workflows-queue/strategic-synthesis-generate-output/StrategicSynthesisOutputGenerator.ts`

```
You are the Strategic Synthesis agent. Your primary focus is rigorous research methodology and evidence-grounded synthesis.

RESEARCH METHODOLOGY (follow in order):
1) Problem Framing: Parse the specifications to enumerate the concrete information needs and decision points.
2) Context Review: Read the knowledge digests and framework specifications to form initial hypotheses and terminology.
3) Targeted Retrieval: Use rag_search only within the allowed chunk IDs to gather facts, definitions, figures, classifications, examples, and counterexamples relevant to each information need.
   - Prefer fewer, higher-quality chunks; prioritize higher similarity scores and diverse sources.
   - Retrieve up to ~20 results per query when needed; refine queries if coverage is weak or repetitive.
4) Evidence Handling: Track which findings support which claims; avoid unverifiable assertions; note when evidence is suggestive vs. conclusive.
5) Synthesis: Integrate the strongest evidence across sources; reconcile conflicts; surface assumptions; structure the narrative to answer the specifications explicitly.

CONSTRAINTS AND PRINCIPLES:
- Ground every claim in the provided digests or rag_search results; do not invent facts or rely on prior external knowledge.
- Prefer precise, neutral language; avoid meta-commentary about the process in the final output.
- If evidence is insufficient for a specific detail, write accurate, non-speculative statements without calling out missing data.

Formatting (minimal):
- Produce a coherent, well-structured Markdown document.
- Use normal prose and Markdown headings/lists as appropriate; avoid annotated code fences or language tags.

Strategic Synthesis Specifications (source of truth):
---
{specifications}
---

Framework Specialist Specifications (methodological context):
---
{frameworkSpecsSection}
---

Knowledge Digests (background context):
---
{digestSection or '(No prior digests available)'}
---
```

### Strategic Synthesis research planning prompt (template)
Source: `apps/server/src/jobs/job-handlers/workflows-queue/strategic-synthesis-generate-output/StrategicSynthesisOutputGenerator.ts`

~~~
Create a concrete research plan that will drive targeted retrieval over the knowledge base.

Planning methodology:
1) Read the specifications, framework specs, and digests (provided in the system prompt) to enumerate information needs.
2) Derive 3-7 concise topics (short noun-phrases) that cover these needs without overlap.
3) For each topic, write 2-5 specific, answerable questions (who/what/when/where/how/why) that the RAG search can resolve.
4) Produce 8-15 focused search queries tailored to the knowledge base; make them precise, deduplicated, and use domain terminology from the inputs.

Constraints:
- Topics must not be empty; include at least 3 and at most 7.
- Questions must be concrete (avoid vague prompts like "learn about").
- Queries should be optimized for retrieval (short, specific, high-signal terms; avoid boilerplate).
- Ensure coverage: include definitions, criteria, examples, risks/limitations, and measurement/metrics where applicable.

Output strictly as JSON (no explanations). Wrap in triple backticks only (no language tag). Use this schema:
```
{ "topics": [{ "name": string, "questions": string[] }], "queries": string[] }
```
~~~

## 4) UI and API touchpoints

### Knowledge Curator
- **Default specs**: UI edits → API → `workflow_node.data.defaultSpecifications`.
- **Iteration specs**: UI edits → API → `ai_generation_iteration.specifications`.

### Framework Specialist
- **Type specs**: UI edits → API → `framework_specialist.defaultSpecifications`.
- **Node specs**: UI edits → API → `workflow_node.data.supplementalSpecifications`.

### Strategic Synthesis
- **Iteration specs**: UI edits → API → `ai_generation_iteration.specifications`.

## 5) Moving parts at a system level

- **UI editors**: Allow users to view/edit specifications for nodes and iterations.
- **API services**: Persist specs and fetch them for display.
- **DB entities**: Store specs on iterations and nodes, plus framework type defaults.
- **Job handlers**:
  - Knowledge Curator interpretation builds prompts and generates digests.
  - Strategic Synthesis generator builds system prompts and final outputs.
- **LLM client**: Executes prompts (Gemini client for synthesis; generic LLM client for knowledge curation).
- **Artifacts**: Store generated content and link it back to iterations and source inputs.
- **Vector store (Qdrant)**: Stores chunk embeddings and supports retrieval in synthesis.

## 6) Quick reference (key files)

- Knowledge Curator default specs: `apps/server/src/workflows/types/knowledge-curator.ts`
- Knowledge Curator prompt builder: `apps/server/src/jobs/job-handlers/workflows-queue/knowledge-item-interpretation.ts`
- Strategic Synthesis prompt builder: `apps/server/src/jobs/job-handlers/workflows-queue/strategic-synthesis-generate-output/StrategicSynthesisOutputGenerator.ts`
- Framework Specialist specs storage: `apps/server/src/database/entities/framework-specialist.entity.ts`
- Iteration specs storage: `apps/server/src/database/entities/ai-generation-iteration.entity.ts`
- Artifact types: `apps/server/src/artifacts/types/artifact.ts`
