from django.core.management.base import BaseCommand
from bot.telegram_client import get_telegram_client
import json


class Command(BaseCommand):
    help = 'List all joined channels and groups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--format',
            type=str,
            default='table',
            choices=['table', 'json', 'simple'],
            help='Output format: table, json, or simple'
        )
        parser.add_argument(
            '--type',
            type=str,
            choices=['channel', 'supergroup', 'group', 'all'],
            default='all',
            help='Filter by type: channel, supergroup, group, or all'
        )

    def handle(self, *args, **options):
        output_format = options['format']
        filter_type = options['type']
        
        client = get_telegram_client()
        
        if not client.is_configured():
            self.stdout.write(
                self.style.ERROR('Telegram client is not properly configured. Please check your .env file.')
            )
            return
        
        # Check if phone number is set (required for listing channels)
        if not client.phone_number:
            self.stdout.write(
                self.style.ERROR(
                    '\n⚠️  ERROR: To list channels, you need to use a USER account, not a bot account.\n'
                    'Bots cannot list dialogs/channels due to Telegram API restrictions.\n\n'
                    'Please add to your .env file:\n'
                    'TELEGRAM_PHONE_NUMBER=+1234567890  (your phone number with country code)\n\n'
                    'Example: TELEGRAM_PHONE_NUMBER=+998901234567\n\n'
                    'Note: On first run, Telethon will ask for a verification code sent to your phone.'
                )
            )
            return
        
        self.stdout.write(self.style.SUCCESS('Connecting as user account...'))
        self.stdout.write(self.style.WARNING('Note: If this is your first time, you may be asked for a verification code.'))
        
        channels = client.get_joined_channels()
        
        if not channels:
            self.stdout.write(self.style.WARNING('No channels or groups found.'))
            return
        
        # Calculate counts by type
        counts = {}
        for channel in channels:
            ch_type = channel['type']
            counts[ch_type] = counts.get(ch_type, 0) + 1
        
        # Filter by type if specified
        if filter_type != 'all':
            channels = [ch for ch in channels if ch['type'] == filter_type]
        
        # Show statistics
        self._print_statistics(counts, filter_type)
        
        if output_format == 'json':
            self.stdout.write(json.dumps(channels, indent=2, ensure_ascii=False))
        elif output_format == 'simple':
            for channel in channels:
                username = f"@{channel['username']}" if channel['username'] else "No username"
                self.stdout.write(f"{channel['type'].upper()}: {channel['title']} ({username})")
        else:  # table format
            self._print_table(channels)
        
        self.stdout.write(
            self.style.SUCCESS(f'\nTotal: {len(channels)} {"item" if len(channels) == 1 else "items"} found')
        )
    
    def _print_statistics(self, counts, filter_type):
        """Print statistics by type for channels and groups"""
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS("📊 Statistics by Type"))
        self.stdout.write("=" * 60)
        
        total = sum(counts.values())
        
        type_labels = {
            'channel': '📢 Channels',
            'supergroup': '👥 Supergroups',
            'group': '💬 Groups'
        }
        
        for ch_type, label in type_labels.items():
            count = counts.get(ch_type, 0)
            if count > 0:
                percentage = (count / total * 100) if total > 0 else 0
                bar = '█' * int(percentage / 2)  # Visual bar
            
                if filter_type == 'all' or filter_type == ch_type:
                    self.stdout.write(
                        f"{label:<20} {count:>4} ({percentage:>5.1f}%) {bar}"
                    )
        
        self.stdout.write("=" * 60)
        self.stdout.write(f"{'Total':<20} {total:>4} (100.0%)")
        self.stdout.write("=" * 60 + "\n")
    
    def _print_table(self, channels):
        """Print channels in a formatted table"""
        self.stdout.write("\n" + "=" * 100)
        self.stdout.write(f"{'Type':<10} {'Title':<40} {'Username':<25} {'ID':<15} {'Members':<10}")
        self.stdout.write("=" * 100)
        
        for channel in channels:
            channel_type = channel['type'].upper()
            title = channel['title'][:38] + '..' if len(channel['title']) > 40 else channel['title']
            username = f"@{channel['username']}" if channel['username'] else "N/A"
            channel_id = str(channel['id'])
            members = str(channel['participants_count']) if channel['participants_count'] else "N/A"
            
            self.stdout.write(
                f"{channel_type:<10} {title:<40} {username:<25} {channel_id:<15} {members:<10}"
            )
        
        self.stdout.write("=" * 100)

