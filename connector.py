import time
from concurrent.futures import ThreadPoolExecutor
import uuid
from queue import Queue
from TestBot.init_threads import init_active_threads, received_messages, message_timings, get_message_async
from pubsub_connectors import SendDirectMessage


class Connector:
    def __init__(self, set_prefix=None):
        self.thread_pool = ThreadPoolExecutor(max_workers=4, thread_name_prefix="connector_worker")
        self._pubsub_client = None
        self.set_prefix = set_prefix
        self._init_complete = False
        self._initialize()

    def _initialize(self):
        if self._init_complete:
            return
        init_active_threads()
        self._pubsub_client = SendDirectMessage(self.set_prefix)
        while not received_messages.empty():
            received_messages.get()

        self._init_complete = True

    def get_response_for_one_message(self, client_id, user_id, message, timeout=30):
        if not self._init_complete:
            self._initialize()

        result_queue = Queue()
        message_id = str(uuid.uuid4())

        while not received_messages.empty():
            received_messages.get()

        self.thread_pool.submit(
            self._send_and_receive,
            client_id, user_id, message, result_queue, message_id, timeout
        )

        try:
            result = result_queue.get(timeout=timeout)
            return result
        except Exception as e:
            print("Timeout waiting for response", e.args)
            return {
                "response": None,
                "latency": None,
                "message_id": message_id,
                "latency_breakdown": {"error": f"Timeout waiting for response after {timeout}s"}
            }

    async def get_response_async(self, client_id, user_id, message, timeout=30):
        if not self._init_complete:
            self._initialize()

        message_id = str(uuid.uuid4())
        while not received_messages.empty():
            received_messages.get()

        start_time = time.time()
        message_timings[message_id] = {
            "init_time": start_time,
            "pubsub_send_start": time.time(),
            "pubsub_send_complete": 0,
            "response_received": 0,
            "processing_complete": 0
        }

        if self._pubsub_client is None:
            self._pubsub_client = SendDirectMessage(self.set_prefix)

        print(f"Sending message to {user_id}: {message} [ID: {message_id}]")
        self._pubsub_client.send_direct_message(message, client_id, user_id, message_id)
        sent_time = time.time()
        message_timings[message_id]["pubsub_send_complete"] = sent_time

        print(
            f"Message sent. PubSub send latency: "
            f"{(sent_time - message_timings[message_id]['pubsub_send_start']) * 1000:.2f} ms")

        response_data = await get_message_async(timeout)

        if response_data is None:
            print(f"Async timeout waiting for response after {timeout}s")
            return {
                "response": None,
                "latency": None,
                "message_id": message_id,
                "latency_breakdown": {"error": f"Timeout waiting for response after {timeout}s"}
            }

        if isinstance(response_data, dict):
            response = response_data.get("message", str(response_data))
            received_message_id = response_data.get("message_id", "unknown")
        else:
            response = response_data
            received_message_id = "unknown"

        end_time = time.time()
        message_timings[message_id]["response_received"] = end_time
        total_latency = (end_time - start_time) * 1000
        processing_end = time.time()
        message_timings[message_id]["processing_complete"] = processing_end

        latency_breakdown = {
            "client_preparation": (message_timings[message_id]["pubsub_send_start"] - start_time) * 1000,
            "pubsub_outgoing": (message_timings[message_id]["pubsub_send_complete"] -
                                message_timings[message_id]["pubsub_send_start"]) * 1000,
            "bot_processing": (message_timings[message_id]["response_received"] -
                               message_timings[message_id]["pubsub_send_complete"]) * 1000,
            "response_processing": (processing_end - message_timings[message_id]["response_received"]) * 1000,
            "total_latency": total_latency
        }

        print(f"Response received [ID: {received_message_id}]. Total latency: {total_latency:.2f} ms")

        return {
            "response": response,
            "latency": total_latency,
            "send_time": start_time,
            "receive_time": end_time,
            "message_id": message_id,
            "received_message_id": received_message_id,
            "latency_breakdown": latency_breakdown
        }

    def _send_and_receive(self, client_id, user_id, message, result_queue, message_id, timeout=30):
        """
        Send a message and wait for response (internal implementation)

        This method runs in a separate thread and puts result in the queue
        """
        print(f"Sending message to {user_id}: {message} [ID: {message_id}]")

        # Record timing information
        start_time = time.time()
        message_timings[message_id] = {
            "init_time": start_time,
            "pubsub_send_start": time.time(),
            "pubsub_send_complete": 0,
            "response_received": 0,
            "processing_complete": 0
        }

        if self._pubsub_client is None:
            self._pubsub_client = SendDirectMessage(self.set_prefix)

        self._pubsub_client.send_direct_message(message, client_id, user_id, message_id)
        sent_time = time.time()
        message_timings[message_id]["pubsub_send_complete"] = sent_time

        print(
            f"Message sent successfully. PubSub send latency: "
            f"{(sent_time - message_timings[message_id]['pubsub_send_start']) * 1000:.2f} ms")

        polling_interval = 0.05
        wait_start = time.time()

        while time.time() - wait_start < timeout:
            try:
                if not received_messages.empty():
                    priority, response_data = received_messages.get_nowait()

                    if isinstance(response_data, dict):
                        response = response_data.get("message", str(response_data))
                        received_message_id = response_data.get("message_id", "unknown")
                    else:
                        response = response_data
                        received_message_id = "unknown"

                    end_time = time.time()
                    message_timings[message_id]["response_received"] = end_time
                    total_latency = (end_time - start_time) * 1000
                    processing_end = time.time()
                    message_timings[message_id]["processing_complete"] = processing_end

                    pubsub_send_start = message_timings[message_id]["pubsub_send_start"]
                    pubsub_send_complete = message_timings[message_id]["pubsub_send_complete"]
                    response_received = message_timings[message_id]["response_received"]

                    latency_breakdown = {
                        "client_preparation": (pubsub_send_start - start_time) * 1000,
                        "pubsub_outgoing": (pubsub_send_complete - pubsub_send_start) * 1000,
                        "bot_processing": (response_received - pubsub_send_complete) * 1000,
                        "response_processing": (processing_end - response_received) * 1000,
                        "total_latency": total_latency
                    }

                    print(f"Response received [ID: {received_message_id}]. Total latency: {total_latency:.2f} ms")
                    print("Latency breakdown:")
                    for component, time_ms in latency_breakdown.items():
                        if component != "total_latency":
                            percentage = (time_ms / total_latency) * 100
                            print(f"  {component}: {time_ms:.2f} ms ({percentage:.1f}%)")

                    result_queue.put({
                        "response": response,
                        "latency": total_latency,
                        "send_time": start_time,
                        "receive_time": end_time,
                        "message_id": message_id,
                        "received_message_id": received_message_id,
                        "latency_breakdown": latency_breakdown
                    })
                    return

                # Short sleep to prevent CPU spinning
                time.sleep(polling_interval)
            except Exception as e:
                print(f"Error processing response: {e}")

        # Timeout occurred
        print(f"Timeout waiting for response for message ID: {message_id}")
        result_queue.put({
            "response": None,
            "latency": None,
            "message_id": message_id,
            "latency_breakdown": {"error": f"Timeout waiting for response after {timeout}s"}
        })
