# Hải Đồ IT - cào tin IT định kỳ (ITviec, TopDev, API ATS, Cốc Cốc) vào data/scraped/*.jsonl
# Mỗi lần chạy chỉ tải tin chưa cào (state lưu cạnh JSONL), nên chạy hằng ngày để tích luỹ dần.
# Lên lịch hằng ngày lúc 02:00 bằng Task Scheduler (chạy một lần, từ thư mục gốc repo):
#   schtasks /Create /TN "HaiDoIT Scrapers" /SC DAILY /ST 02:00 `
#     /TR "powershell -NoProfile -ExecutionPolicy Bypass -File \"$PWD\scraper\run_scrapers.ps1\"" /F
param (
    [int]$Limit = 1000,
    [string]$Contact = $env:SCRAPER_CONTACT
)

$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

$PythonExe = "python"
if (Test-Path ".venv\Scripts\python.exe") {
    $PythonExe = ".venv\Scripts\python.exe"
}

New-Item -ItemType Directory -Force "data\scraped" | Out-Null
$Stamp = Get-Date -Format 'yyyyMMdd-HHmm'
$Log = "data\scraped\run-$Stamp.log"        # tóm tắt (stdout)
$ErrLog = "data\scraped\run-$Stamp.err.log" # log chi tiết + lỗi (stderr)
$ScraperArgs = "-m scraper.jobboards --source all --limit $Limit"
if ($Contact) {
    $ScraperArgs += " --contact `"$Contact`""
}

Write-Host "Cào mọi nguồn (tối đa $Limit trang/nguồn) -> $Log" -ForegroundColor Cyan
$Proc = Start-Process -FilePath $PythonExe -ArgumentList $ScraperArgs -Wait -PassThru -NoNewWindow `
    -RedirectStandardOutput $Log -RedirectStandardError $ErrLog
$Code = $Proc.ExitCode
Get-Content $Log, $ErrLog -Encoding UTF8 | Select-String -Pattern "^(===|  [a-z_]+ +:|DỪNG|LỖI)"
switch ($Code) {
    0 { Write-Host "Xong." -ForegroundColor Green }
    3 { Write-Host "Có nguồn chặn bot - đã dừng nguồn đó, không vượt chặn." -ForegroundColor Yellow }
    default { Write-Host "Lỗi (mã $Code), xem $ErrLog" -ForegroundColor Red }
}
exit $Code
