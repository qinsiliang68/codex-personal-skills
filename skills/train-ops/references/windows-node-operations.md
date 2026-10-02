# Windows node operations

Read this for Windows LAN training/inference nodes. Use the current machine inventory and user-approved policy; the examples below are operating profiles, not universal limits or permission to change a GPU.

## Set the active fleet policy

Record normal and temperature-sensitive nodes separately in the private inventory. Do not embed names/IPs here. Keep each node's approved power range, concurrency and exclusions explicit. Its active thermal policy must specify the target band, sampling interval, sustained-temperature trigger in seconds or consecutive samples, immediate-action ceiling, permitted response and recheck time. Reuse an existing applicable approved policy without asking again. Missing policy values are unknown, not defaults: continue independent read-only checks, but resolve them before dependent launches or tuning. If overheating is observed, follow any already-approved immediate response and report missing decisions promptly; do not invent a grace period or a stop/reboot permission.

An established fleet may use these settings only when its current policy explicitly adopts them; this table is not a complete active policy:

| Condition | Example operating policy |
| --- | --- |
| Ordinary node, dedicated active compute | 80–83°C operating band with an 83°C immediate-action ceiling. Use the recorded sustained-temperature trigger for earlier intervention; it never adds a grace period at the ceiling. |
| Temperature-sensitive node | 65–70°C band with a 70°C immediate-action ceiling. Apply the recorded response at the ceiling and the earlier-intervention rule before it where specified. |
| Power adjustment | Change in 5 W steps within that node's authorized and supported range. A 3–5 minute recheck applies only to routine adjustment below the immediate-action ceiling; reaching that ceiling triggers its recorded response and shorter recheck, without waiting for the routine timer. |
| Unoccupied inference helper | Three independent inference processes only if the active policy permits three and the established workload fits its resources. |
| Shared node with real competing CPU/interactive work | Reduce to one process or yield entirely according to user policy and measured interference. |
| Another user's GPU computation or an explicit exclusion | Do not assign GPU work unless coexistence is explicitly permitted and verified. |

A sensitive node is not automatically limited to two processes: current policy may authorize three with a lower thermal ceiling. Never treat more processes as necessarily faster; compare total throughput, memory, temperature, and result-return cost.

Adjust power based on sustained active compute, utilization, actual draw versus limit, temperature trend, and measured speed. Low temperature during staging, validation, idle time, or an IO stall does not justify raising power. Stay within the device's supported range; exceeding its default limit requires explicit per-node permission. Do not install automatic temperature controllers unless requested.

Use the current fleet timezone and its maximum safe gap between inspections. After each inspection, set the next in-session wait from the earliest predicted event using measured progress and recent unit time: for example, if a ten-window transfer batch should finish in five minutes, inspect near then instead of waiting for a routine 20- or 30-minute slot. Include the next temperature check, task completion, active transfer or verifier, and any known availability change. If no event can be estimated reliably, use the fleet's approved safety interval. Recalculate immediately after each event or action; faults and process exits warrant prompt inspection. Never turn a one-day class stop/resume time into a permanent timetable. A no-training/no-inference class period overrides normal concurrency; authorized background preparation may continue only within its resource restrictions.

## Background compute and independent progress display

- In this Windows LAN profile, run training and inference in an approved background task/process by default so closing a terminal does not stop computation. A user's explicit foreground requirement overrides this default. Background execution does not override the machine owner's availability rules.
- On designated training nodes, show that node's native training/inference output in a separate ordinary, non-elevated foreground terminal. Forward existing stdout/stderr; do not replace it with a dashboard or show another node's progress.
- Closing the display must leave compute running. If recovery within about one minute is requested, restore **only a missing display** within that interval. Leave an existing display alone; do not periodically close/reopen it, duplicate it, or restart training to restore it.
- Helpers can run without a display when requested. SSH, transfer, compression, installation and housekeeping run without visible consoles. Use `Start-Process -WindowStyle Hidden` for background helpers; visible windows are reserved for the approved display.
- After completion, close the obsolete display and stop its restoration mechanism within authorization so it cannot resurrect an empty window.

For scheduled training/inference tasks, inspect priority and execution limits. `New-ScheduledTaskSettingsSet` defaults to priority 7; set `$settings.Priority = 4` before `Register-ScheduledTask` when Normal priority is intended. Do not arbitrarily force BelowNormal or one CPU core for decoding. For a slow live run, inspect and change only the process tree bound to its exact `--output-root` under applicable permission. Do not change scientific parameters or kill training to repair priority.

For an authorized long-running task that must not expire, verify `ExecutionTimeLimit = PT0S`. Do not introduce a limit that silently kills training. Check executable, arguments, working directory, user/logon type, task result, and actual parent/child processes; scheduler status alone is insufficient.

## Storage, memory, and connection checks

For a new/repaired node, first verify identity and authorized access, then deploy the established code/environment/data package from its approved source. Configure SSH, firewall, keys/ACLs, drivers or startup settings only when deployment authorization covers them. Verify environment imports, GPU visibility, real paths, dataset/cache readiness and package hashes before starting work. Driver installation or reboot is not implied by a monitoring request.

- Resolve repeated-read paths to physical storage: dataset, workdir, staging, base/active cache, CSV/manifests, active checkpoint input, code and runtime. Use the fleet's real SSD. If C: is its only SSD, inputs belong on C:, not an HDD exposed through a junction.
- HDDs may store approved outputs, logs, saved checkpoints and packages. Lightweight output-metadata reads are fine. Copy an archived checkpoint to appropriate input storage when repeated reads require it; never mutate the archived source.
- Include cache/staging growth in free-space checks. Move only authorized non-active files; protect files used by PFC, Abaqus and other users. Do not convert data preparation into general cleanup.
- Check available physical RAM, process consumption, and actual allocation/1455/OOM errors. High committed-memory usage alone does not establish failure or justify stopping healthy computation.
- Identify this task's SSH/SCP/SFTP processes and connections, including configured forwarded ports, when diagnosing contention or abandoned work. Do not mistake a user-owned tunnel for an abandoned control session or kill it. Node-to-node transfers count toward observed network and disk load, but there is no fixed fleet-wide SSH connection cap; reduce a concurrent burst only when measured resource pressure or connection failures warrant it.
- A dropped SSH control connection can coexist with healthy background training. Verify process/output identity after reconnecting before relaunch. Reboot/wake tests require authorization and must not interrupt other users' work.

## Optional raw-fact probe

Use `../scripts/probe-windows-gpu-node.ps1` only when its bundle is useful; otherwise use smaller direct probes. It runs locally on the inspected Windows node and makes no SSH connection or operational changes.

Pass `-TaskNamePattern` and `-ProcessPattern` for the project's names. Defaults are discovery hints, not a complete run inventory. The probe prints GPU power/identity, memory, disks, relevant services/listeners, and candidate tasks/processes, preserving full command lines and parent IDs.

Each section emits status and counts where applicable. `PROBE_STATUS=INCOMPLETE` and exit code 1 mean a query failed; do not turn missing facts into an idle/healthy verdict. `OK` means queries ran, not that the node is safe. Perform ownership, physical-storage/IO, task-exit, progress, and artifact checks separately. Full command lines may contain sensitive arguments: keep raw output in approved private storage and redact before sharing.
