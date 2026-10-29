$base = "D:\git\mulesoft\projects\api-cert-level-2\src\test\resources"
$dirs = Get-ChildItem $base -Directory -Filter "embedded-dw_*"
foreach ($dir in $dirs) {
    $longPath = "\\?\" + $dir.FullName
    [System.IO.Directory]::Delete($longPath, $true)
    Write-Host "Deleted: $($dir.Name)"
}
Write-Host "Done."
