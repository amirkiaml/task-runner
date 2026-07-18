# Coding Challenge | Agentic Task Runner

A FastAPI app where a user submits a task in plain language, a rule-based
router deterministically decides which predefined tool(s) apply, executes
them, and returns a transparent, numbered execution trace. No AI, LLM, or
external model provider involved anywhere in the pipeline.

## What it does

- Enter a task in plain language (e.g. "add 5 and 6, then uppercase the result").
- A keyword/pattern-based router decides which tool(s) apply, executes them
  in sequence, and returns a final answer.
- Every run is logged with a full, numbered execution trace and saved to history.
- Past tasks are viewable and re-inspectable from the UI.

## Tools implemented

| Tool | Purpose |
|---|---|
| `TextProcessorTool` | uppercase / lowercase / word count |
| `CalculatorTool` | addition / subtraction / multiplication / division |
| `WeatherMockTool` | mock weather for a city (no external API) |
| `UnitConvertor` *(bonus)* | km↔miles, °C↔°F, kg↔lbs |

If no tool matches a part of the request, that part is explicitly flagged
as unmatched in the trace rather than guessed at — there's no model here
that could safely fabricate an answer, so it doesn't try.

## How to run

Create and activate a conda environment:

```bash
conda create -n agent-runner python=3.12
conda activate agent-runner
```

Install dependencies and run:

```bash
pip install -r requirements.txt
python app.py
```

Then open `http://localhost:8000` in a browser. No API key or `.env` file
needed — the app has no external dependencies to configure.

**Environment**: tested on Python 3.12.

## Dependencies

```
fastapi
uvicorn
pydantic
```

No frontend build step — the UI is plain HTML/CSS/JavaScript (`static/index.html`),
served as a static file, calling the API directly via `fetch()`.

## Architecture

```
app.py          — FastAPI routes: POST /run, GET /history, DELETE /history
router.py       — Deterministic parsing: splits input into clauses, matches
                   each against known tool patterns via regex/keywords
orchestrator.py — Executes the matched tools in order, builds the numbered
                   trace, carries a step's result forward when the next
                   step depends on it (e.g. "uppercase the result")
tools.py        — The four tool implementations (plain functions)
storage.py      — JSON-file persistence (list/save/clear tasks)
static/         — Single-page frontend: submit a task, view result + trace,
                   browse and re-inspect history
```

`app.py` is intentionally thin — routing only. Parsing, execution, and
persistence are each isolated in their own module, so any one piece can be
tested or replaced independently.

## AI assistance

I used Claude throughout this build for the FastAPI backend wiring and the
frontend (HTML/CSS/JS), both areas I'm actively upskilling in. I also used 
Claude to write up this ReadMe file based on my notes and prompts. 

**Worth being upfront about one detour:** I initially built this using the OpenAI 
Agents SDK, with an LLM deciding which tool to call — before catching that the
assignment email explicitly said no AI/LLM/model-provider integration was
needed. I rebuilt it as the fully deterministic, rule-based system in this
repo once I caught that. All design decisions in the final version — the
clause-splitting approach, the tool-matching patterns, the module
structure — were mine, tested and debugged directly rather than submitted
unreviewed. They all originated from my initial agents SDK work, which I had
spent most of my time working on.

## Assumptions and tradeoffs

**Rule-based clause splitting, not true language understanding.** A
request is split into clauses on unambiguous delimiters only - `then`,
commas, periods, and newlines - then each clause is matched against a
tool's regex/keyword pattern. This deliberately excludes conjunctions like
`and`/`also` as delimiters, since `and` is itself part of the calculator's
own operand syntax ("add 5 **and** 6") - splitting on it would break that
simpler, more common case to handle a rarer compound one. A request like
"what's 5 plus 3 and also tell me the weather" merges into one clause and
only matches the first applicable tool. Found through testing, not fixed,
since resolving it properly would mean building something closer to real
NLU - out of scope for a rule-based router.

**Spelled-out numbers are supported, but only via a fixed word list.**
`_spell_out_numbers()` maps number words zero through twenty to digits
before matching, so "add five and six" works. Numbers spelled out beyond
twenty, or with more complex phrasing ("twenty-five"), aren't covered.

**Unit conversion direction is derived from word order in the input**, not
a fixed field order - found and fixed a real bug where "100 fahrenheit to
celsius" was silently reversed because the original matcher checked units
in a fixed reference-list order rather than their position in the actual
sentence.

**Uppercasing a number is a known no-op.** `TextProcessorTool.upper()` on
a numeric string like `"11"` returns `"11"` unchanged, since digits have no
letter case. Found via testing a compound prompt ("add 5 and 6, then
uppercase the result") - technically correct behavior, but a UX gap not
resolved here (would need number-to-words conversion first).

**`WeatherMockTool` isn't wired to `UnitConvertor`.** The mock returns a
formatted display string, not a raw number, so a request like "weather in
London in celsius and fahrenheit" can't feed the temperature back into the
converter - that part of the request is correctly flagged as unmatched
rather than silently dropped.

**JSON-file persistence has no write locking.** `storage.py` reads,
modifies, and rewrites the whole file per save - fine for a single-user
demo, but two truly simultaneous requests could race and drop a write.
Named here rather than fixed, since adding locking would be more than this
scope needs.

## Limitations

This system uses deterministic keyword and pattern matching - not an LLM -
to decide which tool applies to each part of a request. That means
behavior is fully predictable and reproducible, and there's no
hallucination risk on unmatched requests, since it never tries to answer
outside its tools. The tradeoff is flexibility: phrasing the router's
patterns don't anticipate (unusual conjunctions, indirect phrasing, complex
number words) won't be recognized, where a language-model-based agent would
likely handle it. The tools themselves are also intentionally simple mocks,
so this doesn't reflect the reliability or scale demands of a production
system.

## Possible improvements

- **Replace mock tools with real services** - e.g. a live weather API in
  place of `WeatherMockTool`, and wire `UnitConvertor` to consume its actual
  numeric output.
- **A more capable parser** for clause splitting and intent matching -
  the current regex/keyword approach is deliberately simple; a natural
  extension (outside this challenge's no-AI scope) would be swapping the
  rule-based router for an LLM-based one, which I've built and tested
  separately in an initial iteration of this project.
- **Automated tests** for each tool in isolation, and for the router's
  clause-matching logic against a fixed set of prompts.
- **File locking or a real database** for persistence, if this ever needed
  to support concurrent users - I've used Supabase in production
  elsewhere and would likely reach for that here over the current
  JSON-file setup, for the same reasons: hosted, easy to query, minimal
  ops overhead, and no risk of the write-race condition flagged above.
- **UI improvements** - both aesthetic, and in how multi-tool results are
  displayed, to make tool-calling order and interdependencies (e.g. one
  step's result feeding the next) more visually explicit than the current
  bulleted list.

## Time spent

Before I noticed that no LLMs or real agents were required, I spent ~10
hours building the version that uses real agents via the OpenAI Agents
SDK. About 4h of that went into writing and testing the tools and
the agent, and documenting the work through a Jupyter notebook; the rest
went into modularization, and setting up and testing FastAPI and the UI.
Once I caught that no real agents were actually needed, I spent ~2 hours
repurposing the existing modules and building the new ones needed for
the current, deterministic version.
