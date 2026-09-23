# Memory and Contradiction Handling

Memory types can include:
preference, profile, goal, fact, instruction, correction.

A candidate memory contains text, type, source, confidence and validation status.

Retrieve only relevant validated memories. Do not dump the entire database into prompts.

## Conflict flow
1. Semantically search similar memories.
2. Detect potentially conflicting facts.
3. Create conflict record.
4. Keep old and new facts.
5. Ask for explicit resolution.
6. Apply keep_old / keep_new / keep_both.
7. Record audit event.

Example:
Old: "I prefer Python."
New: "I now prefer Java."

Do not automatically treat an LLM assumption as a validated memory.
