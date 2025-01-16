param (
    [string]$FilePath,   # Path to the large XML file
    [int]$ChunkSize = 100,  # Number of elements per chunk
    [string]$OutputDir = "./xml_chunk_output"  # Directory for output chunks
)

# Check if file exists
if (-not (Test-Path $FilePath)) {
    Write-Error "File '$FilePath' not found."
    exit
}

# Ensure output directory exists
if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir | Out-Null
}

# Detect parent tag
$ParentTag = Select-String -Path $FilePath -Pattern "</([^>]+)>" | ForEach-Object {
    if ($_.Matches.Groups[1].Value -ne "root") {
        $_.Matches.Groups[1].Value
    }
} | Select-Object -First 1

if (-not $ParentTag) {
    Write-Error "Could not detect a parent tag in the XML file."
    exit
}

Write-Host "Detected parent tag: <$ParentTag>"

# Initialize variables
$ChunkCount = 0
$RecordCount = 0
$ChunkFile = ""
$CurrentChunk = @()

# Process the XML file line by line
Get-Content $FilePath | ForEach-Object {
    $line = $_

    if ($line -match "<$ParentTag>") {
        $RecordCount++
    }

    # Start a new chunk
    if ($RecordCount % $ChunkSize -eq 1) {
        $ChunkCount++
        $ChunkFile = "$OutputDir/chunk_$ChunkCount.xml"
        Write-Host "Creating $ChunkFile"
        Set-Content -Path $ChunkFile -Value "<root>"
    }

    # Add the current line to the current chunk
    Add-Content -Path $ChunkFile -Value $line

    # Close the chunk when the limit is reached
    if ($line -match "</$ParentTag>" -and $RecordCount % $ChunkSize -eq 0) {
        Add-Content -Path $ChunkFile -Value "</root>"
    }
}

# Finalize the last chunk if it is not closed
if ($RecordCount % $ChunkSize -ne 0) {
    Add-Content -Path $ChunkFile -Value "</root>"
}

Write-Host "XML split completed. $ChunkCount files created in '$OutputDir'."
