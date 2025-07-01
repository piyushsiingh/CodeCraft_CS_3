import re
import sys
import time
import string
from enum import Enum, auto
from threading import Thread
from getpass import getpass

class StrengthLevel(Enum):
    VERY_WEAK = auto()
    WEAK = auto()
    MODERATE = auto()
    STRONG = auto()
    VERY_STRONG = auto()

# (Truncated for brevity – full script included below)
# You can paste the full code here if needed

if __name__ == "__main__":
    checker = PasswordAssessor()
    checker.run_assessment_loop()
