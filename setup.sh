#!/bin/bash

cp run.py run
sudo chmod +x run

cp run_warnings.py run_warnings
sudo chmod +x run_warnings

dos2unix run
dos2unix run_warnings