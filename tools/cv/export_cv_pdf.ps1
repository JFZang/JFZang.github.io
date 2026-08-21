$toolDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent (Split-Path -Parent $toolDir)
$docx = Join-Path $toolDir 'source\cut_Jeff_Zhang_CV.docx'
$pdf = Join-Path $projectRoot 'assets\documents\Jiefu-Zhang-CV.pdf'

if (-not (Test-Path $docx)) {
  throw "Missing source DOCX: $docx"
}

$word = New-Object -ComObject Word.Application
$word.Visible = $false

try {
  $doc = $word.Documents.Open($docx, $false, $true)
  $doc.ExportAsFixedFormat($pdf, 17)
  $doc.Close($false)
}
finally {
  $word.Quit()
}

Write-Host "Wrote $pdf"
