import asyncio
import threading
import time
import signal
import sys

from agents.llm_agents.all_characters_list import ALL_CHARACTERS
from all_classes.manager_class import ManagerAgent
from entities import MANAGER
from run_one_test import test_active_one_session

advisory_manager = None
keep_running = True


def signal_handler(_, __):
    global keep_running
    print("\nReceived termination signal. Shutting down...")
    keep_running = False
    stop_main_process()
    sys.exit(0)


async def start_main_process():
    global advisory_manager
    manager_charater = ALL_CHARACTERS[MANAGER][0]
    advisory_manager = ManagerAgent("manager_1", manager_charater, MANAGER)
    advisory_manager.start_in_background()
    initialization_successful = await advisory_manager.wait_for_initialization(timeout=30.0)
    if initialization_successful:
        print(f"Main process initialized successfully")
    else:
        print(f"Warning: Main process initialization timed out, continuing anyway")
    return advisory_manager


def stop_main_process():
    global advisory_manager
    if advisory_manager is None:
        print("No active listener to stop")
        return
    print("Stopping message listener...")
    try:
        advisory_manager.stop()
        print("Message listener stopped.")
    except Exception as e:
        print(f"Error stopping message listener: {e}")
    finally:
        advisory_manager = None


def keep_alive_thread():
    global keep_running
    while keep_running:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            break
    print("Keep-alive thread exiting")


async def run_main_test():
    global advisory_manager
    if advisory_manager is None:
        await start_main_process()
    print("Running test one session")
    test_active_one_session(advisory_manager)
    return True


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
