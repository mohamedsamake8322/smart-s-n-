@echo off
setlocal enabledelayedexpansion

set "LOCAL_FOLDER=C:\Downloads\CMS_Global_Map_Mangrove_Canopy_1665_1.3-20250722_112323-20250725T131545Z-1-001"
set "BUCKET=gs://plant-ai-dataset-mohamed-20100116"

echo 🌍 Starting upload...

for %%F in ("%LOCAL_FOLDER%\*.tif") do (
    echo 📤 Uploading: %%~nxF
    gsutil cp "%%F" "%BUCKET%/"
)

echo ✅ All done!
pause
