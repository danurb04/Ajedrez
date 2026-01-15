# spi_link.py
import spidev
import time

class SpiLink:
    def __init__(self, bus=0, device=0, speed=500000, mode=0b00):
        self.spi = spidev.SpiDev()
        self.spi.open(bus, device)          # /dev/spidev0.0
        self.spi.max_speed_hz = speed
        self.spi.mode = mode

    def close(self):
        self.spi.close()

    def send_line(self, line: str) -> None:
        # Envía una línea terminada en '\n'
        msg = (line + "\n").encode("ascii")
        self.spi.xfer2(list(msg))
        time.sleep(0.002)

    def send_board(self, board) -> None:
        """
        board: lista 8x8 con strings tipo 'wP', 'bK' o '--'
        Se envía como 64 tokens separados por coma.
        """
        flat = ",".join(board[r][c] for r in range(8) for c in range(8))
        self.send_line("B " + flat)   # Prefijo B = Board
        
    def send_raw(self, s:str):
            self.spi.xfer2(list(s.encode('ascii')))
