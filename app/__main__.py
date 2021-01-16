import os
from itertools import cycle
from time import sleep
from typing import Dict
import time
import json

from redis import Redis
from redis.client import PubSub

from app.config import load_config
from app.logging import logger, initialize_logger


class NoSonarException(Exception):
    pass


def get_distance(pubsub: PubSub) -> float:
    pubsub.subscribe("subsystem.sonar.measurement", ignore_subscribe_messages=True)
    timeout = 0.5
    start = time.time()
    while cycle([True]):
        if time.time() - start > timeout:
            logger.error("Unable to get sonar measurement!!")
            raise NoSonarException("Unable to get sonar measurement")
        redis_message = pubsub.get_message()
        if redis_message is not None:
            pubsub.unsubscribe("subsystem.sonar.measurement")
            message = json.loads(redis_message['data'])
            return float(message)
        sleep(0.01)


def turn_randomly(redis_client: Redis):
    logger.debug("TODO: implement turn_randomly")
    message = json.dumps({
        "command": "turn_left",
        "speed": 1.0
    })
    redis_client.publish("subsystem.motor.command", message)
    logger.debug("TODO: use compass to know when to stop")
    time.sleep(2)
    stop_motors(redis_client)
    time.sleep(1)


def say(redis_client: Redis, phrase: str):
    redis_client.publish("subsystem.speech.command", phrase)
    time.sleep(1)


def drive(redis_client: Redis):
    message = json.dumps({
        "command": "drive",
        "speed": 1.0,
        "direction": "forward"
    })
    redis_client.publish("subsystem.motor.command", message)


def stop_motors(redis_client: Redis):
    message = json.dumps({
        "command": "stop"
    })
    redis_client.publish("subsystem.motor.command", message)


def led_on(redis_client: Redis, led_name: str):
    message = json.dumps({
        "command": "turn_on",
        "name": led_name
    })
    redis_client.publish("subsystem.led.command", message)


def led_off(redis_client: Redis, led_name: str):
    message = json.dumps({
        "command": "turn_off",
        "name": led_name
    })
    redis_client.publish("subsystem.led.command", message)


def main():
    environment: str = os.getenv("ENVIRONMENT", "dev")
    config: Dict = load_config(environment)
    initialize_logger(level=config['logging']['level'], filename=config['logging']['filename'])
    redis_host = config['redis']['host']
    redis_port = config['redis']['port']
    logger.debug(f"Connecting to redis at {redis_host}:{redis_port}")
    redis_client: Redis = Redis(
        host=redis_host, port=redis_port, db=0
    )
    pubsub: PubSub = redis_client.pubsub(ignore_subscribe_messages=True)

    try:
        say(redis_client, "here we go!")
        drive(redis_client)
        while cycle([True]):
            logger.debug("Reading distance")
            distance = get_distance(pubsub)
            logger.debug(f"Distance is {distance}")
            if distance < 40.0:
                logger.debug("Too close to an obstacle. Turning away.")
                stop_motors(redis_client)
                led_on(redis_client, "red")
                say(redis_client, "Can't go that way!")
                led_off(redis_client, "red")
                turn_randomly(redis_client)
                drive(redis_client)
            sleep(0.01)
    except Exception as e:
        logger.exception(f"Something bad happened: {str(e)}")
    finally:
        logger.debug("Cleaning up")
        stop_motors(redis_client)
        pubsub.close()
        redis_client.close()
        logger.debug("Shutting down")


if __name__ == '__main__':
    main()