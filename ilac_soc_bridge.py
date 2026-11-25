from pathlib import Path
import re
import subprocess
import tempfile


PROJECT_DIR = Path(__file__).resolve().parent

CLASSIFICATIONS = {
    0: "WEAK",
    1: "AVERAGE",
    2: "GOOD",
    3: "INVALID",
}


def run_ilac_soc(answer_flags):
    """
    Send quiz answers through the AXI4-Lite interface to the
    ILAC Verilog SoC, simulate it, and return the hardware result.

    True  = correct answer
    False = incorrect answer
    """

    answers = [bool(answer) for answer in answer_flags]

    if not answers:
        raise ValueError("No quiz answers were provided.")

    if len(answers) > 255:
        raise ValueError("The ILAC SoC supports up to 255 answers per run.")

    design_file = PROJECT_DIR / "design.sv"

    if not design_file.exists():
        raise FileNotFoundError("design.sv was not found in the project folder.")

    transactions = "\n".join(
        f"        axi_write(4'h4, 32'd{1 if answer else 0});"
        for answer in answers
    )

    testbench = f"""
module ilac_runtime_tb;

    reg ACLK;
    reg ARESETN;

    reg [3:0] AWADDR;
    reg AWVALID;
    wire AWREADY;

    reg [31:0] WDATA;
    reg [3:0] WSTRB;
    reg WVALID;
    wire WREADY;

    wire [1:0] BRESP;
    wire BVALID;
    reg BREADY;

    reg [3:0] ARADDR;
    reg ARVALID;
    wire ARREADY;

    wire [31:0] RDATA;
    wire [1:0] RRESP;
    wire RVALID;
    reg RREADY;

    reg [31:0] read_data;
    reg [31:0] class_data;

    ilac_soc_top dut (
        .ACLK(ACLK),
        .ARESETN(ARESETN),
        .AWADDR(AWADDR),
        .AWVALID(AWVALID),
        .AWREADY(AWREADY),
        .WDATA(WDATA),
        .WSTRB(WSTRB),
        .WVALID(WVALID),
        .WREADY(WREADY),
        .BRESP(BRESP),
        .BVALID(BVALID),
        .BREADY(BREADY),
        .ARADDR(ARADDR),
        .ARVALID(ARVALID),
        .ARREADY(ARREADY),
        .RDATA(RDATA),
        .RRESP(RRESP),
        .RVALID(RVALID),
        .RREADY(RREADY)
    );

    always #5 ACLK = ~ACLK;

    task axi_write;
        input [3:0] address;
        input [31:0] data;
        reg aw_done;
        reg w_done;
        begin
            aw_done = 0;
            w_done = 0;

            @(negedge ACLK);
            AWADDR = address;
            WDATA = data;
            AWVALID = 1;
            WVALID = 1;

            while (!(aw_done && w_done)) begin
                @(posedge ACLK);
                if (AWREADY)
                    aw_done = 1;
                if (WREADY)
                    w_done = 1;
            end

            @(negedge ACLK);
            AWVALID = 0;
            WVALID = 0;

            wait (BVALID == 1);
            @(negedge ACLK);
            BREADY = 1;

            @(negedge ACLK);
            BREADY = 0;
        end
    endtask

    task axi_read;
        input [3:0] address;
        output [31:0] data;
        begin
            @(negedge ACLK);
            ARADDR = address;
            ARVALID = 1;

            do begin
                @(posedge ACLK);
            end while (ARREADY !== 1'b1);

            @(negedge ACLK);
            ARVALID = 0;

            wait (RVALID == 1);
            data = RDATA;

            @(negedge ACLK);
            RREADY = 1;

            @(negedge ACLK);
            RREADY = 0;
        end
    endtask

    initial begin
        ACLK = 0;
        ARESETN = 0;

        AWADDR = 0;
        AWVALID = 0;
        WDATA = 0;
        WSTRB = 4'b1111;
        WVALID = 0;
        BREADY = 0;

        ARADDR = 0;
        ARVALID = 0;
        RREADY = 0;

        read_data = 0;
        class_data = 0;

        repeat (4) @(negedge ACLK);
        ARESETN = 1;

        // Reset the ILAC accelerator through AXI4-Lite.
        axi_write(4'h0, 32'd1);

        // Submit every quiz answer through AXI4-Lite.
{transactions}

        // Read the SoC result and classification registers.
        axi_read(4'h8, read_data);
        axi_read(4'hC, class_data);

        $display(
            "ILAC_RESULT correct=%0d total=%0d classification=%0d",
            read_data[7:0],
            read_data[15:8],
            class_data[1:0]
        );

        $finish;
    end

    initial begin
        #100000;
        $display("ERROR: ILAC simulation timed out.");
        $finish;
    end

endmodule
"""

    with tempfile.TemporaryDirectory(prefix="ilac_soc_") as temp_dir:
        temp_path = Path(temp_dir)
        tb_file = temp_path / "ilac_runtime_tb.sv"
        output_file = temp_path / "ilac_runtime.vvp"

        tb_file.write_text(testbench, encoding="utf-8")

        compile_result = subprocess.run(
            [
                "iverilog",
                "-g2012",
                "-s",
                "ilac_runtime_tb",
                "-o",
                str(output_file),
                str(design_file),
                str(tb_file),
            ],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )

        if compile_result.returncode != 0:
            raise RuntimeError(
                "ILAC Verilog compilation failed:\n"
                + compile_result.stdout
                + compile_result.stderr
            )

        simulation_result = subprocess.run(
            ["vvp", str(output_file)],
            cwd=PROJECT_DIR,
            capture_output=True,
            text=True,
            timeout=30,
        )

        simulation_output = (
            simulation_result.stdout + simulation_result.stderr
        )

        if simulation_result.returncode != 0:
            raise RuntimeError(
                "ILAC simulation failed:\n" + simulation_output
            )

        match = re.search(
            r"ILAC_RESULT\s+correct=(\d+)\s+total=(\d+)\s+classification=(\d+)",
            simulation_output,
        )

        if not match:
            raise RuntimeError(
                "Could not read the ILAC SoC result.\n"
                + simulation_output
            )

        correct = int(match.group(1))
        total = int(match.group(2))
        classification_code = int(match.group(3))

        if total != len(answers):
            raise RuntimeError(
                f"SoC reported {total} answers, but {len(answers)} were submitted."
            )

        return {
            "correct": correct,
            "total": total,
            "classification_code": classification_code,
            "classification": CLASSIFICATIONS.get(
                classification_code, "UNKNOWN"
            ),
            "simulation_output": simulation_output,
        }
