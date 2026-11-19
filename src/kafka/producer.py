from aiokafka import AIOKafkaProducer
from src.core.config import settings
import json
from src.logger_core.logging_config import logger


class KafkaProducerService:
    def __init__(self):
        self._producer: AIOKafkaProducer | None = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.kafka.kafka_bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )
        await self._producer.start()
        logger.info("Кафка продюсер запущен")

    async def stop(self):
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None
            logger.info("Кафка продюсер остановлен")

    async def send_inn_task(self, task_id: str, inn: str):
        if self._producer is None:
            logger.error("KafkaProducerService не запущен")
            raise RuntimeError("KafkaProducerService is not started.")
        await self._producer.send_and_wait(
            settings.kafka.kafka_topic_inn,
            {"task_id": task_id, "inn": inn}
        )
        logger.info("Послано сообщение с ИНН в кафку: inn=%s", inn)