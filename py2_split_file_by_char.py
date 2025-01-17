param(
    [string]$FileName,
    [int]$ChunkSize
)

if (-not $FileName -or -not $ChunkSize) {
    Write-Host "Usage: powershell -File split_file.ps1 -FileName <file_name> -ChunkSize <chunk_size>"
    exit
}

try {
    $Content = Get-Content -Raw -Path $FileName
    $BaseName = [System.IO.Path]::GetFileNameWithoutExtension($FileName)
    $Extension = [System.IO.Path]::GetExtension($FileName)

    $Chunks = @()
    for ($i = 0; $i -lt $Content.Length; $i += $ChunkSize) {
        $Chunks += $Content.Substring($i, [Math]::Min($ChunkSize, $Content.Length - $i))
    }

    for ($j = 0; $j -lt $Chunks.Count; $j++) {
        $ChunkFileName = "{0}_part_{1}{2}" -f $BaseName, ($j + 1), $Extension
        $Chunks[$j] | Set-Content -Path $ChunkFileName
        Write-Host "Created: $ChunkFileName"
    }
} catch {
    Write-Host "Error: $_"
}
