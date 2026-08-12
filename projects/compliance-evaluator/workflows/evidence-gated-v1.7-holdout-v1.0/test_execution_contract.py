#!/usr/bin/env python3
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).resolve().parent.parent/'evidence-gated-v1.4'/'test_execution_contract.py'),run_name='__main__')
