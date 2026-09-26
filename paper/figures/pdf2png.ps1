# Render one page (0-based) of a PDF to PNG with the Windows built-in PDF engine (Windows.Data.Pdf); preview only.
# Usage: powershell -File pdf2png.ps1 <in.pdf> <out.png> [scale] [page]
param([string]$In, [string]$Out, [double]$Scale = 3.0, [int]$Page = 0)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Data.Pdf.PdfDocument, Windows.Data.Pdf, ContentType = WindowsRuntime]
$null = [Windows.Storage.Streams.InMemoryRandomAccessStream, Windows.Storage.Streams, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$t) { $task = $asTask.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(); $task.Result }
$asAction = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
    $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and
    $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncAction' })[0]
function AwaitAction($op) { $task = $asAction.Invoke($null, @($op)); $task.Wait() }

$file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync((Resolve-Path $In).Path)) ([Windows.Storage.StorageFile])
$doc = Await ([Windows.Data.Pdf.PdfDocument]::LoadFromFileAsync($file)) ([Windows.Data.Pdf.PdfDocument])
$pg = $doc.GetPage($Page)
$opts = New-Object Windows.Data.Pdf.PdfPageRenderOptions
$opts.DestinationWidth = [uint32]($pg.Size.Width * $Scale)
$opts.DestinationHeight = [uint32]($pg.Size.Height * $Scale)
$opts.BackgroundColor = [Windows.UI.Color]::FromArgb(255, 255, 255, 255)
$stream = New-Object Windows.Storage.Streams.InMemoryRandomAccessStream
AwaitAction ($pg.RenderToStreamAsync($stream, $opts))
$reader = New-Object Windows.Storage.Streams.DataReader($stream.GetInputStreamAt(0))
$size = [uint32]$stream.Size
$null = Await ($reader.LoadAsync($size)) ([uint32])
$bytes = New-Object byte[] $size
$reader.ReadBytes($bytes)
[System.IO.File]::WriteAllBytes($Out, $bytes)
Write-Output "$Out $($opts.DestinationWidth)x$($opts.DestinationHeight)"
