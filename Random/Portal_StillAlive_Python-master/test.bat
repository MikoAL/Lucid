@echo off

call conda activate Lucid

python test.py
@echo off

call conda deactivate
