@echo off
rem Startet Blender mit dem Varianten-Panel (Reiter "Variante" in der Seitenleiste, Taste N).
rem Blender-Pfad bei Bedarf anpassen.
set BLENDER=D:\Blender\blender.exe
start "" "%BLENDER%" --python "%~dp0vk_start.py" -- %*
