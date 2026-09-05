param(
    [int]$TopProcessCount = 8
)

$ErrorActionPreference = "SilentlyContinue"
$ProgressPreference = "SilentlyContinue"

function Write-Kv {
    param([string]$Key, [object]$Value)
    if ($null -eq $Value) {
        Write-Output "$Key="
    } else {
        Write-Output "$Key=$Value"
    }
}

Write-Kv "TIME" (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Write-Kv "HOST" $env:COMPUTERNAME
Write-Kv "USER" $env:USERNAME

$os = Get-CimInstance Win32_OperatingSystem
if ($os) {
    Write-Kv "UPTIME" $os.LastBootUpTime.ToString("yyyy-MM-dd HH:mm:ss")
    Write-Kv "MEM_FREE_GB" ([math]::Round($os.FreePhysicalMemory / 1MB, 2))
    Write-Kv "MEM_TOTAL_GB" ([math]::Round($os.TotalVisibleMemorySize / 1MB, 2))
}

if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    $gpu = & nvidia-smi --query-gpu=name,driver_version,memory.used,memory.total,utilization.gpu,temperature.gpu --format=csv,noheader,nounits 2>$null
    Write-Kv "NVIDIA_SMI_EXIT" $LASTEXITCODE
    foreach ($line in @($gpu)) {
        Write-Kv "GPU" $line
    }
} else {
    Write-Kv "NVIDIA_SMI" "missing"
    Get-CimInstance Win32_VideoController | ForEach-Object {
        Write-Kv "GPU_WMI" $_.Name
    }
}

Get-PSDrive -PSProvider FileSystem | Sort-Object Name | ForEach-Object {
    Write-Kv "DISK_$($_.Name)" ("free_gb={0};used_gb={1};root={2}" -f ([math]::Round($_.Free / 1GB, 2)), ([math]::Round($_.Used / 1GB, 2)), $_.Root)
}

Get-Service sshd, ssh-agent, DoSvc -ErrorAction SilentlyContinue | Sort-Object Name | ForEach-Object {
    Write-Kv "SERVICE_$($_.Name)" "$($_.Status),$($_.StartType)"
}

Get-NetTCPConnection -LocalPort 22 -State Listen -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Kv "PORT22_LISTEN" "$($_.LocalAddress):$($_.LocalPort);pid=$($_.OwningProcess)"
}

Get-CimInstance Win32_Process |
    Sort-Object WorkingSetSize -Descending |
    Select-Object -First $TopProcessCount |
    ForEach-Object {
        Write-Kv "TOP_MEM_PROC" ("pid={0};name={1};gb={2}" -f $_.ProcessId, $_.Name, ([math]::Round($_.WorkingSetSize / 1GB, 2)))
    }

Get-ScheduledTask -TaskName "YOLO*" -ErrorAction SilentlyContinue |
    Sort-Object TaskName |
    ForEach-Object {
        Write-Kv "YOLO_TASK" "$($_.TaskName),$($_.State)"
    }

Get-CimInstance Win32_Process |
    Where-Object { $_.CommandLine -match "yolo|ultralytics|train|evaluate|uv run" } |
    ForEach-Object {
        $cmd = $_.CommandLine
        if ($cmd -and $cmd.Length -gt 360) {
            $cmd = $cmd.Substring(0, 360)
        }
        Write-Kv "TRAINING_LIKE_PROC" "pid=$($_.ProcessId);name=$($_.Name);cmd=$cmd"
    }
