# ILAC – Intelligent Learning Assistant Chip

## Overview
ILAC combines a Streamlit quiz application, machine learning prediction, and a Verilog-based System-on-Chip (SoC).

## Features
- Interactive student quiz platform.
- Machine learning performance prediction.
- Verilog quiz processor and performance classifier.
- AXI4-Lite communication.
- Python-to-RTL simulation bridge.
- Local CSV result storage.

## Technologies
- Python, Streamlit
- Verilog HDL
- Icarus Verilog
- Yosys
- Machine Learning
- GitHub Codespaces

## Hardware Modules
- ilac_quiz_processor
- ilac_performance_classifier
- ilac_top
- ilac_axi_lite
- ilac_soc_top

## Classification Verification

| Correct | Total | Classification | Result |
|---:|---:|---|---|
| 0 | 0 | INVALID | PASS |
| 2 | 10 | WEAK | PASS |
| 5 | 10 | AVERAGE | PASS |
| 8 | 10 | GOOD | PASS |

## Synthesis Results
- Total generic logic cells: 583
- Sequential cells: 45
- Combinational cells: 538

## Run the Project

Install dependencies:

    pip install -r requirements.txt

Install simulation tools:

    sudo apt-get update
    sudo apt-get install -y iverilog yosys

Run the website:

    streamlit run app.py

## Evidence
The ILAC_SoC_Evidence folder contains simulation waveforms, AXI transaction logs, classification test results, and the Yosys synthesis report.

## Implementation Note
The SoC was verified through RTL simulation and generic logic synthesis. No physical FPGA implementation or hardware deployment has been performed.

## System Architecture

```mermaid
flowchart TD
    A["Student"] --> B["Streamlit Quiz Application"]
    B --> C["Quiz Evaluation"]
    C --> D["Local CSV Storage"]
    C --> E["Machine Learning Model"]
    E --> F["ML Performance Prediction"]
    C --> G["Python–SoC Bridge"]
    G --> H["Icarus Verilog Simulator"]
    H --> I["AXI4-Lite Interface"]
    I --> J["ILAC Verilog SoC"]
    J --> K["Quiz Processor"]
    K --> L["Performance Counters"]
    L --> M["Performance Classifier"]
    M --> N["INVALID / WEAK / AVERAGE / GOOD"]
    N --> I
    I --> G
    G --> B
    F --> O["Final Results Dashboard"]
    B --> O
git add README.md
git commit -m "Add ILAC system architecture diagram"
git push origin main
