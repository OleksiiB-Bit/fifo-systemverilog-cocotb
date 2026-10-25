
# Synchronous FIFO Memory with Cocotb Verification Suite

A fully synchronous FIFO (First-In, First-Out) memory module designed in **SystemVerilog (IEEE 1800-2012)** and verified using an event-driven Python testbench with **Cocotb** and **Icarus Verilog**.

## Key Specification & Features

The module implements a circular ring buffer architecture with combinatorial output logic for zero-latency read capability.

* **Parameters**:
  * `DATA_WIDTH`: Width of input/output data buses (Default: 8 bits).
  * `DEPTH`: Depth of the RAM buffer (Default: 16 entries).
* **Control Flags**:
  * `full`: High when the buffer reaches maximum capacity (`count == DEPTH`).
  * `empty`: High when the buffer is empty (`count == 0`).
* **Zero Read Latency**: Outputs data directly via `assign dout = mem[read_path]` to allow instantaneous access without an extra clock cycle delay.

## Module Topography
```
                  +-----------------------+
        clk ----->|                       |
      reset ----->|                       |-----> dout [7:0]
      wr_en ----->|   Synchronous FIFO    |-----> full
  din [7:0] ----->|   (8-bit x 16-deep)   |-----> empty
      rd_en ----->|                       |
                  +-----------------------+
```
## Verification Environment (test_fifo.py)
Automated regression suite implemented in Python using Cocotb:

* test_fifo_antiparallel: Verifies sequential write operations up to full == 1, followed by sequential reads down to empty == 1.

* test_fifo_parallel: Tests concurrent write and read transactions (Full Duplex) while maintaining internal buffer stability.

* test_fifo_wraparound: Stress tests ring buffer pointer roll-over across boundaries (DEPTH - 1 -> 0) over 50 consecutive cycles.

## Quick Start & Execution 
### Prerequisites
* Linux / WSL2
* Icarus Verilog (iverilog >= 12.0)
* Python 3.10+ with cocotb

### Run Test Suite
make clean && make
