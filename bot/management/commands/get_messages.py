from django.core.management.base import BaseCommand
from bot.telegram_client import get_telegram_client
import json
from datetime import datetime


class Command(BaseCommand):
    help = 'Get all messages from a user/chat by peer ID'

    def add_arguments(self, parser):
        parser.add_argument(
            'peer_id',
            type=str,
            help='Peer ID (user ID, chat ID, or channel ID)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=100,
            help='Maximum number of messages to retrieve (default: 100)'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='table',
            choices=['table', 'json', 'simple'],
            help='Output format: table, json, or simple'
        )
        parser.add_argument(
            '--offset-id',
            type=int,
            default=0,
            help='Offset message ID (to get messages before this ID)'
        )

    def handle(self, *args, **options):
        peer_id = options['peer_id']
        limit = options['limit']
        output_format = options['format']
        offset_id = options['offset_id']
        
        client = get_telegram_client()
        
        if not client.is_configured():
            self.stdout.write(
                self.style.ERROR('Telegram client is not properly configured. Please check your .env file.')
            )
            return
        
        # Check if phone number is set
        if not client.phone_number:
            self.stdout.write(
                self.style.ERROR(
                    '\n⚠️  ERROR: To get messages, you need to use a USER account, not a bot account.\n'
                    'Please add TELEGRAM_PHONE_NUMBER to your .env file.\n'
                )
            )
            return
        
        # Convert peer_id to integer (handle negative IDs for groups/channels)
        try:
            if peer_id.startswith('-'):
                peer_id_int = int(peer_id)
            else:
                peer_id_int = int(peer_id)
        except ValueError:
            self.stdout.write(
                self.style.ERROR(f'Invalid peer ID: {peer_id}. Must be a number.')
            )
            return
        
        self.stdout.write(self.style.SUCCESS(f'Fetching messages from peer ID: {peer_id_int}'))
        self.stdout.write(self.style.WARNING(f'Limit: {limit} messages'))
        
        # Get messages
        messages = client.get_messages(peer_id_int, limit=limit, offset_id=offset_id)
        
        if not messages:
            self.stdout.write(self.style.WARNING('No messages found.'))
            return
        
        # Display messages
        if output_format == 'json':
            self.stdout.write(json.dumps(messages, indent=2, ensure_ascii=False, default=str))
        elif output_format == 'simple':
            self._print_simple(messages)
        else:  # table format
            self._print_table(messages)
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {len(messages)} messages retrieved')
        )
    
    def _print_simple(self, messages):
        """Print messages in simple format"""
        for msg in messages:
            date = str(msg.get('date', 'N/A'))
            sender = msg.get('sender_name') or 'Unknown'
            text = msg.get('text') or ''
            if not text:
                media_type = msg.get('media_type') or 'Media'
                text = f"[{media_type}]"
            text = str(text)[:100]  # First 100 chars
            msg_id = msg.get('id', 'N/A')
            
            self.stdout.write(f"[{date}] {sender} (ID: {msg_id}): {text}")
    
    def _print_table(self, messages):
        """Print messages in a formatted table"""
        self.stdout.write("\n" + "=" * 120)
        self.stdout.write(f"{'ID':<10} {'Date':<20} {'Sender':<25} {'Message':<60}")
        self.stdout.write("=" * 120)
        
        for msg in messages:
            msg_id = str(msg.get('id', 'N/A'))
            date = str(msg.get('date', 'N/A'))[:19] if msg.get('date') else 'N/A'  # Truncate date
            sender = (msg.get('sender_name') or 'Unknown')[:23]
            
            # Get message text or media type, handle None values
            text = msg.get('text') or ''
            if not text:
                media_type = msg.get('media_type') or 'Media'
                text = f"[{media_type}]"
            text = str(text)[:58]  # Ensure it's a string and truncate
            
            self.stdout.write(
                f"{msg_id:<10} {date:<20} {sender:<25} {text:<60}"
            )
        
        self.stdout.write("=" * 120)

