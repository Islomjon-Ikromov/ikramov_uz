from django.core.management.base import BaseCommand
from bot.telegram_client import get_telegram_client
import json
from collections import defaultdict


class Command(BaseCommand):
    help = 'Get your complete message history from all groups, channels, and chats'

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Maximum number of messages per chat (default: 50)'
        )
        parser.add_argument(
            '--format',
            type=str,
            default='summary',
            choices=['summary', 'json', 'detailed'],
            help='Output format: summary, json, or detailed'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['all', 'channels', 'supergroups', 'groups', 'chats'],
            default='all',
            help='Filter by type: all, channels, supergroups, groups, or chats'
        )
        parser.add_argument(
            '--min-messages',
            type=int,
            default=1,
            help='Minimum number of messages to include a chat (default: 1)'
        )
        parser.add_argument(
            '--my-messages-only',
            action='store_true',
            help='Show only messages written by you'
        )

    def handle(self, *args, **options):
        limit = options['limit']
        output_format = options['format']
        filter_type = options['type']
        min_messages = options['min_messages']
        my_messages_only = options['my_messages_only']
        
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
                    '\n⚠️  ERROR: To get message history, you need to use a USER account.\n'
                    'Please add TELEGRAM_PHONE_NUMBER to your .env file.\n'
                )
            )
            return
        
        if my_messages_only:
            self.stdout.write(self.style.SUCCESS('📝 Mode: Showing only YOUR messages'))
        
        self.stdout.write(self.style.SUCCESS('Fetching all dialogs...'))
        self.stdout.write(self.style.WARNING('This may take a while depending on the number of chats...'))
        
        # Get all dialogs
        dialogs = client.get_all_dialogs()
        
        if not dialogs:
            self.stdout.write(self.style.WARNING('No dialogs found.'))
            return
        
        # Filter by type
        if filter_type != 'all':
            type_map = {
                'channels': 'channel',
                'supergroups': 'supergroup',
                'groups': 'group',
                'chats': 'user'
            }
            dialogs = [d for d in dialogs if d.get('type') == type_map.get(filter_type)]
        
        self.stdout.write(self.style.SUCCESS(f'Found {len(dialogs)} dialogs. Fetching messages...'))
        
        # Get messages from each dialog
        history_data = []
        total_messages = 0
        
        for i, dialog in enumerate(dialogs, 1):
            dialog_id = dialog.get('id')
            dialog_title = dialog.get('title') or dialog.get('name') or f"Chat {dialog_id}"
            dialog_type = dialog.get('type', 'unknown')
            
            self.stdout.write(f"  [{i}/{len(dialogs)}] Fetching from {dialog_title} ({dialog_type})...")
            
            try:
                messages = client.get_messages(dialog_id, limit=limit, from_user_only=my_messages_only)
                
                if len(messages) >= min_messages:
                    history_data.append({
                        'dialog': dialog,
                        'messages': messages,
                        'message_count': len(messages)
                    })
                    total_messages += len(messages)
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f"    ⚠️  Error fetching messages from {dialog_title}: {str(e)}")
                )
                continue
        
        if not history_data:
            self.stdout.write(self.style.WARNING('No messages found matching criteria.'))
            return
        
        # Display results
        if output_format == 'json':
            self._print_json(history_data)
        elif output_format == 'detailed':
            self._print_detailed(history_data, my_messages_only)
        else:  # summary
            self._print_summary(history_data, total_messages, my_messages_only)
    
    def _print_summary(self, history_data, total_messages, my_messages_only=False):
        """Print summary of message history"""
        self.stdout.write("\n" + "=" * 80)
        title = "📊 Message History Summary"
        if my_messages_only:
            title += " (Your Messages Only)"
        self.stdout.write(self.style.SUCCESS(title))
        self.stdout.write("=" * 80)
        
        # Group by type
        by_type = defaultdict(list)
        for item in history_data:
            dialog_type = item['dialog'].get('type', 'unknown')
            by_type[dialog_type].append(item)
        
        # Print statistics
        self.stdout.write(f"\nTotal Chats: {len(history_data)}")
        self.stdout.write(f"Total Messages: {total_messages}")
        if my_messages_only:
            self.stdout.write(self.style.SUCCESS("✨ Showing only YOUR messages"))
        
        self.stdout.write("\n" + self.style.SUCCESS("Breakdown by Type:"))
        type_labels = {
            'channel': '📢 Channels',
            'supergroup': '👥 Supergroups',
            'group': '💬 Groups',
            'user': '💬 Private Chats'
        }
        
        for ch_type, label in type_labels.items():
            if ch_type in by_type:
                count = len(by_type[ch_type])
                msg_count = sum(item['message_count'] for item in by_type[ch_type])
                self.stdout.write(f"  {label:<20} {count:>4} chats, {msg_count:>6} messages")
        
        # Top chats by message count
        self.stdout.write("\n" + self.style.SUCCESS("Top Chats by Message Count:"))
        sorted_data = sorted(history_data, key=lambda x: x['message_count'], reverse=True)[:10]
        
        for i, item in enumerate(sorted_data, 1):
            dialog = item['dialog']
            title = dialog.get('title') or dialog.get('name') or f"Chat {dialog.get('id')}"
            msg_count = item['message_count']
            dialog_type = dialog.get('type', 'unknown')
            
            self.stdout.write(
                f"  {i:>2}. {title[:50]:<50} ({dialog_type}) - {msg_count:>4} messages"
            )
        
        self.stdout.write("=" * 80 + "\n")
    
    def _print_detailed(self, history_data, my_messages_only=False):
        """Print detailed message history"""
        self.stdout.write("\n" + "=" * 100)
        title = "📨 Detailed Message History"
        if my_messages_only:
            title += " (Your Messages Only)"
        self.stdout.write(self.style.SUCCESS(title))
        self.stdout.write("=" * 100)
        
        for item in history_data:
            dialog = item['dialog']
            messages = item['messages']
            title = dialog.get('title') or dialog.get('name') or f"Chat {dialog.get('id')}"
            dialog_type = dialog.get('type', 'unknown')
            
            self.stdout.write(f"\n{'=' * 100}")
            self.stdout.write(
                self.style.SUCCESS(f"💬 {title} ({dialog_type.upper()}) - {len(messages)} messages")
            )
            self.stdout.write("=" * 100)
            
            for msg in messages[:20]:  # Show first 20 messages per chat
                msg_id = msg.get('id', 'N/A')
                date = str(msg.get('date', 'N/A'))[:19] if msg.get('date') else 'N/A'
                sender = msg.get('sender_name') or 'Unknown'
                
                text = msg.get('text') or ''
                if not text:
                    media_type = msg.get('media_type') or 'Media'
                    text = f"[{media_type}]"
                text = str(text)[:70]
                
                self.stdout.write(
                    f"  [{date}] {sender}: {text}"
                )
            
            if len(messages) > 20:
                self.stdout.write(f"  ... and {len(messages) - 20} more messages")
        
        self.stdout.write("\n" + "=" * 100 + "\n")
    
    def _print_json(self, history_data):
        """Print message history as JSON"""
        output = {
            'total_chats': len(history_data),
            'total_messages': sum(item['message_count'] for item in history_data),
            'history': []
        }
        
        for item in history_data:
            dialog = item['dialog']
            output['history'].append({
                'dialog': dialog,
                'messages': item['messages'],
                'message_count': item['message_count']
            })
        
        self.stdout.write(json.dumps(output, indent=2, ensure_ascii=False, default=str))

