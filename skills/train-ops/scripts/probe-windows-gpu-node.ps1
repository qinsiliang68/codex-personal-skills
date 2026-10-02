param(
    [ValidateRange(1, 50)][int]$TopProcessCount = 8,
    [string]$TaskNamePattern = "YOLO*",
    [string]$ProcessPattern = "yolo|ultralytics|train|evaluate|infer|predict|uv run"
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"
$script:ProbeFailed = $false

function Write-Kv {
    param([string]$Key, [object]$Value)
    if ($null -eq $Value) {
        Write-Output "$Key="
    } else {
        Write-Output "$Key=$Value"
    }
}

function Invoke-ProbeSection {
    param([string]$Name, [scriptblock]$Query)
    try {
        & $Query
        Write-Kv "${Name}_STATUS" "OK"
    } catch {
        $script:ProbeFailed = $true
        Write-Kv "${Name}_STATUS" "ERROR"
        Write-Kv "${Name}_ERROR" ($_.Exception.Message -replace '[\r\n]+', ' ')
    }
}

Write-Kv "TIME" (Get-Date -Format "o")
Write-Kv "HOST" $env:COMPUTERNAME
Write-Kv "USER" $env:USERNAME

Invoke-ProbeSection "MEMORY" {
    $os = Get-CimInstance Win32_OperatingSystem
    if ($null -eq $os) { throw "Operating system query returned no record." }
    Write-Kv "UPTIME" $os.LastBootUpTime.ToString("yyyy-MM-dd HH:mm:ss")
    Write-Kv "MEM_FREE_GB" ([math]::Round($os.FreePhysicalMemory / 1MB, 2))
    Write-Kv "MEM_TOTAL_GB" ([math]::Round($os.TotalVisibleMemorySize / 1MB, 2))
}

Invoke-ProbeSection "GPU" {
    if (-not (Get-Command nvidia-smi -ErrorAction SilentlyContinue)) {
        throw "nvidia-smi is unavailable."
    }
    $gpu = & nvidia-smi --query-gpu=uuid,name,driver_version,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,power.limit,power.default_limit --format=csv,noheader,nounits
    $gpuExit = $LASTEXITCODE
    Write-Kv "NVIDIA_SMI_EXIT" $gpuExit
    if ($gpuExit -ne 0 -or @($gpu).Count -eq 0) { throw "nvidia-smi returned no usable result (exit $gpuExit)." }
    Write-Kv "GPU_FIELDS" "uuid,name,driver_version,memory.used,memory.total,utilization.gpu,temperature.gpu,power.draw,power.limit,power.default_limit"
    foreach ($line in @($gpu)) {
        Write-Kv "GPU" $line
    }
}

Invoke-ProbeSection "DISKS" {
    Get-PSDrive -PSProvider FileSystem | Sort-Object Name | ForEach-Object {
        Write-Kv "DISK_$($_.Name)" ("free_gb={0};used_gb={1};root={2}" -f ([math]::Round($_.Free / 1GB, 2)), ([math]::Round($_.Used / 1GB, 2)), $_.Root)
    }
}

Invoke-ProbeSection "SERVICES" {
    $services = @(Get-Service | Where-Object { $_.Name -in @('sshd', 'ssh-agent', 'DoSvc') })
    Write-Kv "SERVICE_COUNT" $services.Count
    $services | Sort-Object Name | ForEach-Object {
        Write-Kv "SERVICE_$($_.Name)" "$($_.Status),$($_.StartType)"
    }
}

Invoke-ProbeSection "LISTENERS" {
    $listeners = @(Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq 22 })
    Write-Kv "PORT22_LISTEN_COUNT" $listeners.Count
    $listeners | ForEach-Object {
        Write-Kv "PORT22_LISTEN" "$($_.LocalAddress):$($_.LocalPort);pid=$($_.OwningProcess)"
    }
}

Invoke-ProbeSection "TASKS" {
    $tasks = @(Get-ScheduledTask | Where-Object { $_.TaskName -like $TaskNamePattern })
    Write-Kv "TASK_PATTERN" $TaskNamePattern
    Write-Kv "TASK_COUNT" $tasks.Count
    $tasks | Sort-Object TaskPath, TaskName | ForEach-Object {
        Write-Kv "TASK" "$($_.TaskPath)$($_.TaskName),$($_.State)"
    }
}

Invoke-ProbeSection "PROCESSES" {
    $processes = @(Get-CimInstance Win32_Process)
    $processes | Sort-Object WorkingSetSize -Descending | Select-Object -First $TopProcessCount | ForEach-Object {
        Write-Kv "TOP_MEM_PROC" ("pid={0};name={1};gb={2}" -f $_.ProcessId, $_.Name, ([math]::Round($_.WorkingSetSize / 1GB, 2)))
    }
    $candidates = @($processes | Where-Object { $_.CommandLine -match $ProcessPattern })
    Write-Kv "PROCESS_PATTERN" $ProcessPattern
    Write-Kv "TRAINING_LIKE_PROC_COUNT" $candidates.Count
    $candidates | ForEach-Object {
        $cmd = $_.CommandLine -replace '[\r\n]+', ' '
        Write-Kv "TRAINING_LIKE_PROC" "pid=$($_.ProcessId);parent=$($_.ParentProcessId);name=$($_.Name);cmd=$cmd"
    }
}

if ($script:ProbeFailed) {
    Write-Kv "PROBE_STATUS" "INCOMPLETE"
    exit 1
}
Write-Kv "PROBE_STATUS" "OK"
