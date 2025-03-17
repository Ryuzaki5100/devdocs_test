param (
    [string]$inputFile,
    [string]$outputDir,
    [string]$imageDir
)

$json = Get-Content -Raw $inputFile | ConvertFrom-Json
foreach ($pair in $json.PSObject.Properties) {
    $filePath = $pair.Name
    $fileName = [System.IO.Path]::GetFileNameWithoutExtension($filePath) + '.md'
    $outputPath = Join-Path $outputDir $fileName
    $content = $pair.Value

    # Ensure the image directory exists
    if (!(Test-Path $imageDir)) {
        New-Item -ItemType Directory -Path $imageDir | Out-Null
    }

    # Extract base64 images and save them as PNG files
    $imageRegex = '(?<=!\[.*?\]\(data:image/png;base64,)([^)]+)(?=\))'
    $index = 1

    foreach ($match in [regex]::Matches($content, $imageRegex)) {
        $base64String = $match.Groups[1].Value
        $imageFileName = [System.IO.Path]::GetFileNameWithoutExtension($fileName) + '_img' + $index + '.png'
        $imagePath = Join-Path $imageDir $imageFileName

        # Convert base64 string to binary and save as PNG
        [System.IO.File]::WriteAllBytes($imagePath, [Convert]::FromBase64String($base64String))

        # Fix the image reference in the Markdown
        $content = $content -replace ('!\[.*?\]\(data:image/png;base64,' + [regex]::Escape($base64String) + '\)'), "![Image](images/$imageFileName)"
        $index++
    }

    # Write the processed markdown file
    $content | Set-Content -Path $outputPath -Encoding UTF8
}

Write-Host "Markdown files created successfully!"
