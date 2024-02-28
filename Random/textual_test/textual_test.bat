@echo off

call conda activate Lucid

python textual_test.py
@echo off

call conda deactivate
