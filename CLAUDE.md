# CLAUDE.md

## Project purpose

This project is not a coding-first project.  
Its purpose is to transform fragmented notes from chats, Google Docs, and ad hoc team discussions into a rigorous problem statement, a mathematical formulation, and one or more validated solution paths.

The domain is mathematical modeling of risk in lottery-like systems or adjacent probabilistic decision problems.  
The assistant must prioritize clarity, traceability, and formalization over speed or premature solution generation.

## Main objective

Produce a clean research workflow with these outputs:

1. `raw_facts.md` — extracted facts, assumptions, numbers, constraints, terminology.
2. `contradictions.md` — conflicts, ambiguities, missing definitions, unresolved questions.
3. `problem_statement_plain.md` — formal problem statement in precise natural language.
4. `problem_statement_math.md` — formal mathematical formulation.
5. `hypotheses.md` — hypotheses, rationale, implications, falsification conditions, validation plan.
6. `solution_options.md` — alternative model classes and solution strategies.
7. `validation_plan.md` — what to test analytically, numerically, and by simulation.
8. `final_solution.md` — final document with one or several candidate solutions and explicit assumptions.

## Core working principles

- Do not jump to solving before the problem is formalized.
- Do not merge facts, guesses, interpretations, and open questions.
- Do not smooth over contradictions. Surface them explicitly.
- Do not invent missing parameters, distributions, objectives, or constraints.
- If multiple interpretations are possible, enumerate them and keep them separate.
- Treat vague business language as raw material, not as a formal definition.
- Prefer a smaller correct model over a larger incoherent one.
- Every nontrivial conclusion must be traceable to source notes or to an explicit assumption.

## Required classification of statements

Every extracted statement must be labeled as exactly one of:

- `FACT`
- `ASSUMPTION`
- `INTERPRETATION`
- `OPEN_QUESTION`
- `CONFLICT`

Never present an `ASSUMPTION` as a `FACT`.  
Never hide a `CONFLICT` inside a summary paragraph.

## Standard workflow

For any substantial task, follow this order:

1. **Ingest**
   - Read the material relevant to the current subtask.
   - Extract entities, variables, numeric values, rules, objectives, and constraints.
   - Write structured notes, not polished prose.

2. **Normalize**
   - Deduplicate terms.
   - Build a glossary.
   - Identify synonymous phrases that refer to the same concept.
   - Separate domain language from mathematical language.

3. **Resolve structure**
   - List contradictions.
   - List missing information required for formalization.
   - List candidate interpretations when the source material is ambiguous.

4. **Plain-language formalization**
   - Produce a rigorous natural-language statement of the problem.
   - Define scope, actors, decisions, uncertainties, constraints, success criteria, and exclusions.

5. **Mathematical formalization**
   - Define sets, indices, parameters, random variables, decision variables, dynamics, constraints, objectives, and risk measures.
   - State assumptions explicitly.
   - Map the problem to candidate model families.

6. **Hypotheses and solution design**
   - Generate hypotheses only after the mathematical structure is explicit.
   - For each hypothesis, define what evidence would support or falsify it.
   - Propose alternative solution paths when appropriate.

7. **Validation**
   - Separate analytical checks, numerical checks, simulation checks, and sensitivity checks.
   - Explicitly note which claims are proven, simulated, estimated, or conjectured.

## Output format rules

When producing any structured artifact, prefer compact sections and bullet points.

For each document:
- start with purpose
- define inputs
- define outputs
- list assumptions separately
- list unresolved questions separately

For formal mathematical outputs, always include these sections if applicable:

- Problem setting
- Entities and actors
- Observables / data
- Parameters
- Random variables
- Decision variables
- Objective function
- Constraints
- Risk metrics
- Assumptions
- Candidate stochastic processes / model classes
- What remains unidentified

## Mathematical modeling rules

When formalizing a problem, explicitly check whether it reduces to one or more of:

- discrete probability model
- binomial / multinomial structure
- compound distribution
- Markov chain
- absorbing process
- ruin process
- point process / arrival process
- stochastic optimization
- game-theoretic model
- simulation-first model
- Bayesian inference problem
- estimation / calibration problem

Do not force a game-theoretic formulation if there is no strategic interaction.  
Do not force continuous-time machinery if the process is naturally discrete.  
Do not assume independence unless it is justified or declared as an approximation.

## Verification rules

Before accepting any model or solution, check:

- Are all variables defined?
- Are units consistent?
- Are probabilities valid and normalized?
- Are objectives and constraints compatible?
- Are assumptions explicit?
- Is the model identifiable from available data?
- Does the proposed method answer the actual business/problem question?
- What would make this model wrong?

If a model cannot yet be verified, state exactly what is missing.

## Interaction rules

When information is incomplete:
- ask targeted questions
- ask only the minimum needed to unblock progress
- prefer grouped clarification questions over scattered ones

When given messy notes:
- first convert them into structure
- do not write polished prose too early

When given a possible solution:
- first restate the implied problem
- then test whether the solution matches that problem
- then list hidden assumptions

## Document quality rules

All final documents must:
- be concise but formal
- separate facts from assumptions
- contain no rhetorical filler
- avoid motivational language
- avoid fake certainty
- preserve alternative interpretations when unresolved

## File conventions

Use these files consistently:

- `notes/raw_facts.md`
- `notes/glossary.md`
- `notes/contradictions.md`
- `docs/problem_statement_plain.md`
- `docs/problem_statement_math.md`
- `docs/hypotheses.md`
- `docs/solution_options.md`
- `docs/validation_plan.md`
- `docs/final_solution.md`
- `docs/open_questions.md`

Do not overwrite a more formal artifact with a rougher draft.  
If revising, preserve a short changelog section at the top.

## Default response behavior

Unless explicitly asked otherwise:
- first produce structure
- then produce formalization
- then produce hypotheses
- then produce validation steps
- only then produce a recommended solution

If the task is ambiguous, do not choose silently.  
Show the competing interpretations and the consequences of each.
