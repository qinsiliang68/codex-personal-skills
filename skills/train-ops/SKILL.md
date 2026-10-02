---
name: train-ops
description: Operate local or LAN GPU training and inference jobs from deployment through recovery, result return, and archive acceptance. Use for machine inspections, resource and temperature control, checkpoint-based inference, nonduplicate work assignment, and artifact completeness checks. Follow the current project runner and fleet policy; do not redesign experiments or judge scientific results.
---

# Training and Inference Operations

## Scope and authority

Operate approved workloads using the existing project commands, ledgers, validators, and environments. Preserve training continuity, other users' work, and the identity and completeness of required outputs. This skill supplies operating instructions, not permission to act outside the current authorization.

- Read the newest direct user instructions, taskbook, frozen configuration, and relevant handoff. Distinguish current instructions from quoted historical summaries. Apply corrections only to their stated scope; do not revive an old rule by copying a summary. Resolve material conflicts before the affected action.
- A request to inspect stays read-only. Within an approved operational scope, carry out routine steps without asking again. Code/experiment changes, destructive cleanup, reboot, and external notifications require the applicable authorization.
- Treat archived commands and session transcripts as evidence, not executable launchers. Do not run old scripts merely because a prior session used them.
- Use one operating agent unless the user authorizes delegation. Do not inherit old agent assignments, notification recipients, or cleanup permissions.
- Keep hosts, addresses, experiment IDs, seeds, parameters, and private source records out of this reusable skill. Keep them in the current task's approved private ledger.

## Establish the operating contract

Reuse the project ledger or a compact handoff table. Do not invent a task database, lock service, scheduler framework, or configuration system. Before deployment or takeover, make these facts explicit:

| Area | Required facts |
| --- | --- |
| Scope | Approved actions, priorities, stop/pause rules, protected paths, excluded machines, and final deliverables. |
| Identity | Experiment/run/group/seed, code revision or package hash, frozen parameter source, dataset/manifests, initial weights, and output roots. |
| Job type | Test, benchmark, or formal run; training or inference; exact checkpoint/epoch, role, and shard/range. |
| Nodes | Host identity, real storage layout, environment, other users' active work, normal/sensitive thermal class, and allowed concurrency. |
| Resources | Temperature target, sampling interval, sustained-temperature trigger (duration or consecutive samples), immediate-action ceiling and response, authorized power range/step and recheck time, memory/disk reserve, transfer route, and any measured bandwidth or resource bottleneck. |
| Cadence | Timezone, routine inspection times, event-triggered checks, next check, and the available mechanism that will actually perform them. |
| Presentation | Background compute, any node-local progress window, and approved destinations for operations logs versus experiment logs/data. |
| Acceptance | Required checkpoints, roles, files, fields, counts, exact validation units and stage-specific progress denominators, validators, return destination, retention and package naming rules. |

Do not guess missing scientific parameters, role coverage, or temperature limits. Ask only for a missing decision that blocks safe work; continue independent authorized checks. Do not invent a class timetable or repeatedly ask for one after the user has given an applicable availability rule.

For Windows LAN nodes, read [Windows node operations](references/windows-node-operations.md). It covers background/display separation, task settings, and configurable fleet policy examples. Numerical examples are not universal hardware specifications.

## Work stages and acceptance gates

Start with training scheduling and carry the work through acceptance. Data completeness and technical integrity checks are mandatory acceptance work, with early checks to catch defects before they multiply.

Define validation units before launch. For epoch-based training, the first complete training unit is one full epoch with its required validation, records and finished checkpoint writes; for step-based training, use the full checkpoint/evaluation interval specified by the taskbook. An inference unit is one run and checkpoint identity, one role, and a predefined complete sample-ID set or nonoverlapping shard. Validate all required outputs for that unit. A small smoke sample is not a complete training unit or evidence for a larger inference range; do not shrink a unit or denominator after a failure to claim acceptance.

| Stage | Required action and release condition |
| --- | --- |
| Training scheduling | Derive the expected output inventory from the taskbook before launch: required epochs/checkpoints, record types, fields, counts, roles, and destinations. Verify readiness and assign each formal run once. |
| Training execution and inspection | Check resources, process health, real progress, and new outputs. Validate the first complete required unit before expanding new/changed code. Keep runtime progress separate from accepted data coverage. |
| Training-output acceptance | For each required completed unit, verify the saved checkpoint identity and required training records against the inventory. A finished training process alone does not pass this gate. |
| Inference scheduling and execution | Apply the checkpoint readiness rule below, then assign checkpoint/role/range units, preserve unique ownership, and inspect runtime progress. |
| Inference-data acceptance | Open each required completed unit and check file/field completeness, row and ID coverage, checkpoint/role identity, and the contract's value invariants. Record exact gaps and failures. |
| Return and final acceptance | Verify returned data at the required destination, reconcile every expected unit, and inspect the actual archive contents and manifests. Only then declare the authorized workload delivered. |

These gates apply per defined unit, not as a fleet-wide barrier. **Checkpoint readiness for inference** requires a finished, loadable checkpoint with verified run/epoch identity and hash, validated inference inputs, and any upstream records required to interpret or run that inference. Once these conditions and current authorization are met, inference may begin while later training continues. Missing training records that are not inference prerequisites remain an acceptance debt; missing prerequisites block the affected inference. **Training-output acceptance** requires every training artifact in the unit's inventory to pass. Inference readiness never implies that the training unit, run, or final archive has passed acceptance.

## Inspect, decide, act, verify

1. Reconcile the ledger with live evidence. After a new conversation, reboot, disconnect, or restart, do not treat a historical snapshot as current.
2. Check the permitted connection path and residual control/transfer processes. Run independent SSH/SCP/SFTP commands concurrently without a preset connection or command limit when the current relay, network, disks, and nodes can handle them. Keep each operation bounded and close it. If actual connection failures or resource contention appear, diagnose and temporarily reduce the affected burst, then recheck; do not turn that response into a permanent concurrency cap.
3. Inspect enough state to decide:
   - hostname and GPU identity; temperature, utilization, GPU memory, actual power and power limit;
   - available physical RAM, relevant memory errors, free space on each input/output drive, and disk activity;
   - other users' actual resource use, not just installed software or a process name;
   - task state, real exit code, exact command/output root, parent and child processes, and relevant log tail;
   - current training/inference work and the set of newly validated outputs since the preceding inspection.
4. Choose one bounded action, perform it within authorization, and verify its effect before the next decision. Deploy nodes one at a time in the current requested order; a fleet recovery may require an initial inventory before assignment.
5. Report state, evidence time, action, remaining work, next check, and material risk. Stay quiet between checks when only meaningful changes were requested. Alert on failures, overheating, other-user conflicts, required user action, and verified completion.

Use short single-purpose commands or scripts for raw facts, one bounded transfer, packaging, or a mechanical validator. Scripts may check paths, exit codes, counts, sizes, and hashes. Keep recovery choices, scheduling, exception interpretation, and next actions in the agent. No automatic retry or decision loop merely to reduce tool calls.

A failed or unavailable query means **unknown**, not idle or healthy. Do not decide from a missing field, a task labeled Running, momentary zero GPU load, an existing directory, or the largest epoch number alone. Reconcile process, log, and artifact evidence.

Check after launch, restart, power/concurrency changes, task exit, and result return. At each inspection, estimate the next actionable event from live progress and recent unit duration: a transfer-sized completed range, expected task exit, active transfer or verifier completion, thermal recheck, or availability change. Wait until the earliest expected event or the active policy's maximum safety interval when no reliable event time is known; do not mechanically wait for a fixed clock slot. Recompute the next wait after handling an event. Compare progress over an interval appropriate to the measured epoch/shard duration. Distinguish staging, validation, checkpoint writing, and inference from a stall. An unchanged epoch counter during a long valid epoch does not justify killing it.

Record the next inspection time and its trigger. Use the available user-approved wakeup or monitoring mechanism; a written promise or an idle chat is not a running monitor. Do not add a scheduled task when the user selected an in-session wait, and do not let waiting prevent responding to new input. A wait timeout does not prove that a live process ended; recheck its handle or authoritative remote state.

## Launch and preserve training

- Verify the node's real environment, dataset and cache, manifests, free-space headroom, frozen configuration, code and initial-weight hashes. Use the established runner; for a uv-managed project use `uv run`, not an unrelated Python installation.
- Freeze scientific settings separately from operational scheduling. A batch of runs is not the model's batch size or sampling policy. Do not alter batch size, workers, augmentation, seeds, epochs, precision, sampling, or initialization for speed without approval.
- Keep a new experiment's code/config/output identity separate from frozen prior experiments. Reuse verified mechanisms without modifying archived scientific code in place.
- Before expanding new or changed code, verify the complete training unit defined above and its checkpoint, then the associated inference unit and actual output schema. Small smoke inputs check wiring; they do not establish full-workload speed or complete epoch coverage.
- Bind each launch to its exact run and output root. Check existing tasks/process trees and valid or partial artifacts before launching once. A test or benchmark never counts as formal deployment or progress without an explicitly approved, verified promotion.
- Start slow nodes first when requested, using their measured comparable durations rather than GPU model names. Honor explicit node order. Do not leave ready resources idle without a stated scheduling or safety reason.
- Keep computation independent of its progress-display window when required. Closing the display must not terminate training or inference. Forward existing native logs rather than building a second monitoring application.
- Protect uninterrupted training. Transfers, compression, derivation, and validation may overlap only when authorized and their measured resource impact does not disrupt primary work. Throttle or defer interfering maintenance before disturbing healthy training.
- Start the next run/phase only when its current gates and authorization permit it. Do not universally require all inference to finish first if the approved plan assigns inference elsewhere. Keep earlier unfinished inference and result returns explicitly outstanding.

For performance work, compare the same node with its own comparable baseline under recorded power, configuration, and data conditions. Measure full epoch wall time including required validation, recording, and checkpoint writes. Separate initial scanning/cache creation from steady-state time; observe multiple full epochs when startup effects matter. Report absolute times and what changed. Utilization, a tiny smoke test, or a faster machine alone does not prove an optimization.

## Assign and operate inference

- Derive the expected work set from the taskbook: run, checkpoint identity/epoch, role/split, and shard/sample range. Respect the defined uses of training, validation, calibration, and test data. Do not invent roles, thresholds, or call ordinary predictions OOF.
- Keep training and distributed inference outputs separate, linked by run and checkpoint hash. Infer only a fully written, verified checkpoint; never copy or consume a half-written file. Inference may overlap training on other nodes when supported and authorized.
- Give each work unit exactly one active owner. Check the ledger and live process/output evidence before assignment. Never let two nodes overwrite the same role/epoch/shard.
- Inspect the node before selecting concurrency. Apply its current normal/shared/sensitive policy and actual memory, heat, other users' workloads, and measured throughput. Do not blindly increase process count or underfeed decoding with arbitrary low priority/core limits.
- Prefer data already resident on suitable storage. Assign more remaining work to faster measured nodes when the gain exceeds input-transfer and return costs. Do not move an entire dataset to avoid a small checkpoint transfer.
- On a new code/environment/role path, validate one complete predefined inference unit before expansion. Verify its intended checkpoint, full ID coverage and required records, not just a successful process exit. This validates that unit only; remaining units still need acceptance.
- Track separate counts for deployed nodes, successful tests and active formal jobs. For each fixed formal work set, report distinct generated, source-validated, returned and destination-accepted counts: each numerator counts unique units at that stage, and each denominator is the full expected set in the stated scope. A source-validated unit awaiting return is not destination-accepted. Overall data-delivery progress uses destination-accepted units divided by all required delivery units; disclose gaps, outstanding returns and any separate packaging gate. Do not average unlike training epochs and inference shards into one percentage or silently reduce the denominator; an authorized scope change must be explicit.
- Estimate time from recent real throughput and remaining work per node, including return/validation costs where material. Do not extrapolate total completion from instantaneous GPU load.

## Diagnose, pause, and recover

- Read the failure and diagnose before retrying: access/tunnel failure, process crash, memory exhaustion, disk/input bottleneck, thermal throttling, incomplete write, or competing work. SSH loss alone does not prove shutdown or OOM. Each retry is a bounded new operation after diagnosis.
- When the user pauses the assistant's operations, immediately stop inspections, new assignments and mutations. Leave existing training/inference processes unchanged unless the user also requests pausing those jobs. For an explicit job pause/stop, act only on the named scope: honor an immediate-stop instruction; use a checkpoint/epoch boundary only when the user permits waiting for it. If the target or timing is unclear, stop further operations and ask for that distinction before changing running jobs. Do not continue inspection or maintenance under the pretext of waiting for a safe boundary. Retain existing checkpoints and the known remaining-work record without extra mutation after an operations pause.
- For training recovery, verify run/dataset/config/code identity and the last complete resumable checkpoint, including optimizer/scheduler/RNG state where required. Use the existing resume command. A weights-only restart is not necessarily an exact resume; disclose the distinction and obtain applicable approval before changing the run's meaning.
- For inference recovery, keep validated units, identify exact missing/invalid units, and isolate partial outputs only when necessary. Resume those units through the existing entrypoint. Do not overwrite valid work because a wrapper failed later.
- Before transferring ownership or restarting, stop only the identified task's process tree when authorized and verify its children exited. An unreachable old node may still run: do not silently assume abandonment. Require an explicit reassignment decision, separate destinations, and reconciliation/quarantine of late old outputs.
- Recheck temperature, power limits, paths, active tasks, and ownership after reboot or recovery. Restarting a tunnel is distinct from rebooting a computer; protect other users' work and remote-access tools.
- If a failure recurs without new evidence or its fix expands scope, stop blind retries and report the exact blocker and required decision.

## Accept data, return results, and verify packages

Derive a checklist from the current taskbook before declaring a unit complete. Separate technical integrity/completeness from scientific interpretation; do not demand favorable metrics or agreement with literature.

For each required run/epoch/checkpoint/role/range, record the expected versus observed files, fields, rows and IDs, the validation evidence, and any missing or invalid item in the existing ledger or validator output. Name the affected unit and file/field precisely. A question about one epoch's completeness must receive this unit-level comparison, not only a whole-batch progress percentage.

1. **Identity:** match run/group/seed, checkpoint type/epoch, configuration/dataset provenance, role/shard, and real checkpoint/file hashes where required.
2. **Contents:** open actual files with the project reader. Check required files/fields, rows, unique IDs, full intended ID coverage, frozen labels/membership, and task-specific value invariants. Investigate missing, overwritten, truncated, nonfinite, or suspicious placeholder fields; do not reject legitimate zeros without the field's semantics.
3. **Training records:** verify required per-epoch weights, per-image/batch records, native logs, and provenance. A final checkpoint does not prove intermediate records exist.
4. **Inference records:** verify every required checkpoint/role/range and its correct training association. Respect the inspection scope; a checked sample does not prove all units pass.
5. **Return:** validate on the helper, transfer through the approved route, compare required package/file counts, sizes and hashes, and run actual destination readback/acceptance checks. Label remote completion, returned, and accepted separately. Never fabricate exit or acceptance receipts.
6. **Archive:** collect to the agreed destination using stable scientific identity such as run/group/seed, not only a temporary machine/wave number. Separate weights and materials when required. Retain every contract-required checkpoint, including per-epoch/EMA weights; never assume only `best.pt` and `last.pt` are needed. Verify package contents/manifests and preserve sources until retention/cleanup is explicitly authorized.

Validate a unit only after the project's writer/completion evidence establishes that its required files are closed and will no longer be changed in place. Bind validation evidence to the exact unit, expected coverage, validator/version, file inventory and content hashes. An unchanged name, size, timestamp or old PASS marker alone does not prove unchanged contents. During routine inspection, reuse evidence for units whose immutability is established; if that cannot be established, recompute hashes before relying on prior validation. A replaced, regenerated or hash-mismatched file requires renewed content validation. After transfer, compute destination hashes and perform the required destination readback. At final acceptance, reconcile the full expected set and recompute its destination file hashes; matching files may reuse their bound content-validation evidence. Do not reopen and reparse every unchanged accepted file on every poll.

Missing, unreadable, mismatched, or unvalidated required data blocks acceptance of the affected unit. Within authorization, regenerate missing/invalid inference outputs from the original verified checkpoint, inputs and configuration; record the regeneration provenance and validate the outputs. Training-time observations such as gradients or per-batch traces may be irrecoverable: restore them only from verified original evidence, and never insert observations from a new training execution as if they came from the original run. Derived records may be recomputed from preserved source evidence only when their defined semantics allow it, with that provenance stated. If recovery is impossible, retain the explicit missing status. Rerunning training to produce replacement observations requires applicable approval and a new run identity; it does not repair the original run's missing records. Ordinary verified checkpoint resumption follows the recovery rule above. Preserve valid results and unrelated running work. Report the same stage-specific counts defined above, with exact outstanding items. Deployment success, exit code 0, aggregate file totals, and a representative sample cannot substitute for complete required coverage.

Large artifacts use the approved direct LAN/source-to-target route rather than an operations relay or management laptop. Respect bandwidth limits and ongoing training. Reserve real SSD space for data **and** cache/staging growth; free bytes after copying images alone do not prove readiness. Never conceal an HDD input path behind an SSD-named junction.

## Handoff and completion

Keep experiment logs/data with approved run storage. Keep operations records only at the approved destination; if operations logs belong on a VPS, do not leave extra local copies or send datasets there. Never publish private transcripts, inventories, paths, or credentials in this skill. Changing log retention or removing software remains a separately authorized action.

Follow the project's artifact language convention; for new deployments in the established English-log workflow, write added status/ledger/error explanations in English. Preserve native tool output and existing/frozen logs. Speak to the user in their requested language.

Write an actionable handoff in the existing approved location:

- latest instructions/policy overrides, evidence time/timezone, permitted actions and exclusions;
- each node's exact task/process identity, test/formal state, current work and last verified progress;
- unique assignments, missing/failed/partial units, and results awaiting return or destination acceptance;
- thermal/power/concurrency decisions, other-user restrictions, faults and next inspection;
- remaining packages, validator results, retention restrictions, and concrete next commands or project entrypoints.

Declare completion only when all authorized training/inference, destination acceptance, and required packaging have passed; disclose unresolved items. Close obsolete progress windows after completion. Stop only this task's monitoring/display machinery within authorization so empty displays do not reappear. Send a final notification only through an authorized channel and recipient.
