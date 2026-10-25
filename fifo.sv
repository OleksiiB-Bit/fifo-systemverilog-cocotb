module fifo#(
	parameter int DATA_WIDTH = 8,
	parameter int DEPTH = 16
)(
	input logic clk,
	input logic reset,
	input logic wr_en,
	input logic [DATA_WIDTH -1:0] din,
	input logic rd_en,
	output logic [DATA_WIDTH-1:0] dout,
	output logic full,
	output logic empty
);

logic [DATA_WIDTH-1:0] mem [0:DEPTH-1];
logic [$clog2(DEPTH)+1:0] count;
logic [$clog2(DEPTH)-1:0] write_path;
logic [$clog2(DEPTH)-1:0] read_path;


always_ff @(posedge clk or posedge reset) begin
	if (reset) begin
		count <= '0;
		write_path <= '0;
		read_path <= '0;
	end else begin
		if (wr_en && rd_en) begin
			mem[write_path] <= din;
			write_path <= (write_path==DEPTH-1) ? '0 : write_path + 1'b1;
			read_path <= (read_path==DEPTH-1) ? '0 : read_path + 1'b1;
		end else if (wr_en && ~full) begin
			mem[write_path] <= din;
			count <= count + 1'b1;
			write_path <= (write_path==DEPTH-1) ? '0 : write_path + 1;
		end else if (rd_en && ~empty) begin
			read_path <= (read_path==DEPTH-1) ? '0 : read_path+1'b1;
			count <= count - 1'b1;
		end
	end
end

	assign dout  = mem[read_path];
	assign empty = (count == 0);
	assign full  = (count == DEPTH);

endmodule
