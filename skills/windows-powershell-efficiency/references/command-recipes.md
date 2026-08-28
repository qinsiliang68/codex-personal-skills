# PowerShell Command Recipes

Read only the section needed for the current operation. These are preferred patterns, not mandatory syntax when a project-specific tool provides a better answer.

## Concise initial probe

Use only when the facts are not already known:

```powershell
$PSVersionTable.PSVersion
(Get-Location).Path
Get-Command git, python, py, uv, rg, fd -ErrorAction SilentlyContinue |
    Select-Object Name, Source
```

Do not run several equivalent `where.exe`, `Get-Command`, and `--version` probes afterward. If a project virtual environment or tool manifest already identifies the runtime, inspect that directly.

## Inspect a known directory

```powershell
Get-ChildItem -LiteralPath $path -Force |
    Select-Object -First 100 Name, Mode, Length
```

For a single known path:

```powershell
Test-Path -LiteralPath $path
Resolve-Path -LiteralPath $path
```

For two path predicates, parenthesize each cmdlet call before applying Boolean operators:

```powershell
if ((Test-Path -LiteralPath $first) -or (Test-Path -LiteralPath $second)) {
    # At least one path exists.
}
```

Do not write `Test-Path -LiteralPath $first -or Test-Path -LiteralPath $second`; Windows PowerShell may treat the latter tokens as additional parameters to the first command.

## Find repository files

For tracked files:

```powershell
git ls-files
git ls-files '*trainer*'
```

With ripgrep:

```powershell
rg --files -g 'train.py'
rg --files src tests | Select-Object -First 100
```

If indexed tools cannot answer the question, use targeted recursion:

```powershell
Get-ChildItem -LiteralPath $sourceRoot -File -Recurse -Filter 'train.py' -ErrorAction SilentlyContinue |
    Select-Object -First 20 -ExpandProperty FullName
```

`Select-Object -First` limits displayed results, not necessarily traversal cost. Narrow `$sourceRoot`, use `-Filter`, and use a suitable `-Depth` when possible.

## Search text

Search expected directories first:

```powershell
rg -n 'target_text' src tests
```

Use task-relevant exclusions for a wider search:

```powershell
rg -n 'target_text' . `
    -g '!node_modules/**' `
    -g '!.venv/**' `
    -g '!build/**' `
    -g '!dist/**'
```

Do not exclude directories that may own the requested behavior. In particular, keep `.github` in scope for CI, automation, template, or dependency-management work.

`rg --max-count 50` caps matches per file, not globally. To cap emitted lines globally:

```powershell
rg -n 'target_text' src tests | Select-Object -First 50
```

## Read selected content

Beginning of a file:

```powershell
Get-Content -LiteralPath $path -TotalCount 120
```

Selected range:

```powershell
Get-Content -LiteralPath $path |
    Select-Object -Skip 200 -First 100
```

For code, first locate symbols and then read their surrounding region:

```powershell
rg -n 'class Trainer|def train|def validate' $path
```

Do not reread unchanged content already available in the task context.

## Read a bounded suffix from a live progress log

`Get-Content -Tail` is line-bounded, not byte-bounded. Do not use it for a live log that may contain carriage-return-only progress updates. Read at most the required suffix while allowing the producer to keep the file open:

```powershell
[int64]$maxBytes = 65536
$stream = [System.IO.File]::Open(
    $path,
    [System.IO.FileMode]::Open,
    [System.IO.FileAccess]::Read,
    [System.IO.FileShare]::ReadWrite
)
try {
    [int64]$take = [Math]::Min($maxBytes, $stream.Length)
    [void]$stream.Seek(-$take, [System.IO.SeekOrigin]::End)
    $buffer = New-Object byte[] ([int]$take)
    $read = $stream.Read($buffer, 0, $buffer.Length)
} finally {
    $stream.Dispose()
}
$suffix = [Text.Encoding]::Unicode.GetString($buffer, 0, $read)
```

Select the encoding from the producer or an encoding probe; Windows PowerShell output captured by `Tee-Object` is often UTF-16LE (`[Text.Encoding]::Unicode`), but do not assume that for every file. Parse and emit only the final marker needed for the decision.

An SSH timeout only proves that the client stopped waiting. Before retrying a timed-out remote diagnostic, inspect remote processes using exact command-line, parent PID, creation time, and PID evidence. Stop only the confirmed diagnostic process; never stop broad `powershell.exe` or `python.exe` process sets.

## Inspect Git state compactly

```powershell
git status --short
git diff --stat
git diff -- 'src/trainer.py'
git log -n 5 --oneline
```

Request the full repository diff only when the complete diff is itself necessary evidence.

## Construct and reuse paths

```powershell
$repoRoot = (Get-Location).Path
$sourceRoot = Join-Path $repoRoot 'src'
$configPath = Join-Path $repoRoot 'configs\train.yaml'
```

Use `-LiteralPath` with known filenames, especially when brackets or wildcard characters may appear.

Keep token boundaries explicit, especially in generated or encoded commands:

```powershell
$transactions = Join-Path -Path $outputRoot -ChildPath '03_epoch_transactions'
foreach ($file in $files) {
    # Work with one item.
}
```

Do not remove the spaces before variables or after `in`; `Join-Path$outputRoot` and `foreach ($file in$files)` are not safe compact equivalents.

## Create a ZIP from directory contents

`-LiteralPath` does not expand `*`. To archive the children of an already resolved directory without adding the directory itself as another level:

```powershell
$ErrorActionPreference = 'Stop'
$sourceRoot = (Resolve-Path -LiteralPath $sourceRoot).Path
if (Test-Path -LiteralPath $zipPath) {
    throw "Archive already exists: $zipPath"
}
Compress-Archive -Path (Join-Path $sourceRoot '*') -DestinationPath $zipPath -CompressionLevel Optimal
if (-not (Test-Path -LiteralPath $zipPath -PathType Leaf)) {
    throw "Archive was not created: $zipPath"
}
```

Do not write `Compress-Archive -LiteralPath (Join-Path $sourceRoot '*')`: the wildcard remains literal, the archive may not be created, and Windows PowerShell can continue after non-terminating path errors unless error handling is explicit.

## Run native programs safely

```powershell
pytest tests\test_model.py -q
$testCode = $LASTEXITCODE

if ($testCode -ne 0) {
    Write-Output "pytest exit code: $testCode"
}
```

For Windows PowerShell 5.1 compatibility, issue dependent commands separately and test `$LASTEXITCODE` instead of assuming `&&`.

## Pipe compound statements safely

Windows PowerShell may reject a language-level `foreach` statement piped directly into another command:

```powershell
foreach ($item in $items) {
    [pscustomobject]@{ Name = $item.Name }
} | ConvertTo-Json
```

Collect the statement results first:

```powershell
$results = foreach ($item in $items) {
    [pscustomobject]@{ Name = $item.Name }
}
$results | ConvertTo-Json
```

An explicit collecting expression is also valid when it remains readable:

```powershell
@(foreach ($item in $items) {
    [pscustomobject]@{ Name = $item.Name }
}) | ConvertTo-Json
```

This restriction concerns the language statement. The pipeline cmdlet `ForEach-Object` is a different construct and can participate in a pipeline normally.

## Aggregate ordered dictionaries and finalize receipts safely

`[ordered]@{}` creates an `OrderedDictionary`. In Windows PowerShell 5.1, its keys are not reliable input properties for `Measure-Object -Property`:

```powershell
$rows += [ordered]@{ bytes = [int64]$item.Length }
$total = ($rows | Measure-Object -Property bytes -Sum).Sum
```

Accumulate the scalar while constructing rows, and use `[pscustomobject]` when later pipeline commands need properties:

```powershell
$rows = @()
[int64]$total = 0
foreach ($item in $items) {
    [int64]$bytes = $item.Length
    $rows += [pscustomobject]@{ bytes = $bytes }
    $total += $bytes
}
```

For a machine-readable receipt, keep the default state failed. Complete every fallible calculation before setting success, and use dictionary indexers for state updates:

```powershell
$state = [ordered]@{ status = 'FAILED'; error = $null }
try {
    # Perform and verify the operation, then finish all receipt fields.
    $state['total_bytes'] = $total
    $state['status'] = 'PASS'
} catch {
    $state['status'] = 'FAILED'
    $state['error'] = $_.Exception.Message
}
$json = $state | ConvertTo-Json -Depth 4
```

Do not perform another fallible receipt calculation after assigning `PASS`. A failed operation must not leave a receipt containing both a success status and an error.

For a JSON object used as a dictionary, materialize its adapted property collection before counting:

```powershell
$entryCount = @($jsonObject.PSObject.Properties).Count
```

Do not use `$jsonObject.PSObject.Properties.Count`; Windows PowerShell 5.1 can member-enumerate the child properties and emit an array of their individual `Count` values instead of one scalar count.

## Select a Python runtime once

Prefer the interpreter established by the project. If a local virtual environment exists and is intended for the task:

```powershell
.\.venv\Scripts\python.exe script.py
```

Do not alternate between `python`, `py`, `uv run python`, and virtual-environment interpreters without a concrete reason.

## Avoid nested quoting

Delimit a variable before a literal colon in an expandable string:

```powershell
"${path}:$message"
```

Do not write `"$path:$message"`; PowerShell parses `$path:` as a scoped variable reference and fails before execution.

For short, one-off multiline Python input:

```powershell
@'
print("literal input")
'@ | python -
```

Use a durable project script only when the logic is part of the approved task and should be maintained or reused.

## Validate progressively

Examples for a Python project:

```powershell
python -m py_compile src\trainer.py
pytest tests\test_trainer.py::test_resume_training -q
pytest tests\test_trainer.py -q
ruff check src\trainer.py
```

Run broader checks only when the affected surface or repository policy justifies them.

## Show exact properties when needed

Prefer raw compact values:

```powershell
Get-ChildItem -LiteralPath $path -File |
    Select-Object -ExpandProperty FullName
```

If PowerShell's default table truncates a diagnostic property, a final formatter is appropriate:

```powershell
Get-Item -LiteralPath $path |
    Select-Object FullName, Length, Attributes |
    Format-List
```
