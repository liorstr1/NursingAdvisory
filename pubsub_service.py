import json
import time
import threading
from google.cloud import pubsub_v1
from google.api_core.exceptions import NotFound
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import os


class PubSubService:
    _publisher_clients = {}
    _subscriber_clients = {}
    _topic_cache = {}  # Cache for existing topics
    _subscription_cache = {}  # Cache for existing subscriptions

    def __init__(self, project_id):
        self.project_id = project_id

        # Use cached clients when possible
        if project_id not in PubSubService._publisher_clients:
            PubSubService._publisher_clients[project_id] = pubsub_v1.PublisherClient(
                # Configure publisher for better performance
                publisher_options=pubsub_v1.types.PublisherOptions(
                    enable_message_ordering=True,
                    flow_control=pubsub_v1.types.PublishFlowControl(
                        message_limit=1000,
                        byte_limit=10 * 1024 * 1024,  # 10MB
                        limit_exceeded_behavior=pubsub_v1.types.LimitExceededBehavior.BLOCK,
                    )
                )
            )

        if project_id not in PubSubService._subscriber_clients:
            PubSubService._subscriber_clients[project_id] = pubsub_v1.SubscriberClient()

        self.publisher = PubSubService._publisher_clients[project_id]
        self.subscriber = PubSubService._subscriber_clients[project_id]

        # Pre-format paths to avoid string operations during runtime
        self.subscription_path = f"projects/{self.project_id}/subscriptions/{{}}"
        self.topic_path = f"projects/{self.project_id}/topics/{{}}"

        # Instance variables
        self.thread_pool = ThreadPoolExecutor(
            max_workers=min(32, (os.cpu_count() or 1) * 2),
            thread_name_prefix=f"pubsub_worker_{project_id}"
        )
        self._subscriber_threads = []
        self._active_streaming_futures = {}
        self._lock = threading.RLock()  # Reentrant lock for thread safety

    def check_or_create_topic(self, topic_name: str):
        """Check if topic exists and create if not (with caching)"""
        # Check cache first
        cache_key = f"{self.project_id}:{topic_name}"
        if cache_key in PubSubService._topic_cache:
            return PubSubService._topic_cache[cache_key]

        topic_path = self.topic_path.format(topic_name)
        try:
            with self._lock:
                if cache_key in PubSubService._topic_cache:
                    return PubSubService._topic_cache[cache_key]

                self.publisher.get_topic(request={"topic": topic_path})
                PubSubService._topic_cache[cache_key] = topic_path
                return topic_path
        except NotFound:
            with self._lock:
                self.publisher.create_topic(request={"name": topic_path})
                print(f"Created topic: {topic_name}")
                PubSubService._topic_cache[cache_key] = topic_path
                return topic_path

    def check_or_create_subscription(self, topic_name: str, subscription_name: str):
        """Check if subscription exists and create if not (with caching)"""
        # Check cache first
        cache_key = f"{self.project_id}:{subscription_name}"
        if cache_key in PubSubService._subscription_cache:
            return PubSubService._subscription_cache[cache_key]

        subscription_path = self.subscription_path.format(subscription_name)
        topic_path = self.check_or_create_topic(topic_name)  # Ensure topic exists

        try:
            with self._lock:
                if cache_key in PubSubService._subscription_cache:
                    return PubSubService._subscription_cache[cache_key]

                self.subscriber.get_subscription(
                    request={"subscription": subscription_path}
                )
                PubSubService._subscription_cache[cache_key] = subscription_path
                return subscription_path
        except NotFound:
            with self._lock:
                # Create with optimized settings
                self.subscriber.create_subscription(
                    request={
                        "name": subscription_path,
                        "topic": topic_path,
                        "enable_exactly_once_delivery": True,
                        "ack_deadline_seconds": 10,  # Reduced from 10
                        "message_retention_duration": {"seconds": 600},  # 10 minutes
                        "expiration_policy": {"ttl": {"seconds": 86400}},  # 1 day
                        "enable_message_ordering": True,
                    }
                )
                print(f"Created subscription: {subscription_name} for topic: {topic_name}")
                PubSubService._subscription_cache[cache_key] = subscription_path
                return subscription_path

    def subscribe_to_topic(
            self, topic_name: str, subscription_name: str, message_handler
    ):
        """Subscribe to a topic with improved error handling and performance"""
        # Ensure topic and subscription exist
        subscription_path = self.check_or_create_subscription(topic_name, subscription_name)

        def callback(message, max_retries=2):
            try:
                # Get retry count if available
                retry_count = 0
                if hasattr(message, 'attributes') and 'retry_count' in message.attributes:
                    retry_count = int(message.attributes['retry_count'])

                # Check if we've exceeded max retries
                if retry_count >= max_retries:
                    print(f"Message failed after {retry_count} retries, dropping message")
                    message.ack()  # Acknowledge to remove from queue
                    return

                # Try to decode and process message
                try:
                    if isinstance(message.data, bytes):
                        # Try to decode as UTF-8 with replacement for invalid chars
                        message_str = message.data.decode('utf-8', errors='replace')

                        # Try JSON or tab-delimited parsing
                        try:
                            if message_str.strip().startswith('{'):
                                # Looks like JSON
                                decoded_message = json.loads(message_str)
                            else:
                                # Try a basic parsing for tab-delimited format
                                # This is a simplified version - you might need to adjust based on your format
                                parsed_message = {}
                                # Just use the original message if parsing fails
                                decoded_message = message.data
                        except:
                            # If parsing fails, log and drop
                            print(f"Failed to parse message format, dropping: {message_str[:100]}...")
                            message.ack()
                            return
                    else:
                        # Not bytes, use as is
                        decoded_message = message.data

                    # Process the message
                    result = message_handler(decoded_message)

                    if result:
                        message.ack()
                    else:
                        print(f"Message handler returned False, dropping message after {retry_count} retries")
                        message.ack()

                except UnicodeDecodeError:
                    # For messages that can't be decoded properly
                    print(f"Unicode decode error, dropping message")
                    message.ack()

                except json.JSONDecodeError:
                    # For messages that aren't valid JSON
                    print(f"JSON decode error, dropping message")
                    message.ack()

                except Exception as e:
                    print(f"Error processing message: {e}")
                    message.ack()

            except Exception as outer_e:
                # Catch-all for any errors in the callback itself
                print(f"Critical error in message callback, dropping message: {outer_e}")
                message.ack()

        # Configure flow control for better performance
        flow_control = pubsub_v1.types.FlowControl(
            max_messages=25,  # Process in smaller batches
            max_bytes=5 * 1024 * 1024,  # 5MB limit
            max_lease_duration=10,  # 10 seconds
        )

        # Create streaming pull future with optimized settings
        streaming_pull_future = self.subscriber.subscribe(
            subscription_path,
            callback=callback,
            flow_control=flow_control,
        )

        # Store reference to the future
        key = f"{topic_name}:{subscription_name}"
        self._active_streaming_futures[key] = streaming_pull_future

        def stream_messages():
            """Handle the streaming pull with improved error recovery"""
            i_key = f"{topic_name}:{subscription_name}"
            retry_count = 0
            max_retries = 5
            retry_delay = 1

            while i_key in self._active_streaming_futures:
                try:
                    self._active_streaming_futures[i_key].result(timeout=120)
                    break
                except TimeoutError:
                    if i_key not in self._active_streaming_futures:
                        break

                    print(f"PubSub stream {i_key} timed out, continuing...")
                except Exception as e:

                    if i_key not in self._active_streaming_futures:
                        break

                    retry_count += 1
                    print(f"PubSub stream {i_key} error ({retry_count}/{max_retries}): {e}")

                    if retry_count >= max_retries:
                        print(f"Too many errors for {i_key}, stopping subscription")
                        break
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 60)  # Cap at 60 seconds

                    try:
                        print(f"Resubscribing to {i_key}...")
                        self._active_streaming_futures[key] = self.subscriber.subscribe(
                            subscription_path,
                            callback=callback,
                            flow_control=flow_control
                        )
                    except Exception as sub_error:
                        print(f"Failed to resubscribe to {i_key}: {sub_error}")
            with self._lock:
                if key in self._active_streaming_futures:
                    del self._active_streaming_futures[key]

            print(f"Subscription {key} stream handler exited")
        subscriber_thread = threading.Thread(
            target=stream_messages,
            daemon=True,
            name=f"pubsub-{topic_name}-{subscription_name}"
        )
        subscriber_thread.start()
        self._subscriber_threads.append(subscriber_thread)

        return subscriber_thread

    def publish_message(self, topic_name: str, data: dict):
        """Publish message with improved performance and error handling"""
        topic_path = self.check_or_create_topic(topic_name)
        data_bytes = json.dumps(data).encode("utf-8")

        try:
            future = self.publisher.publish(topic=topic_path, data=data_bytes)

            def on_publish(publish_future):
                try:
                    message_id = publish_future.result(timeout=2)
                    if 'message_id' in data:
                        print(f"Published message {data['message_id']} to {topic_name}, got ID: {message_id}")
                except Exception as ex:
                    print(f"Error publishing to {topic_name}: {ex}")

            future.add_done_callback(on_publish)
            return future

        except Exception as e:
            print(f"Error publishing message to {topic_name}: {e}")
            raise

    def close(self):
        for key, future in list(self._active_streaming_futures.items()):
            try:
                print(f"Cancelling subscription {key}")
                future.cancel()
                del self._active_streaming_futures[key]
            except Exception as e:
                print(f"Error cancelling subscription {key}: {e}")

        for thread in self._subscriber_threads:
            if thread.is_alive():
                thread.join(timeout=1)

        if hasattr(self, 'thread_pool') and self.thread_pool:
            self.thread_pool.shutdown(wait=False)

        self.publisher = None
        self.subscriber = None
