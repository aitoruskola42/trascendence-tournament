from django.core.management.base import BaseCommand
import pika
import json
import pytz
import os
from datetime import datetime
from api.models import Match

class Command(BaseCommand):
	def handle(self, *args, **kwargs):
		connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='match_history_rabbitmq',
                credentials=pika.PlainCredentials(
                    os.getenv("RABBITMQ_DEFAULT_USER"),
                    os.getenv("RABBITMQ_DEFAULT_PASS"))
            )
        )
		channel = connection.channel()
		channel.queue_declare(queue='match_results')

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
			queue='match_results',
			on_message_callback=callback,
			auto_ack=True
		)
		channel.start_consuming()
