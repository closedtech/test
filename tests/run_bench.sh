#!/bin/bash
cd /home/user/.openclaw/workspace
python3 test_bigint.py > bench_results.txt 2>&1
echo "Done" >> bench_results.txt
