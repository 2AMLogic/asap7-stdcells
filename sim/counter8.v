// 8-bit synchronous up-counter with enable and synchronous clear
// (spec/stdcells.md "Integration design"). Clear wins over enable.
module counter8 (
    input  wire       clk,
    input  wire       clr,
    input  wire       en,
    output reg  [7:0] q
);
    always @(posedge clk)
        if (clr)     q <= 8'd0;
        else if (en) q <= q + 8'd1;
endmodule
