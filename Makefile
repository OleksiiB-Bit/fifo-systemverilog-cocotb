TOPLEVEL_LANG = verilog
VERILOG_SOURCES = fifo.sv
TOPLEVEL = fifo
MODULE = test_fifo

COCOTB_MAKEFILES = $(shell python3 -m cocotb_tools.config --makefiles)
include $(COCOTB_MAKEFILES)/Makefile.sim
