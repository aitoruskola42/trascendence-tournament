from django.core.management.base import BaseCommand
import pika
import json
import pytz
import os
import time
from datetime import datetime
from api.models import Match

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		rabbitmq_host = os.getenv("RABBITMQ_HOST")
		rabbitmq_user = os.getenv("RABBITMQ_DEFAULT_USER")
		rabbitmq_pass = os.getenv("RABBITMQ_DEFAULT_PASS")
		match_history_queue = os.getenv("RABBITMQ_PONG_MATCH_QUEUE")

		while True:
			try:
				connection = pika.BlockingConnection(
					pika.ConnectionParameters(
						host=rabbitmq_host,
						credentials=pika.PlainCredentials(
							rabbitmq_user,
							rabbitmq_pass
						)
					)
				)
				channel = connection.channel()
				channel.queue_declare(queue=match_history_queue)

				def callback(ch, method, properties, body):
					data = json.loads(body)
					Match.objects.create(
						tournament_id=data.get('tournament_id'),
						player1_id=data.get('player1_id'),
						player2_id=data.get('player2_id'),
						player1_display_name=data.get('player1_display_name'),
						player2_display_name=data.get('player2_display_name'),
						player1_score=data.get('player1_score'),
						player2_score=data.get('player2_score'),
						match_type=data.get('match_type'),
						winner_id=data.get('winner_id'),
						date=datetime.now(pytz.UTC)
					)

				channel.basic_consume(
					queue=match_history_queue,
					on_message_callback=callback,
					auto_ack=True
				)
				channel.start_consuming()

			except Exception as e:
				retry_wait = 5
				self.stderr.write(f"Message queue error: {e}")
				self.stderr.write(f"Retrying connection in {retry_wait} seconds...")
				time.sleep(retry_wait)
