param(
  [string]$SrcRoot = "Logistics Route Optimization Platform/src/app",
  [switch]$Json
)

$uiDir = Join-Path $SrcRoot "components/ui"
if (-not (Test-Path $uiDir)) {
  Write-Error "No se encontro directorio UI: $uiDir"
  exit 1
}

$uiFiles = Get-ChildItem $uiDir -File -Filter *.tsx | Select-Object -ExpandProperty Name
$imports = rg "components/ui/|../components/ui/|../ui/" $SrcRoot -g "*.tsx" -g "*.ts" -n --no-heading

$used = New-Object System.Collections.Generic.HashSet[string]
foreach ($line in $imports) {
  if ($line -match "(components/ui/|../components/ui/|../ui/)([a-z0-9\-]+)") {
    $name = $matches[2]
    if (-not $name) { continue }
    [void]$used.Add(($name + ".tsx").ToLower())
  } elseif ($line -match "components/ui/([A-Za-z0-9\-_]+)") {
    [void]$used.Add(($matches[1] + ".tsx").ToLower())
  }
}

$unused = $uiFiles | Where-Object { -not $used.Contains($_.ToLower()) } | Sort-Object

$report = [ordered]@{
  totalUiFiles = $uiFiles.Count
  usedUiFiles = $used.Count
  unusedCandidates = $unused
}

if ($Json) {
  $report | ConvertTo-Json -Depth 4
} else {
  Write-Host ("UI files total: " + $report.totalUiFiles)
  Write-Host ("UI files usados: " + $report.usedUiFiles)
  Write-Host "Candidatos no referenciados:"
  foreach ($item in $unused) {
    Write-Host (" - " + $item)
  }
}
