# Braidpipe Positioning

> One playbook. One Braid. No workers.

## One-Liner

Braidpipe is an async data orchestrator that fits in a single YAML file.  
It choreographs data movement — not business logic.

---

## The Braidpipe Ontology

| Term | Meaning | What It Is Not |
|------|---------|----------------|
| **Braidpipe** | The open-source project. The CLI. The engine. | Not a company. Not a SaaS (yet). |
| **Playbook** | A single YAML file declaring source, transform, destination. | Not code. Not a script. Not a DAG graph. |
| **Braid** | One runtime execution of one Playbook. One OS process. | Not a worker. Not a thread inside a monolith. Not a reusable daemon. |
| **Connector** | An extension that reads from or writes to an external system. | Not a custom script. Not a Python function embedded in YAML. |
| **Statement** | A transform extension that enhances data in-flight. | Not a branching `if`. Not a loop. |
| **Context** | The shared namespace for a single Braid run. | Not a global variable pool. Never holds unbounded collections in memory. |
| **Flow** | The completed trace of a Braid. | Not a persistent service. |

---

## What Braidpipe Is

- A **declarative dataflow engine**. You describe where data comes from, how it changes, and where it goes.
- **Choreography, not execution**. The YAML orchestrates. Your services (FastAPI, containers, functions) execute.
- **Stateless by default**. Checkpoints and telemetry are local SQLite/JSON. No Redis, no database server required.
- **Memory-safe**. Collections and large values transparently spill to SQLite. Scalars stay in RAM. Records stream through.

## What Braidpipe Is Not

- Not a **task orchestrator** like Airflow, Temporal, or Kestra. We do not manage business logic, retries on human tasks, or multi-day sagas.
- Not a **no-code** tool. The user writes YAML. We do not offer drag-and-drop.
- Not a **workflow engine with code escapes**. There is no `script:` block, no `eval`, no inline Python.
- Not a **captive platform**. We do not swallow your logic into our boxes.

---

## The Choreography Principle

> **If your playbook feels like it needs branching, loops, or inline code, the problem is not the playbook. The problem is that you are trying to embed business logic where it does not belong.**

Business logic belongs in **your services**.  
Braidpipe belongs in the **spaces between them** — enhancing, enriching, routing.

This principle comes from classical workflow architecture (PROSA). The workflow is the conductor. The orchestra is your code. Never confuse the baton with the instrument.

---

## The Memory Contract

1. **Records stream through.** They are yielded, transformed, and forwarded. Never stored in memory in bulk.
2. **Context holds references.** It holds IDs, cursors, tokens, and scalar flags. Always O(1) in size.
3. **Collections live in the Run Spool.** If a step must share a lookup table or large payload, it writes to the per-run SQLite cache. This is temporary disk, not RAM.
4. **Spool is deleted on success.** When the Braid exits cleanly, the scratchpad is cleared.

---

## The Grammar Rules

- A Playbook has **one `version`**, optional `name`, `sources`, optional `transform` statements, and `destinations`.
- Sources and destinations are **dicts** (named keys). The key is the output context name.
- The singular `source:` and `destination:` are convenience aliases normalized to the plural form.
- **No `if`.** No `forEach`. No `while`. No `script`.
- Conditions are data mappings (`cases`), not control flow. They produce values, not branches.
- Formulas are arithmetic and comparison expressions (Excel-like), not imperative logic.

---

## Target User

**Senior data engineers, platform engineers, and backend developers** building high-throughput sync, ETL, and API aggregation pipelines.

They have outgrown cron scripts and Airflow workers, but do not want to provision a distributed orchestration cluster for simple data movement.

## Target Pain

> "My current orchestrator is too heavy for a simple API-to-database sync, but my Python scripts are too fragile to run in production."

---

## The Anti-Captive Position

Legacy workflow platforms (SOAR, RPA, no-code tools) lure you in with visual editors, then trap your logic inside proprietary boxes.

**Braidpipe is the exit ramp.**

- Your logic stays in your repos.
- Your runtime stays on your machines.
- Your YAML is plain text — version-controlled, diffable, portable.

If a vendor asks you to paste Python into their web UI, you are building a prison. Braidpipe is the key.

---

## The SaaS Boundary

The open-source CLI will always be **infrastructure-free**: no Docker, no queues, no hosted control plane.

The future SaaS will add **convenience and scale**, not core engine features:

| Capability | OSS | Cloud |
|------------|-----|-------|
| YAML execution | ✅ | ✅ |
| Local SQLite / JSON | ✅ | ✅ |
| Webhook ingestion (push triggers) | ❌ | ✅ |
| Team collaboration / GitOps sync | ❌ | ✅ |
| Managed schedules / multi-node fleet | ❌ | ✅ |
| SSO / audit logs / SLAs | ❌ | ✅ |

The community never pays for connectors. The enterprise pays for governance.

---

## The Workflow Market Insight

The industry is a yo-yo: users flock to visual workflow tools, discover the lock-in, then struggle to migrate.

Braidpipe exists for the **second half of that cycle** — the migration, the cleanup, the return to sane architecture. We do not compete with the shiny drag-and-drop tools. We compete with the regret that follows them.

---

## License

MIT — Personal project, 2024.