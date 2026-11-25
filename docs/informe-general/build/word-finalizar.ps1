# Abre el .docx generado en Microsoft Word, actualiza el índice y los campos, guarda y exporta el PDF equivalente.
# Uso: powershell -File word-finalizar.ps1 <entrada.docx> <salida.pdf>
param([string]$Docx, [string]$Pdf)
$w = New-Object -ComObject Word.Application
$w.Visible = $false
$w.DisplayAlerts = 0
try {
    $d = $w.Documents.Open($Docx, $false, $false)
    $d.Repaginate()
    foreach ($t in $d.TablesOfContents) { $t.Update() }
    $d.Fields.Update() | Out-Null
    $d.Repaginate()
    foreach ($t in $d.TablesOfContents) { $t.Update() }      # segunda pasada: los números de página ya son estables
    $d.Save()
    # 17 = wdExportFormatPDF; CreateBookmarks 1 = encabezados (marcadores del PDF)
    $d.ExportAsFixedFormat($Pdf, 17, $false, 0, 0, 1, 1, 0, $true, $true, 1, $true, $true, $false)
    "paginas=" + $d.ComputeStatistics(2)
    $d.Close(0)
} finally { $w.Quit() }
