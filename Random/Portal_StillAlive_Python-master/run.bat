@echo off

call conda activate Lucid

python still_alive_credit.py--no-sound
@echo off

REM Activate the conda environment
call conda activate Lucid

REM Run the Python file
python still_alive_credit.py --no-sound

REM Deactivate the conda environment
call conda deactivate