#!/usr/bin/env bash
# The --high-mem CPU runtime's unit rate (R&D: above 0.5/hr, stop and tell). One session, read `colab usage`, stop.
set -uo pipefail
echo "before: $(colab usage 2>&1 | grep -E 'rate|balance' | tr '\n' ' ')"
timeout 300 colab new --high-mem -s hmprobe 2>&1 | tail -1
sleep 15
echo "open:   $(colab usage 2>&1 | grep -E 'rate|assign' | tr '\n' ' ')"
colab stop -s hmprobe 2>&1 | tail -1
sleep 5; echo "after:  $(colab usage 2>&1 | grep -E 'rate' | tr '\n' ' ')"; colab sessions 2>&1 | tail -2
