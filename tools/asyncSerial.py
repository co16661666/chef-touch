import serial
import threading
import time

class AsyncSerialReader:
    def __init__(self, port, baudrate=9600):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        self.latest_line = None
        self.running = True
        self.lock = threading.Lock()
        
        # Start the background thread
        self.thread = threading.Thread(target=self._update, daemon=True)
        self.thread.start()

    def _update(self):
        """Internal method to constantly read from the serial port."""
        while self.running:
            if self.ser.in_waiting > 0:
                try:
                    # Read the line and decode
                    data = self.ser.readline().decode('utf-8').strip()
                    if data:
                        # Use a lock to prevent race conditions during the write
                        with self.lock:
                            self.latest_line = data
                except Exception as e:
                    print(f"Serial Error: {e}")
            
            # Tiny sleep to yield to other threads
            time.sleep(0.01)

    def get_latest(self):
        """Retrieve the most recent line captured by the thread."""
        with self.lock:
            return self.latest_line

    def stop(self):
        """Clean up the serial port and thread."""
        self.running = False
        self.thread.join()
        self.ser.close()