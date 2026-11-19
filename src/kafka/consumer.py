import json
from aiokafka import AIOKafkaConsumer
from collections.abc import Callable, Awaitable
from src.logger_core.logging_config import logger
from src.core.config import settings

MessageHandler = Callable[[dict], Awaitable[None]]

class KafkaConsumerService:

    def __init__(self):
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self):
        self._consumer = AIOKafkaConsumer(
            settings.kafka.kafka_topic_inn,
            bootstrap_servers=settings.kafka.kafka_bootstrap_servers,
            group_id=settings.kafka.kafka_group_id,
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            enable_auto_commit=False,
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        logger.info(
            "Kafka consumer started: topic=%s group=%s",
            settings.kafka.kafka_topic_inn,
            settings.kafka.kafka_group_id,
        )

    async def stop(self):
        if self._consumer is not None:
            await self._consumer.stop()
            self._consumer = None
            logger.info("Kafka consumer stopped")

    async def fetch_messages(self, handler: MessageHandler):
        if self._consumer is None:
            raise RuntimeError("KafkaConsumerService is not started")
        async for msg in self._consumer:
            logger.info(
                "Received: topic=%s partition=%s offset=%s value=%s",
                msg.topic, msg.partition, msg.offset, msg.value,
            )
            try:
                await handler(msg.value)
                await self._consumer.commit()
            except Exception:
                logger.exception(
                    "Handler failed: offset=%s value=%s",
                    msg.offset, msg.value,
                )
