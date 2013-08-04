#!/usr/bin/env python
import sys
import os

HERE = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(HERE, ".."))

from django.core.management import execute_from_command_line

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "baculaUI.settings")

if __name__ == "__main__":
    execute_from_command_line(sys.argv)
