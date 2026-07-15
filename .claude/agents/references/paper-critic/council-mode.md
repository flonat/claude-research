# Paper Critic — Portable Council Mode

This optional mode is orchestrated by the main session, not by one
`paper-critic` worker. Read the installed shared `council-protocol.md`, then:

1. Run compilation, reference, citation, and page-limit gates.
2. Build the system prompt from `paper-critic.md` and the sibling council
   persona/prompt references.
3. Build one context file from the paper source, bibliography, and build log.
4. Invoke a separately verified council backend. The bundled public option is
   `council-api`; its OpenRouter calls are paid and require user approval.
5. Format the chairman result as the standard critic report, followed by
   council agreements, disputes, model identifiers, and timing metadata.

If no backend is installed or fewer than two models answer, run the standard
single-client review and label it clearly; do not claim a council result.
