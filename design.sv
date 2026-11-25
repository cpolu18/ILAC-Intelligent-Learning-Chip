
`timescale 1ns/1ps

// ============================================
// 1. ILAC QUIZ PROCESSOR
// ============================================

module ilac_quiz_processor (
    input wire clk,
    input wire reset,
    input wire answer_valid,
    input wire answer_correct,
    output reg [7:0] correct_count,
    output reg [7:0] total_count
);

    always @(posedge clk) begin
        if (reset) begin
            correct_count <= 0;
            total_count <= 0;
        end
        else if (answer_valid && total_count < 255) begin
            total_count <= total_count + 1'b1;

            if (answer_correct && correct_count < 255)
                correct_count <= correct_count + 1'b1;
        end
    end

endmodule


// ============================================
// 2. PERFORMANCE CLASSIFIER
// ============================================

module ilac_performance_classifier (
    input wire [7:0] correct_count,
    input wire [7:0] total_count,
    output reg [1:0] classification
);

    wire [15:0] correct_scaled;
    wire [15:0] total_40;
    wire [15:0] total_70;

    assign correct_scaled = correct_count * 16'd100;
    assign total_40 = total_count * 16'd40;
    assign total_70 = total_count * 16'd70;

    always @(*) begin
        if (total_count == 0 || correct_count > total_count)
            classification = 2'b11;
        else if (correct_scaled < total_40)
            classification = 2'b00;
        else if (correct_scaled < total_70)
            classification = 2'b01;
        else
            classification = 2'b10;
    end

endmodule


// ============================================
// 3. ILAC TOP
// ============================================

module ilac_top (
    input wire clk,
    input wire reset,
    input wire answer_valid,
    input wire answer_correct,
    output wire [7:0] correct_count,
    output wire [7:0] total_count,
    output wire [1:0] classification
);

    ilac_quiz_processor processor (
        .clk(clk),
        .reset(reset),
        .answer_valid(answer_valid),
        .answer_correct(answer_correct),
        .correct_count(correct_count),
        .total_count(total_count)
    );

    ilac_performance_classifier classifier (
        .correct_count(correct_count),
        .total_count(total_count),
        .classification(classification)
    );

endmodule


// ============================================
// 4. AXI4-LITE SLAVE
// ============================================

module ilac_axi_lite (
    input wire ACLK,
    input wire ARESETN,

    input wire [3:0] AWADDR,
    input wire AWVALID,
    output wire AWREADY,

    input wire [31:0] WDATA,
    input wire [3:0] WSTRB,
    input wire WVALID,
    output wire WREADY,

    output reg [1:0] BRESP,
    output reg BVALID,
    input wire BREADY,

    input wire [3:0] ARADDR,
    input wire ARVALID,
    output wire ARREADY,

    output reg [31:0] RDATA,
    output reg [1:0] RRESP,
    output reg RVALID,
    input wire RREADY
);

    reg [3:0] saved_write_address;
    reg [31:0] saved_write_data;
    reg [3:0] saved_write_strb;

    reg write_address_saved;
    reg write_data_saved;

    reg answer_valid;
    reg answer_correct;
    reg accelerator_reset;

    wire [7:0] correct_count;
    wire [7:0] total_count;
    wire [1:0] classification;

    wire aw_fire;
    wire w_fire;

    wire [3:0] active_write_address;
    wire [31:0] active_write_data;
    wire [3:0] active_write_strb;

    assign AWREADY = ARESETN &&
                     !write_address_saved &&
                     !BVALID;

    assign WREADY = ARESETN &&
                    !write_data_saved &&
                    !BVALID;

    assign ARREADY = ARESETN && !RVALID;

    assign aw_fire = AWVALID && AWREADY;
    assign w_fire = WVALID && WREADY;

    assign active_write_address =
        write_address_saved ?
        saved_write_address : AWADDR;

    assign active_write_data =
        write_data_saved ?
        saved_write_data : WDATA;

    assign active_write_strb =
        write_data_saved ?
        saved_write_strb : WSTRB;

    ilac_top accelerator (
        .clk(ACLK),
        .reset(accelerator_reset),
        .answer_valid(answer_valid),
        .answer_correct(answer_correct),
        .correct_count(correct_count),
        .total_count(total_count),
        .classification(classification)
    );

    always @(posedge ACLK) begin

        if (!ARESETN) begin

            saved_write_address <= 0;
            saved_write_data <= 0;
            saved_write_strb <= 0;

            write_address_saved <= 0;
            write_data_saved <= 0;

            BVALID <= 0;
            BRESP <= 0;

            RVALID <= 0;
            RDATA <= 0;
            RRESP <= 0;

            answer_valid <= 0;
            answer_correct <= 0;
            accelerator_reset <= 0;

        end

        else begin

            answer_valid <= 0;
            accelerator_reset <= 0;

            // Capture write address
            if (aw_fire) begin
                saved_write_address <= AWADDR;
                write_address_saved <= 1;
            end

            // Capture write data
            if (w_fire) begin
                saved_write_data <= WDATA;
                saved_write_strb <= WSTRB;
                write_data_saved <= 1;
            end

            // Execute when both channels are received
            if (!BVALID &&
                (write_address_saved || aw_fire) &&
                (write_data_saved || w_fire)) begin

                case (active_write_address)

                    4'h0: begin
                        if (active_write_strb[0] &&
                            active_write_data[0])
                            accelerator_reset <= 1;
                    end

                    4'h4: begin
                        if (active_write_strb[0]) begin
                            answer_valid <= 1;
                            answer_correct <= active_write_data[0];
                        end
                    end

                    default: begin
                    end

                endcase

                write_address_saved <= 0;
                write_data_saved <= 0;

                BVALID <= 1;
                BRESP <= 2'b00;

            end

            // Write response
            if (BVALID && BREADY)
                BVALID <= 0;

            // Read address and data
            if (ARVALID && ARREADY && !RVALID) begin

                case (ARADDR)

                    4'h0:
                        RDATA <= 32'h00000000;

                    4'h4:
                        RDATA <= {31'b0, answer_correct};

                    4'h8:
                        RDATA <= {
                            16'b0,
                            total_count,
                            correct_count
                        };

                    4'hC:
                        RDATA <= {
                            30'b0,
                            classification
                        };

                    default:
                        RDATA <= 32'h00000000;

                endcase

                RRESP <= 2'b00;
                RVALID <= 1;

            end

            // Read response
            if (RVALID && RREADY)
                RVALID <= 0;

        end

    end

endmodule


// ============================================
// 5. ILAC SOC TOP
// ============================================

module ilac_soc_top (

    input wire ACLK,
    input wire ARESETN,

    input wire [3:0] AWADDR,
    input wire AWVALID,
    output wire AWREADY,

    input wire [31:0] WDATA,
    input wire [3:0] WSTRB,
    input wire WVALID,
    output wire WREADY,

    output wire [1:0] BRESP,
    output wire BVALID,
    input wire BREADY,

    input wire [3:0] ARADDR,
    input wire ARVALID,
    output wire ARREADY,

    output wire [31:0] RDATA,
    output wire [1:0] RRESP,
    output wire RVALID,
    input wire RREADY

);

    ilac_axi_lite ilac_accelerator (

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

endmodule
