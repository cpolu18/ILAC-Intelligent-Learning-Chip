`timescale 1ns/1ps

module ilac_classification_tb;

reg ACLK = 0;
reg ARESETN = 0;
reg [3:0] AWADDR, ARADDR;
reg AWVALID, WVALID, BREADY, ARVALID, RREADY;
reg [31:0] WDATA;
reg [3:0] WSTRB;
wire AWREADY, WREADY, BVALID, ARREADY, RVALID;
wire [1:0] BRESP, RRESP;
wire [31:0] RDATA;

integer i, test_num, correct_count, total_count;
reg [1:0] expected_class;
reg [31:0] performance_result, classification_result;

always #5 ACLK = ~ACLK;

ilac_soc_top dut (
    .ACLK(ACLK), .ARESETN(ARESETN),
    .AWADDR(AWADDR), .AWVALID(AWVALID), .AWREADY(AWREADY),
    .WDATA(WDATA), .WSTRB(WSTRB), .WVALID(WVALID), .WREADY(WREADY),
    .BRESP(BRESP), .BVALID(BVALID), .BREADY(BREADY),
    .ARADDR(ARADDR), .ARVALID(ARVALID), .ARREADY(ARREADY),
    .RDATA(RDATA), .RRESP(RRESP), .RVALID(RVALID), .RREADY(RREADY)
);

task axi_write(input [3:0] address, input [31:0] data);
begin
    @(negedge ACLK);
    AWADDR = address; WDATA = data;
    AWVALID = 1; WVALID = 1; BREADY = 1;
    wait(AWREADY && WREADY);
    @(negedge ACLK);
    AWVALID = 0; WVALID = 0;
    wait(BVALID);
    @(negedge ACLK);
    BREADY = 0;
end
endtask

task axi_read(input [3:0] address, output [31:0] data);
begin
    @(negedge ACLK);
    ARADDR = address; ARVALID = 1; RREADY = 1;
    wait(ARREADY);
    @(negedge ACLK);
    ARVALID = 0;
    wait(RVALID);
    data = RDATA;
    @(negedge ACLK);
    RREADY = 0;
end
endtask

task run_test(
    input integer number,
    input integer correct,
    input integer total,
    input [1:0] expected
);
begin
    test_num = number;
    correct_count = correct;
    total_count = total;
    expected_class = expected;

    ARESETN = 0;
    repeat(3) @(negedge ACLK);
    ARESETN = 1;
    axi_write(4'h0, 32'h1);

    for (i = 0; i < total_count; i = i + 1)
        axi_write(4'h4, (i < correct_count) ? 32'h1 : 32'h0);

    axi_read(4'h8, performance_result);
    axi_read(4'hC, classification_result);

    $display("--------------------------------");
    $display("TEST %0d: Correct=%0d Total=%0d",
             test_num, performance_result[7:0],
             performance_result[15:8]);

    case(classification_result[1:0])
        0: $display("Classification: WEAK");
        1: $display("Classification: AVERAGE");
        2: $display("Classification: GOOD");
        3: $display("Classification: INVALID");
    endcase

    if (performance_result[7:0] == correct_count &&
        performance_result[15:8] == total_count &&
        classification_result[1:0] == expected_class)
        $display("PASS");
    else
        $display("FAIL");
end
endtask

initial begin
    AWADDR=0; AWVALID=0; WDATA=0; WSTRB=4'hF;
    WVALID=0; BREADY=0; ARADDR=0; ARVALID=0; RREADY=0;

    $dumpfile("ilac_classification_waveform.vcd");
    $dumpvars(0, ilac_classification_tb);

    $display("ILAC FOUR-CLASSIFICATION TESTS");

    run_test(1, 0, 0, 3);
    run_test(2, 2, 10, 0);
    run_test(3, 5, 10, 1);
    run_test(4, 8, 10, 2);

    $display("--------------------------------");
    $display("ALL FOUR CLASSIFICATION TESTS COMPLETED");
    $finish;
end

endmodule
