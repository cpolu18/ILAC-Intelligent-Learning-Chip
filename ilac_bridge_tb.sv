
`timescale 1ns/1ps

module ilac_bridge_tb;

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

    reg [31:0] performance_result;
    reg [31:0] classification_result;

    integer i;

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

    // AXI WRITE TASK
    task axi_write;
        input [3:0] address;
        input [31:0] data;
        begin
            $display("AXI WRITE START: Address=0x%0h Data=0x%08h",
                     address, data);

            @(negedge ACLK);
            AWADDR = address;
            WDATA = data;
            WSTRB = 4'b0001;
            AWVALID = 1;
            WVALID = 1;

            do begin
                @(posedge ACLK);
            end while (!(AWREADY && WREADY));

            $display("AWREADY and WREADY received");

            @(negedge ACLK);
            AWVALID = 0;
            WVALID = 0;

            wait (BVALID == 1);

            $display("BVALID received, BRESP=%0d", BRESP);

            @(negedge ACLK);
            wait (BVALID == 0);

            $display("AXI WRITE COMPLETED");
            $display("--------------------------------");
        end
    endtask

    // AXI READ TASK
    task axi_read;
        input [3:0] address;
        output [31:0] data;
        begin
            $display("AXI READ START: Address=0x%0h", address);

            @(negedge ACLK);
            ARADDR = address;
            ARVALID = 1;

            do begin
                @(posedge ACLK);
            end while (ARREADY !== 1);

            $display("ARREADY received");

            @(negedge ACLK);
            ARVALID = 0;

            wait (RVALID == 1);

            data = RDATA;

            $display("RVALID received");
            $display("Read Data = 0x%08h", data);
            $display("RRESP = %0d", RRESP);

            @(negedge ACLK);
            wait (RVALID == 0);

            $display("AXI READ COMPLETED");
            $display("--------------------------------");
        end
    endtask

    // MAIN TESTBENCH
    initial begin

        $dumpfile("ilac_soc_waveform.vcd");
        $dumpvars(0, ilac_bridge_tb);

        ACLK = 0;
        ARESETN = 0;

        AWADDR = 0;
        AWVALID = 0;
        WDATA = 0;
        WSTRB = 0;
        WVALID = 0;
        BREADY = 1;

        ARADDR = 0;
        ARVALID = 0;
        RREADY = 1;

        performance_result = 0;
        classification_result = 0;

        $display("================================");
        $display("ILAC AXI4-LITE SOC TEST STARTED");
        $display("================================");

        repeat (4) @(negedge ACLK);

        ARESETN = 1;

        $display("SOC RESET RELEASED");
        $display("--------------------------------");

        // RESET REGISTER
        axi_write(4'h0, 32'h00000001);

        // SEND 10 QUIZ ANSWERS
        for (i = 0; i < 10; i = i + 1) begin

            if (i < 8) begin
                $display("Question %0d: CORRECT", i + 1);
                axi_write(4'h4, 32'h00000001);
            end
            else begin
                $display("Question %0d: INCORRECT", i + 1);
                axi_write(4'h4, 32'h00000000);
            end

        end

        // READ PERFORMANCE COUNTERS
        axi_read(4'h8, performance_result);

        // READ CLASSIFICATION
        axi_read(4'hC, classification_result);

        // FINAL RESULTS
        $display("================================");
        $display("ILAC SOC FINAL RESULTS");
        $display("================================");

        $display("Correct Answers      : %0d",
                 performance_result[7:0]);

        $display("Total Answers        : %0d",
                 performance_result[15:8]);

        $display("Classification Code  : %0d",
                 classification_result[1:0]);

        if (classification_result[1:0] == 0)
            $display("Classification       : WEAK");
        else if (classification_result[1:0] == 1)
            $display("Classification       : AVERAGE");
        else if (classification_result[1:0] == 2)
            $display("Classification       : GOOD");
        else
            $display("Classification       : INVALID");

        $display("--------------------------------");

        if (performance_result[7:0] == 8 &&
            performance_result[15:8] == 10 &&
            classification_result[1:0] == 2)

            $display("PASS: ILAC AXI SOC BRIDGE TEST");

        else

            $display("FAIL: ILAC AXI SOC BRIDGE TEST");

        $display("================================");

        $finish;

    end

endmodule
