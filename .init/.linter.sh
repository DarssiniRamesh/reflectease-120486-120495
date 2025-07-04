#!/bin/bash
cd /home/kavia/workspace/code-generation/reflectease-120486-120495/daily_journal_backend
source venv/bin/activate
flake8 .
LINT_EXIT_CODE=$?
if [ $LINT_EXIT_CODE -ne 0 ]; then
  exit 1
fi

