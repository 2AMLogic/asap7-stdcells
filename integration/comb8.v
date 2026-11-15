// Flop-free control design for the P&R flow (integration/flowctl_par.sh).
//
// Not a deliverable and not the integration design -- spec/stdcells.md's
// integration design is sim/counter8.v. This exists for one purpose: to route
// a design through integration/par_counter8.tcl that avoids the cells whose
// pins OpenROAD's detailed router cannot reach (integration/README.md), so
// that a refusal on counter8 can be attributed to those cells rather than to
// the flow. An 8-bit ripple-carry adder: combinational, no clock, no flop.
module comb8(a, b, cin, s, cout);
  input  [7:0] a, b;
  input        cin;
  output [7:0] s;
  output       cout;
  wire   [8:0] c;
  assign c[0] = cin;
  genvar i;
  generate for (i = 0; i < 8; i = i + 1) begin : bit
    assign s[i]   = a[i] ^ b[i] ^ c[i];
    assign c[i+1] = (a[i] & b[i]) | (c[i] & (a[i] ^ b[i]));
  end endgenerate
  assign cout = c[8];
endmodule
