// Lock-step comparison of the RTL counter8 against the mapped netlist
// counter8_mapped over a fixed stimulus; prints PASS/FAIL and the cycle count.
`timescale 1ns/1ps
module counter8_tb;
    reg clk = 0, clr = 1, en = 0;
    wire [7:0] q_rtl, q_map;
    counter8        rtl (.clk(clk), .clr(clr), .en(en), .q(q_rtl));
    counter8_mapped map (.clk(clk), .clr(clr), .en(en), .q(q_map));
    integer i, bad = 0;
    reg [31:0] lfsr = 32'hACE1_2468;
    always #5 clk = ~clk;
    initial begin
        // a first clear cycle puts both into a known state
        repeat (2) @(negedge clk);
        for (i = 0; i < 1500; i = i + 1) begin
            lfsr = {lfsr[30:0], lfsr[31] ^ lfsr[21] ^ lfsr[1] ^ lfsr[0]};
            clr = (i < 2) || (lfsr[7:0] == 8'd3);       // rare clears
            en  = (i < 600) ? 1'b1 : lfsr[9];           // long enabled run: wraps 255 -> 0
            @(negedge clk);
            if (q_rtl !== q_map) begin
                bad = bad + 1;
                if (bad < 5) $display("MISMATCH cycle %0d: rtl=%h mapped=%h", i, q_rtl, q_map);
            end
        end
        if (bad == 0) $display("SIM PASS: 1500 cycles, mapped netlist equals RTL");
        else          $display("SIM FAIL: %0d mismatching cycles", bad);
        $finish;
    end
endmodule
