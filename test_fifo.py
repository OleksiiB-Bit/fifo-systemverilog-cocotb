import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

@cocotb.test()
async def test_fifo_antiparallel(dut):
	"""Automatisierter Test 1: Sequentielles Speichern von 16 Elementen und deren Abruf."""
	# 1. Taktgenerator starten
	clock = Clock(dut.clk, 20, unit="ns")
	cocotb.start_soon(clock.start())

	# 2. Initialer Reset
	dut.reset.value = 1
	dut.rd_en.value = 0
	dut.wr_en.value = 0
	await Timer(100, unit="ns")
	dut.reset.value = 0
	await RisingEdge(dut.clk)
	assert dut.empty.value == 1, "Fehler: Der Speicher muss nach dem Zurücksetzen leer sein!"

	# 3. Array einschreiben und ablesen 16 8-bit Zahlen (nicht gleichzeitig)
	test_bytes = [random.randint(0, 255) for _ in range(16)]
	for byte_to_write in test_bytes:
		dut.wr_en.value = 1
		dut.din.value = byte_to_write
		await RisingEdge(dut.clk)
		dut.wr_en.value = 0
		await RisingEdge(dut.clk)
	assert dut.full.value == 1, "Fehler: mem[] soll voll sein!"

	for byte_to_read in test_bytes:
		await Timer(1, unit="ns")
		received_byte = int(dut.dout.value)
		assert byte_to_read == received_byte, f"Fehler! Gesendet: {byte_to_read}, Empfangen: {received_byte}"
		dut._log.info(f"Gesendet: {byte_to_read}, Empfangen: {received_byte}")
		dut.rd_en.value = 1
		await RisingEdge(dut.clk)
		dut.rd_en.value = 0
		await RisingEdge(dut.clk)
	assert dut.empty.value == 1, "Fehler: Der Speicher muss leer sein!"

	dut._log.info("Test 1 erfolgreich und fehlerfrei abgeschlossen!")


@cocotb.test()
async def test_fifo_parallel(dut):
	"""Automatisierter Test 2: Gleichzeitiges Schreiben und Lesen von Elementen im Datenstrom."""
	# 1. Taktgenerator starten
	clock = Clock(dut.clk, 20, unit="ns")
	cocotb.start_soon(clock.start())

	# 2. Initialer Reset
	dut.reset.value = 1
	dut.rd_en.value = 0
	dut.wr_en.value = 0
	await Timer(100, unit="ns")
	dut.reset.value = 0
	await RisingEdge(dut.clk)
	assert dut.empty.value == 1, "Fehler: Der Specher muss leer sein!"

	# 3. Array einschreiben und ablesen 16 8-bit Zahlen (gleichzeitig)

	preload = [10, 20]
	for val in preload:
		dut.wr_en.value = 1
		dut.din.value = val
		await RisingEdge(dut.clk)
	dut.wr_en.value = 0

	test_bytes2 = [random.randint(0, 255) for _ in range(14)]
	expected_queue = preload + test_bytes2
	for byte in test_bytes2:
		await Timer(1, unit="ns")
		expected_val = expected_queue.pop(0)
		received_byte = int(dut.dout.value)
		assert expected_val == received_byte, f"Fehler! Gesendet: {byte}, Empfangen: {received_byte}"
		dut._log.info(f"Gesendet: {byte}, Empfangen: {received_byte}")
		dut.wr_en.value = 1
		dut.rd_en.value = 1
		dut.din.value = byte
		await RisingEdge(dut.clk)
		dut.wr_en.value = 0
		dut.rd_en.value = 0
		await RisingEdge(dut.clk)
	for _ in range(2):
		dut.rd_en.value = 1
		await RisingEdge(dut.clk)
		dut.rd_en.value = 0
		await RisingEdge(dut.clk)
	assert dut.empty.value == 1, "Fehler: Der Speicher muss leer sein!"

	dut._log.info("Test 2 erfolgreich und fehlerfrei bestanden!")


@cocotb.test()
async def test_fifo_wraparound(dut):
	"""Automatisierter Test 3: Stresstest für die Ringadressierung (Übergang von 15 nach 0)."""
	# 1. Taktgenerator starten
	clock = Clock(dut.clk, 20, unit="ns")
	cocotb.start_soon(clock.start())

	# 2. Initialer Reset
	dut.reset.value = 1
	dut.rd_en.value = 0
	dut.wr_en.value = 0
	await Timer(100, unit="ns")
	dut.reset.value = 0
	await RisingEdge(dut.clk)
	assert dut.empty.value == 1, "Fehler: Der Specher muss leer sein!"

	# 3. Array einschreiben und ablesen 50 8-bit Zahlen (Zufallzahlen)
	for i in range(50):
		byte_to_test = random.randint(0, 255)
		dut.wr_en.value = 1
		dut.din.value = byte_to_test
		await RisingEdge(dut.clk)
		dut.wr_en.value = 0
		await Timer(1, unit="ns")
		received_byte = int(dut.dout.value)
		assert byte_to_test == received_byte, f"Zeigerübergangsfehler! Gesendet: {byte_to_test}, Empfangen: {received_byte}"
		dut._log.info(f"Gesendet: {byte_to_test}, Empfangen: {received_byte}")
		dut.rd_en.value = 1
		await RisingEdge(dut.clk)
		dut.rd_en.value = 0
	await RisingEdge(dut.clk)
	assert dut.empty.value == 1, "Fehler: Der Speicher muss leer sein!"

	dut._log.info("Test 3 erfolgreich und fehlerfrei bestanden!")



	dut._log.info("Alle Tests wurden erfolgreich und fehlerfrei bestanden!")
