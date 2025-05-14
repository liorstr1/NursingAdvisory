import sys
import signal
import atexit

from nursing_advisory_center import AdvisoryCenter

sys.stdout.reconfigure(line_buffering=True)


class NursingAdvisoryRunner:
    def __init__(self):
        self.advisory_center = None
        self.running = False

    def start(self):
        """Initialize and start the AdvisoryCenter in its own thread"""
        try:
            print("Starting nursing advisory center...")

            # Initialize AdvisoryCenter
            self.advisory_center = AdvisoryCenter()
            self.running = True

            atexit.register(self.shutdown)
            signal.signal(signal.SIGINT, self._signal_handler)
            if hasattr(signal, 'SIGBREAK'):
                signal.signal(signal.SIGBREAK, self._signal_handler)
            self.advisory_center.start_async()

            return self.advisory_center

        except Exception as e:
            print(f"Error initializing AdvisoryCenter: {str(e)}")
            self.shutdown()
            raise

    def shutdown(self):
        """Shut down the AdvisoryCenter gracefully"""
        if not self.running:
            return

        print("Shutting down nursing advisory center...")
        self.running = False

        if self.advisory_center:
            # The AdvisoryCenter already has its own cleanup method
            self.advisory_center.cleanup()

        self.advisory_center = None
        print("Nursing advisory center shutdown complete")

    def _signal_handler(self, _, __):
        print("\nReceived interrupt signal, shutting down...")
        self.shutdown()
        sys.exit(0)

    def get_active_center(self):
        return self.advisory_center


if __name__ == "__main__":
    runner = NursingAdvisoryRunner()
    runner.start()

    # Keep the main thread alive
    try:
        import time

        while runner.running:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
