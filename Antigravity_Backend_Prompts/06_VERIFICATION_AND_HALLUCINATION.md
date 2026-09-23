# Claim Verification and Hallucination Control

Pipeline:
Evidence → LLM draft → claim extraction → claim/evidence comparison → status → final policy.

Each claim:
- text
- status
- confidence
- source_ids
- contradiction_source_ids

Statuses:
SUPPORTED
UNCERTAIN
CONFLICTING

A first version may use sentence splitting, semantic similarity, entity/keyword overlap and optional NLI.

Policy:
- all important claims supported → SUPPORTED
- important claims lack evidence → UNCERTAIN
- strong contradictory evidence → CONFLICTING

Never turn a low-confidence claim into a confident answer merely because the LLM sounds confident.

Every factual document-grounded answer must be traceable to document, page if available, chunk and source/snippet. Never invent citations.
