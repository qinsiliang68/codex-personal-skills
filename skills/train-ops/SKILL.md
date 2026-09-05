---
name: train-ops
description: Safe local and LAN operations for YOLO/Ultralytics GPU training fleets. Use when Codex is asked to monitor YOLO training machines, deploy or recover training nodes, start the next YOLO run, avoid duplicate runs, verify runs/eval/manifests artifacts, collect lightweight results, diagnose SSH/GPU temperature/GPU memory/system memory/disk/network failures, or maintain long-running multi-node YOLO training without destabilizing the LAN. Prefer short, agent-led operational steps over condition-heavy orchestration scripts.
---

# Train Ops

## Purpose

Operate local or LAN YOLO/Ultralytics GPU training nodes conservatively. Prioritize training continuity, duplicate-run prevention, visible foreground training, artifact integrity, and network stability.

Use the current conversation, user-provided inventory, and project ledgers as the source of truth. Do not hardcode a fleet list, IP addresses, machine models, run IDs, or hyperparameters into this skill.

## Hard Rules

- Across the entire fleet, allow at most one active SSH/SCP/SFTP connection at any instant. This is global, not per host: connections to different machines must never overlap. Before and after every remote operation, check local `ssh`, `scp`, and `sftp` processes plus established TCP/22 connections.
- Prefer more short, bounded operations over one large script. Use the cycle: observe raw state, let the agent decide, perform one action, then verify it before choosing the next action.
- Keep operational scripts single-purpose and normally measured in tens of lines. If a script starts combining inventory, interpretation, copying, packaging, recovery, and fleet scheduling or grows toward hundreds of lines, split it into separate invocations.
- Allow simple script conditions only for mechanical safety and fail-closed behavior, such as exact path/identity checks, required-file checks, free-space thresholds, exit codes, counts, sizes, and hashes. Do not encode operational judgment, exception classification, recovery selection, node scheduling, or next-step choice in script branches.
- Do not create a one-script-for-all-nodes workflow merely to reduce tool calls. Run one node and one bounded phase at a time, inspect its actual output, and make the next decision in the agent.
- Do not add automatic retry loops or unattended decision loops. A retry is a new explicit operation after the agent reads the previous failure. Multiple tool calls are preferred when they preserve judgment and observability.
- Keep SSH short-lived. Connect, run the required command, disconnect. Do not leave SSH sessions open unless the user explicitly asked for a long-lived task.
- Before and after risky operations, check local `ssh`, `scp`, and `sftp` processes and established port-22 connections. Kill only processes created by the current Codex task.
- Do not run old operational scripts from archives unless the user explicitly authorizes them. Treat archive/session directories as read-only references unless the user explicitly asks to write there.
- Do not route large files through the local machine. Prefer remote-to-remote transfer from the target node, and always apply a bandwidth limit for SCP/SFTP-style transfers.
- Completed runs must be collected to the local machine into the current experiment archive after verification. Exclude datasets and bulk checkpoints unless the user asks for them; use one limited-bandwidth transfer at a time.
- For final handoff archives, separate weights from materials: keep `best.pt` and `last.pt` in an uncompressed per-run weights folder for fast lookup, and package non-weight materials separately with `.pt` files excluded. Verify both sides by real file counts before saying cleanup is safe.
- Formal training must be launched in a foreground or interactive window/task so the user can see logs and process command lines. Background tasks are allowed only for maintenance such as transfer, install, or setup.
- Treat any path read repeatedly by training as input and keep it on the node's real C-drive SSD: dataset, workdir, staging, hardlink base cache, active data cache, CSVs, manifests, initial model weights, code, and runtime environment. Reject junctions, symlinks, or mounts that redirect these paths to a mechanical disk.
- Use mechanical disks only as output targets for results, logs, weights, checkpoints, artifacts, and packages. Never configure an HDD as a dataset, staging, workdir, base-cache, or data-loader source. Lightweight reads of output metadata such as a `results.csv` tail, status JSON, or log tail are allowed for monitoring; they are not permission to load training inputs from the HDD.
- Deploy nodes one at a time. Finish identity/resource checks, deployment, visible foreground launch, and initial artifact/process verification on one node before deploying the next. Do not bulk-scan the fleet and then bulk-deploy.
- For new experiments and deployments, write project-owned logs, status files, task output, error summaries, ledger notes, and archive-report fields in English. Do not rename or rewrite active or frozen historical logs merely to change language. Preserve third-party native output as emitted, but write added explanations and conclusions in English.
- Preserve training hyperparameters unless the user explicitly changes them. Reuse the project's established command pattern.
- Use `uv` for YOLO project commands. Do not launch project Python scripts with bare `python`.
- Never kill remote-access tools such as ToDesk unless the user explicitly asks.
- Avoid broad destructive cleanup. Move or delete only files you have identified as non-system, non-active, and safe for the current task.

## Script Boundary

Keep code small and mechanical. Keep interpretation and sequencing in the agent:

- Prefer a direct one-shot command for a single fact or action.
- Use a short script when quoting, repeatability, or a small atomic transaction makes it safer than a direct command.
- A script may collect raw facts such as `nvidia-smi`, memory, disks, listeners, processes, task state, file counts, sizes, and hashes.
- A script may perform one bounded action such as one copy, one TAR creation, one task registration, or one manifest calculation, with simple fail-closed guards.
- Do not let a script classify live state and then choose among operational actions. The agent must inspect the output and decide whether to copy, package, retry, recover, skip, clean, or move to another node.
- Do not embed a fleet list, run matrix, experiment interpretation, exception policy, or multi-node scheduler in a reusable script.
- Do not combine source inventory, copy, TAR creation, validation, cleanup, and recovery into one large wrapper. Run and verify those phases separately.
- Keep project-specific parsing of runs, eval, preflight, post-train, and manifests in the current agent context.

Use `scripts/probe-windows-gpu-node.ps1` only when its compact raw fact bundle is genuinely useful. Prefer smaller direct probes when only a few fields are needed.

## Operating Loop

1. Confirm the current objective and constraints from the newest user message.
2. Check local residual SSH/SCP/SFTP and local network-risk services before remote work.
3. Issue one short probe or bounded action, inspect the returned evidence, and make the next decision in the agent. Do not precompute a long conditional workflow.
4. Process nodes one at a time in the user's requested order or the active ledger order.
5. For each node, gather enough state to decide, not merely report:
   - SSH reachability and hostname.
   - GPU memory, utilization, temperature, and driver visibility.
   - system memory, per-drive disk free space, and realtime disk activity, including system disk, dataset/work SSD, and artifact/output disk when they differ.
   - training/evaluation scheduled tasks and relevant processes.
   - current run ID, epoch/progress, logs or artifact state when the current project context defines how to inspect them.
   - two progress observations 3–5 minutes apart after launch; require `results.csv` row/epoch or mtime advancement. Investigate if no advancement persists for 10 minutes, except during known staging, validation, checkpoint writing, or epoch transitions.
   - known network-risk services such as Delivery Optimization when relevant.
6. Act immediately when the state calls for it.
7. For newly completed runs, verify expected artifacts and collect lightweight results to the local experiment archive before marking them handled.
   For final packaging, split the collected archive into a weights view and a materials package: one folder per run containing only `best.pt` and `last.pt`, plus a separate compressed materials-only package that excludes `.pt`.
8. Verify the action worked before moving to the next node.
9. Report concise status with action taken and next risk.

## Decision Rules

- Active YOLO training with advancing epoch: leave it alone; record status.
- Active training with stale mtime or low GPU use: inspect logs/processes before acting; distinguish IO, eval, crash, and idle states.
- Active evaluation: do not start the next run until formal eval artifacts exist.
- Complete train plus eval: stop stale foreground shell/task if needed, update code patch if required by the current project policy, then select and start a nonduplicate next YOLO run.
- Idle node: verify it is truly idle, then start a nonduplicate run if the node is in scope.
- SSH unreachable: assume possible reboot, network failure, or memory/OOM only after checking context. Retry after a short wait; if the user's policy says SSH loss means memory failure, follow that policy.
- Memory risk: stop known nonessential leak sources first. Do not kill training unless it is clearly duplicated, crashed, or authorized by the user.
- Windows scheduled-task priority: `New-ScheduledTaskSettingsSet` defaults to task priority `7`, so a training launcher and its data-loader children may inherit `BelowNormal` and leave the GPU underfed even though the run is healthy. For training tasks, explicitly set `$settings.Priority = 4` before `Register-ScheduledTask`; keep archive/compression tasks at `BelowNormal`. If a live run is unexpectedly slow, inspect `PriorityClass` only for the process tree bound to its exact `--output-root`, and change only that tree to `Normal`. Do not kill processes or change scientific parameters for this condition.
- GPU temperature control during active training batches: target 78–82°C and make no adjustment in that band; treat 81–82°C as normal. At 83–84°C, observe for 3–5 minutes and reduce the power limit by 5–10W only if temperature stays high or rises. At 85°C or above, reduce by 20–25W immediately and recheck after 3–5 minutes; do not allow sustained operation at or above 85°C. If active batch training stays below 75°C and the current limit is below the GPU's default limit, raise by 5–10W and recheck after 3–5 minutes. Never exceed the default limit without explicit per-node authorization, and never raise power merely to heat an idle, staging, validation, epoch-transition, or IO-bound GPU. Record every adjustment.
- Low disk: treat low free space as an actionable exception, not a passive note. Free space by removing or moving safe non-system, non-active files. Do not move active datasets/workdirs during a running run. If safe cleanup is not possible, avoid producing new files on the low-space drive, redirect new work/output paths to a drive with enough free space, and monitor that node more frequently.
- Wrong-disk IO: all batch and repeated-read IO must hit the real C-drive SSD. Mechanical drives may receive output writes but must not supply dataset, workdir, staging, hardlink cache, manifests, CSVs, checkpoints used as active input, or data-loader reads. Lightweight monitoring reads of small output metadata are acceptable. Sustained HDD reads during training are actionable even when output writes are expected.
- Data uncertainty: verify manifests, counts, paths, and timestamps before starting or recovering training. Do not "fix" by renaming alone.

## Duplicate Prevention

Before starting any YOLO run:

- Confirm the run's manifest exists and matches the intended experiment family.
- Confirm no running task or process already owns the run.
- Confirm output paths for the run are absent, or are already complete and should not be rerun.
- Confirm preflight, post-train, `runs`, `eval`, and repro/output artifacts do not indicate an existing valid run.
- If partial outputs exist, inspect why. Preserve or suffix old partial outputs only when necessary and after verifying the data/run identity.
- Choose the next run from the active experiment matrix or user-approved scheduler, not from guesswork.

## Deployment Workflow

For a new or repaired node:

1. Configure SSH service, firewall, authorized keys, and ACLs.
2. Stop or disable known network-leak services when appropriate.
3. Confirm GPU driver with `nvidia-smi`; install/reboot/recheck if needed.
4. Confirm disk layout and choose SSD-backed dataset/work roots when performance matters.
5. Pull code, environment, manifests, and datasets directly from a source node or remote source, not via local staging for large files.
6. Validate environment with `uv`, project imports, GPU visibility, and required paths.
7. Validate dataset/manifests before training.
8. Start the selected nonduplicate YOLO run in a foreground/interactive task.
9. Recheck after launch to confirm it moved from preflight/scanning into real YOLO training or evaluation.

## Reporting Format

Use compact, action-oriented summaries:

- Node identifier and current IP if the user tracks both.
- Current state: training, eval, complete, idle, deploying, unreachable, or blocked.
- Run ID and epoch/progress when applicable.
- GPU temperature/utilization/memory, system memory, and disk free-space warnings for relevant drives.
- Action taken or next action.

When a run is completed remotely but not archived locally, distinguish remote completion from local collection.

## Resources

- `scripts/probe-windows-gpu-node.ps1`: fixed PowerShell probe for one Windows GPU node. It reports GPU, memory, disks, SSH/DoSvc state, port 22 listeners, top memory processes, YOLO-like tasks, and YOLO-like process command lines. It does not parse project artifacts, select runs, or start training.

## Protected Context

If the project has protected archives, session logs, or ledgers, respect the current user policy. Read them only when needed for context, and write only when explicitly instructed.
