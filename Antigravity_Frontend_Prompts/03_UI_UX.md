# UI/UX Specification

Create a clean, modern AI-assistant interface suitable for a hackathon demo.

## Main layout

```text
┌─────────────────────────────────────────────────────────────┐
│ Assistant / Logo                              Backend ●      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Conversation                                                │
│                                                             │
│ User message                                                │
│                                                             │
│ Assistant answer                                            │
│ [SUPPORTED]                                                 │
│                                                             │
│ Evidence                                                    │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ document.pdf · Page 1                                  │ │
│ │ Relevant source snippet...                             │ │
│ └─────────────────────────────────────────────────────────┘ │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Ask a question...                                  [Send]   │
├─────────────────────────────────────────────────────────────┤
│ [Upload document]                             [Clear chat]   │
└─────────────────────────────────────────────────────────────┘
```

## Statuses

Use text plus visual styling:
- SUPPORTED
- UNCERTAIN
- CONFLICTING

Do not rely on color alone.

## Source cards

Visible:
- filename
- page
- snippet

Expandable:
- source ID
- document ID
- chunk ID
- full snippet

## Conflict UI

Example:

```text
CONFLICTING

The provided documents disagree about the operating voltage.

12 V DC
RAG_Backend_Test_Document.pdf · Page 1

24 V DC
RAG_Conflict_Test_Document.pdf · Page 1
```

Do not label either value as correct unless the backend explicitly establishes that.

## Empty state

Use:
`Ask your documents anything`

and:
`Answers are grounded in uploaded evidence.`

Suggested questions may be shown, but do not hardcode answers.

## Responsive behavior

Desktop: centered conversation, readable width, evidence cards.

Mobile: stacked cards, usable input, no horizontal scrolling.

## Accessibility

Use semantic elements, labels, keyboard navigation, focus states, and aria labels where useful.
