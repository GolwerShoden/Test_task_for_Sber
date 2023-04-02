from fastapi import FastAPI
from pydantic import BaseModel
from kafka import KafkaProducer, KafkaConsumer, TopicPartition


# BOOTSTRAP_SERVERS = ['localhost:9093']
BOOTSTRAP_SERVERS = ['kafka:9092']
API_VERSION = (2, 5, 0)

app = FastAPI(title="My Kafka Producer API")


class MessageRequest(BaseModel):
    message: str


@app.post("/messages/{topic_name}", status_code=201)
def send_message(topic_name, message_request: MessageRequest) -> dict[str, str]:

    producer = KafkaProducer(
        bootstrap_servers=BOOTSTRAP_SERVERS,
        api_version=API_VERSION,
        value_serializer=lambda x: x.encode('utf-8')
    )
    producer.send(topic_name, value=message_request.message)
    return {"detail": "Message sent to Kafka"}


@app.get("/messages/{topic_name}")
def get_last_kafka_messages(topic_name, message_count: int = 10) -> list[str]:
    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        auto_offset_reset='latest',
        enable_auto_commit=False,
        group_id=None,
        value_deserializer=lambda x: x.decode('utf-8'),
        api_version=API_VERSION
    )
    # Костыль т.к. в библиотеке не сразу идёт подписка на топики из-за чего ошибка при consumer.position
    while not consumer._client.poll():
        continue

    topic_partition = TopicPartition(topic_name, 0)

    # Переставляем каретка на 10 сообщений назад
    last_offset = consumer.position(topic_partition)
    start_offset = max(last_offset - message_count, 0)
    consumer.seek(topic_partition, start_offset)

    # Получение 10 сообщений
    messages = []
    count = last_offset - start_offset
    for message in consumer:
        messages.append(message.value)
        # Ограничение, что бы после получения 10 или меньше сообщений не ждал нового
        if len(messages) == count:
            break
    consumer.close()
    return messages
