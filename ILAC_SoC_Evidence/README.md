# ILAC – Intelligent Learning Assistant Chip
## SoC Simulation and Synthesis Evidence

### Project Overview
ILAC is an Intelligent Learning Assistant implemented as a Verilog RTL System-on-Chip (SoC).

The system processes quiz answer data through an AXI4-Lite interface and classifies student performance.

### SoC Architecture
1. Quiz Processor
2. Performance Classifier
3. ILAC Top Module
4. AXI4-Lite Interface
5. ILAC SoC Top Module

### Verification Results
- Correct Answers: 8
- Total Answers: 10
- Classification: GOOD
- Classification Code: 2
- AXI4-Lite Test: PASS

### Evidence Files
- ilac_synthesis_report.txt – Yosys generic RTL synthesis report.
- ilac_soc_waveform.vcd – RTL simulation waveform.
- ilac_axi_transaction_log.txt – AXI4-Lite read/write transaction log.

### Tools Used
- Verilog HDL
- Icarus Verilog
- Yosys
- Python
- Streamlit
- GitHub Codespaces

### Implementation Note
The SoC is verified through RTL simulation and generic logic synthesis.
No physical FPGA implementation or hardware deployment has been performed.
