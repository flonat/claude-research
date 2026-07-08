---
name: codex-math
description: Use when you need OpenAI Codex (gpt-5.5) as an adversarial mathematical co-processor — verify, write, and explore modes for hard proofs, counterexample search, and independent verification. Treat every output as a lead, not a verdict.
author: Moran Koren <korenmor@bgu.ac.il> (Ben-Gurion University of the Negev)
---

> **Author:** Moran Koren, Ben-Gurion University of the Negev (korenmor@bgu.ac.il). Part of the [Theorist Toolbox](https://github.com/morankor/theorist-toolbox).

## What this is

OpenAI Codex (gpt-5.5) as a mathematical co-processor. Codex runs non-interactively via `codex exec` and returns structured results. Use it for hard proof problems that resist direct attempts.

**Execution model (adapted for this system).** This skill does **not** ship its own `codex` wrappers. It dispatches the existing **`codex-research` agent** (which already fronts the `codex` CLI in headless mode) with a math-specific prompt built from one of the three mode templates below. The skill's value is the *discipline* — the erratic-genius triage, the reasoning-effort calibration, and the prompt templates — not the plumbing. The one bundled helper is `scripts/extract_block.py`, which pulls a clean theorem/proof block (plus referenced equations) out of a `.tex` file so the verify/write prompts get self-contained input without hand-pasting.

Three modes: **verify**, **write**, **explore**.

## The erratic genius caveat

Codex is an excellent mathematician but produces a substantial fraction of false positives. It is brilliant and unreliable. Treat every output as a lead, not a verdict.

**Real catches:** concrete counterexamples, dimensional/sign errors, genuine logical gaps, missing existence arguments, incorrect domain specifications.

**False positives:** flagging standard conventions as errors, demanding unnecessary generality, over-interpreting degenerate cases, flagging stated assumptions as "unjustified," missing paper-level context.

**How to tell them apart:**
- A real catch involves a specific counterexample or points to a concrete step that doesn't follow
- A false positive involves a convention mismatch, demands regularity conditions that are standard, or flags something the paper already addresses elsewhere

**Do not accept or reject Codex output without triaging it yourself.** Read each finding. Check whether the concern is real. If Codex says a step is wrong, verify the specific algebra. If Codex says a proof is correct, still check the key steps.

## When to use

- **After a proof attempt fails.** If you tried to prove a result and got stuck, ask Codex to explore or write the proof. It may find a strategy you missed.
- **After the math auditor flags a gap.** If the auditor identified an unproved load-bearing claim, use Codex to attempt the proof before weakening the claim.
- **For hard counterexample search.** If you need to know whether a conjecture is true or false, Codex can systematically explore.
- **For independent verification.** Run Codex verify on your own proofs as a second opinion.
- **Do not use for routine algebra.** Simple FOCs, envelope conditions, sign checks, and standard derivations belong in a deterministic symbolic tool (`sympy`, faster and free), not Codex. Reach for Codex only when the problem requires reasoning — proof strategy, counterexample search, existence/uniqueness — not when it's just symbolic computation.

## Reasoning effort

Codex supports three reasoning effort levels. **Do not limit effort on hard problems.** The cost of running high effort is small; the cost of missing a proof or counterexample is large.

| Task | Effort | When to use |
|------|--------|-------------|
| Quick sanity check | `low` | Routine sign/dimension check, already confident |
| Standard verification | `medium` | Default. Checking a proof you believe is correct |
| Hard proof, conjecture, or exploration | `high` | **Always use high for:** unproved load-bearing claims, counterexample search, writing proofs for results that resisted direct attempts, anything the math auditor flagged as Critical |

When in doubt, use `high`. There is no reason to economize on reasoning effort for important results.

## How to prompt Codex well

Codex is non-interactive — it gets one prompt and returns one response. The quality of its output depends entirely on the quality of your prompt. **Do the prep work before calling any script.**

### For verify and write modes (extract the block, then build the prompt)

Use `scripts/extract_block.py` to pull the relevant content, then hand it to the `codex-research` agent. Your job is to give the right pattern so it extracts the right block. If the proposition references definitions or equations from elsewhere in the paper, the helper grabs referenced equations automatically, but it may miss context. When verifying a hard proof:

1. Run `python3 ~/.claude/skills/codex-math/scripts/extract_block.py <file.tex> "<pattern>"` first to see what it pulls (`<pattern>` is a label like `prop:concavity` or literal text like `Theorem 1`).
2. Check the extracted block includes everything Codex needs; if critical context is missing, use explore mode instead and construct the full prompt manually.

### For explore mode (you write the prompt)

This is where prompt quality matters most. Before dispatching `codex-research` in explore mode:

1. **State the exact claim.** Not "check the concavity" but "Prove or disprove: V(τ) is strictly concave in τ for all τ > 0, where x*(τ) is the unique fixed point of x = g(τ, x) with g defined by [equation]."
2. **Define all notation.** Codex doesn't know your paper. Spell out every variable, its domain, and its economic meaning. "where τ > 0 is the tax rate, x*(τ) is the equilibrium effort level, σ² > 0 is the noise variance, γ ∈ (0,1) is risk aversion."
3. **Say what's been tried and failed.** "Direct computation of V''(τ) via the chain rule produces a rational function whose sign depends on parameter ratios. The Hessian approach doesn't simplify because the implicit function has a non-separable second derivative."
4. **Ask for specific strategies.** "Try: (a) change of variables to make the composition separable, (b) show the composition of concave functions is concave under the monotonicity conditions that hold here, (c) find a counterexample in the region γ > 0.5, σ² < 1."
5. **Demand rigor.** "Prove every step. If you claim a function is concave, compute the second derivative and show it's negative. If you claim a counterexample, give specific parameter values and verify numerically. Do not hand-wave."

### Example: good vs. bad explore prompts

**Bad:** "Is the value function concave?"

**Good:** "Consider V(τ) = u(c*(τ)) - ψ·x*(τ)², where c*(τ) = f(x*(τ)) - τ·x*(τ) and x*(τ) solves the fixed point x = h(τ, x) with h(τ,x) = (1-τ)f'⁻¹(ψx/(1-τ)). All parameters strictly positive, f strictly concave with f(0)=0, f'(0)=∞, f'(∞)=0. Prove or disprove: V is strictly concave in τ on (0,1). If not globally concave, find the tightest sufficient condition. Approaches tried: direct Hessian (doesn't simplify due to implicit function composition), perturbation around τ=0 (works locally). Try: envelope theorem approach, monotone comparative statics, or counterexample search over standard CES production functions."

The difference: the good prompt gives Codex everything it needs to work independently — definitions, parameter domains, what's been tried, what to try next, and the standard of rigor expected.

### General rules for prompting Codex

- **Be explicit about rigor.** Say "prove every step" or "show all algebra." Codex will hand-wave if you let it.
- **Include parameter domains.** Codex needs to know whether parameters are positive, bounded, in (0,1), etc.
- **State the standard of proof.** "A valid proof must handle all boundary cases" or "a counterexample must give specific numerical parameter values."
- **Ask for multiple strategies when exploring.** Codex may fail with one approach but succeed with another.
- **Pipe content inline; do not have Codex read files itself.** On a properly configured host Codex *can* `cat` files in the workspace, but reading from inside the sandbox is fragile (depends on `bwrap` being functional — see Sandbox model below) and adds a tool call. `extract_block.py` already pre-extracts content; for ad-hoc prompts, paste the content into the prompt yourself.

## How to dispatch (all three modes)

Each mode is the **`codex-research` agent** launched via the `Agent` tool with a mode-specific prompt. The agent fronts `codex exec` headless and returns Codex's final answer as its result. Build the prompt from the templates below; for verify/write, pre-extract the block with `extract_block.py` so Codex gets self-contained input. State the reasoning effort in the prompt (`low`/`medium`/`high` per the table above).

File the result under `reviews/_project/codex-math/<YYYY-MM-DD-HHMM>.md` per `review-artefact-routing`. The result is a **lead, not a verdict** — triage every finding (see the erratic-genius caveat above).

## Mode 1: Verify a proof

Check whether a proof is correct step by step.

```bash
# 1. Extract the block (proposition + proof + referenced equations)
python3 ~/.claude/skills/codex-math/scripts/extract_block.py paper/sections/model.tex "prop:concavity"
```

2. Launch `codex-research` with a prompt of the form:

> "You are a hostile proof-checker. Verify the following result and its proof **step by step** at **high** reasoning effort. For every step, state whether it is justified; if not, give the specific line and why (a concrete counterexample, a sign/dimension error, or a missing existence argument — not a style complaint). Do not hand-wave. End with `VERDICT: PASS` or `VERDICT: FAIL` plus the exact failing step. \n\n[paste extract_block.py output]"

**After running:** For each FAIL finding, check whether it's a real error or a false positive. Report only confirmed errors.

## Mode 2: Write a proof

Ask Codex to write a complete proof of a stated result. Launch `codex-research` with:

> "Prove the following at **high** reasoning effort. A valid proof must justify every step, handle all boundary cases, and give specific numerical parameter values for any claimed counterexample. State all assumptions you use. If you cannot close a step, say so explicitly rather than hand-waving. \n\n[theorem statement, with all notation and parameter domains defined; or `extract_block.py` output for the statement]"

**After running:** Do not blindly paste the proof into the paper. Verify every step. Run Mode 1 (verify) on Codex's own proof — Codex may produce a proof that looks complete but has a subtle gap.

## Mode 3: Explore a conjecture

Investigate whether a claim is true, find conditions, construct counterexamples. Launch `codex-research` with a fully self-contained prompt (see "For explore mode" above — state the exact claim, define all notation/domains, say what's been tried, ask for specific strategies, demand rigor). Example:

> "At **high** reasoning effort: Is V(τ) globally concave for all γ > 0, or can it have multiple local maxima? [definitions, parameter domains, what's been tried]. Try: (a) … (b) … (c) counterexample search over standard CES production functions. Prove every step; for any counterexample give specific parameter values and verify numerically."

**This is the most valuable mode.** When a proof attempt fails and you're unsure whether the result is even true, exploration can:
- Find a counterexample (→ characterize the boundary instead)
- Find a sufficient condition (→ prove under that condition)
- Suggest a proof strategy you haven't tried
- Confirm the result is likely true but hard to prove (→ try harder, or restrict the parameter space)

## Dual audit pattern

For maximum confidence on critical results, run Codex AND a Claude verification in parallel: dispatch `codex-research` (Mode 1) **and** the `domain-reviewer` agent on the same proof.

- Both PASS → high confidence
- Both FAIL on same step → real error
- Disagreement → investigate the specific step manually

For a machine-checked proof of a high-stakes lemma, use `/lean-check` (R3); this skill is the LLM adversarial second opinion (R0′) — a lead, not a verdict.

## Runtime behavior

Hard proofs at `high` effort routinely run 1–5 minutes inside the `codex-research` agent; do not assume a hang. Codex emits mid-thinking progress paragraphs ("I'm thinking about…") before the final answer — those are the model summarizing its own reasoning, not the answer. The agent returns only the final message; do not paste reasoning summaries into the paper.

## Host note (`codex` sandbox)

`codex exec --full-auto` runs in a `workspace-write` sandbox (shell + `python3`/`sympy` available; read everywhere; write only in `workdir`/`/tmp`/`$TMPDIR`/`~/.codex/memories`). On Linux hosts using bubblewrap, unprivileged user namespaces must be enabled (`kernel.apparmor_restrict_unprivileged_userns=0`) or every codex shell command fails with `bwrap: loopback: …`. This does **not** affect the Mac Mini. Because we pre-extract content with `extract_block.py` and pass it inline rather than asking Codex to `cat` files, the modes work regardless of sandbox-shell state.