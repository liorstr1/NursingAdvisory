import asyncio
import threading
import time
import signal
import sys
from main_advisory_center import AdvisoryCenter

advisory_center = None
keep_running = True


def signal_handler(_, __):
    global keep_running
    print("\nReceived termination signal. Shutting down...")
    keep_running = False
    stop_main_process()
    sys.exit(0)


async def start_main_process():
    """Start the AdvisoryCenter and keep it running"""
    global advisory_center

    advisory_center = AdvisoryCenter()
    advisory_center.start_in_background()
    initialization_successful = await advisory_center.wait_for_initialization(timeout=30.0)

    if initialization_successful:
        print(f"Main process initialized successfully")
    else:
        print(f"Warning: Main process initialization timed out, continuing anyway")
    return advisory_center


def stop_main_process():
    """
    Stop the main process gracefully
    """
    global advisory_center
    if advisory_center is None:
        print("No active listener to stop")
        return

    print("Stopping message listener...")
    try:
        advisory_center.stop()
        print("Message listener stopped.")
    except Exception as e:
        print(f"Error stopping message listener: {e}")
    finally:
        advisory_center = None


def keep_alive_thread():
    """Thread to keep the main process running until explicitly stopped"""
    global keep_running
    while keep_running:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    print("Keep-alive thread exiting")


async def run_main_test():
    """Start the advisory center and run tests"""
    global advisory_center

    # Start the advisory center if not already running
    if advisory_center is None:
        await start_main_process()

    # Run your test here
    print("Running test one session")
    test_active_one_session()


    # Add your actual test code here
    print("Simulating test operations...")

    # Example: Test PubSub connectivity
    print("Testing PubSub connectivity...")
    # Your PubSub test code here

    # Example: Test message handling
    print("Testing message handling...")
    # Your message handling test code here

    # Example: Test database operations
    print("Testing database operations...")
    # Your database test code here

    print("Test completed. Advisory center still running.")
    return True  # Return success/failure status


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)

    RUN_TESTS = True
    KEEP_RUNNING = True

    print("Starting advisory center...")

    if RUN_TESTS:
        print("Starting AdvisoryCenter and running test...")
        asyncio.run(run_main_test())
        if not KEEP_RUNNING:
            print("Test completed. Shutting down AdvisoryCenter.")
            stop_main_process()
            sys.exit(0)
    else:
        asyncio.run(start_main_process())

    keep_alive = threading.Thread(target=keep_alive_thread, daemon=False)
    keep_alive.start()

    print("AdvisoryCenter is running. Press Ctrl+C to stop.")
    try:
        keep_alive.join()
    except KeyboardInterrupt:
        keep_running = False
        stop_main_process()
        sys.exit(0)
