"""ANSI colour constants and helpers."""

import re

C_OK    = "\033[92m"
C_FAIL  = "\033[91m"
C_WARN  = "\033[93m"
C_CYAN  = "\033[96m"
C_DIM   = "\033[2m"
C_BOLD  = "\033[1m"
C_RESET = "\033[0m"

def col(c, s):
    return f"{c}{s}{C_RESET}"

_ANSI_RE = re.compile(r'\033\[[0-9;]*m')

def _strip_ansi(text):
    return _ANSI_RE.sub('', text)
