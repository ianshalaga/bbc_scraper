@echo off
for %%a in (%*) do ("%~dp0"\realesrgan-ncnn-vulkan.exe -i "%~1" -o "%~dp1\%~n1.jpg" -n realesrgan-x4plus
@REM "%~dp1\%~n1_4x.png" preview
)
exit