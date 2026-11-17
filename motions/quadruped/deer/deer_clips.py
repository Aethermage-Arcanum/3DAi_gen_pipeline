"""Bewegungsmuster quadruped/deer: nutzt den Vierbeiner-Generator ../wolf/wolf_clips.py mit eigener style.toml.

& "D:\Blender\blender.exe" -b <quadruped_rigged.blend> -P motions/quadruped/deer/deer_clips.py -- <ausgabe> [<creature.toml>]
"""
import pathlib
import runpy

HERE = pathlib.Path(__file__).resolve().parent
runpy.run_path(str(HERE.parent / "wolf" / "wolf_clips.py"), init_globals={"STYLE_DIR": HERE}, run_name="__main__")
