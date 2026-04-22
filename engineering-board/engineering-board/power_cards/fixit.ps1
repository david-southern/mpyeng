$file = "c:\Users\David\source\repos\space-sim\engineering-board\engineering-board\power_cards\animation.py"
$content = Get-Content $file -Raw

# Collapse each bytes([\n  val,\n  val,\n  ...\n]) into bytes([val, val, ...])
# Pattern: bytes(\n followed by lines of digits/commas/whitespace, ending with ]\n)
$pattern = '(?m)bytes\(\s*\[\s*\n((?:\s*\d+,?\s*\n)+)\s*\]\s*\)'
$collapsed = [regex]::Replace($content, $pattern, {
        param($m)
        $inner = $m.Groups[1].Value
        # Extract all numbers
        $nums = [regex]::Matches($inner, '\d+') | ForEach-Object { $_.Value }
        "bytes([" + ($nums -join ", ") + "])"
    })

Set-Content $file $collapsed -NoNewline
Write-Host "Done. Collapsed $([regex]::Matches($content, $pattern).Count) bytes() arrays."