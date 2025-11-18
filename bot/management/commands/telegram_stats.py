from django.core.management.base import BaseCommand
from bot.telegram_client import get_telegram_client


class Command(BaseCommand):
    help = 'Show Telegram account statistics (contacts, chats, channels, groups)'

    def handle(self, *args, **options):
        client = get_telegram_client()
        
        if not client.is_configured():
            self.stdout.write(
                self.style.ERROR('Telegram client is not properly configured. Please check your .env file.')
            )
            return
        
        # Check if phone number is set (required for statistics)
        if not client.phone_number:
            self.stdout.write(
                self.style.ERROR(
                    '\n⚠️  ERROR: To get statistics, you need to use a USER account, not a bot account.\n'
                    'Bots cannot access dialogs due to Telegram API restrictions.\n\n'
                    'Please add to your .env file:\n'
                    'TELEGRAM_PHONE_NUMBER=+1234567890  (your phone number with country code)\n\n'
                    'Example: TELEGRAM_PHONE_NUMBER=+998901234567\n\n'
                    'Note: On first run, Telethon will ask for a verification code sent to your phone.'
                )
            )
            return
        
        self.stdout.write(self.style.SUCCESS('Connecting as user account...'))
        self.stdout.write(self.style.WARNING('Note: If this is your first time, you may be asked for a verification code.'))
        
        # Get statistics
        stats = client.get_statistics()
        
        if not stats:
            self.stdout.write(self.style.WARNING('Could not retrieve statistics.'))
            return
        
        # Display statistics
        self._print_statistics(stats)
    
    def _print_statistics(self, stats):
        """Print comprehensive statistics"""
        self.stdout.write("\n" + "=" * 70)
        self.stdout.write(self.style.SUCCESS("📊 Telegram Account Statistics"))
        self.stdout.write("=" * 70)
        
        # Chats & Contacts Section
        self.stdout.write("\n" + self.style.SUCCESS("💬 Chats & Contacts:"))
        self.stdout.write(f"  📱 Private Chats:     {stats.get('chats', 0):>4}")
        self.stdout.write(f"  👤 Contacts:          {stats.get('contacts', 0):>4}")
        
        # Channels & Groups Section
        self.stdout.write("\n" + self.style.SUCCESS("📢 Channels & Groups:"))
        channels = stats.get('channels', 0)
        supergroups = stats.get('supergroups', 0)
        groups = stats.get('groups', 0)
        total_channels_groups = channels + supergroups + groups
        
        if total_channels_groups > 0:
            self.stdout.write(f"  📢 Channels:          {channels:>4}")
            self.stdout.write(f"  👥 Supergroups:      {supergroups:>4}")
            self.stdout.write(f"  💬 Groups:           {groups:>4}")
            self.stdout.write("  " + "-" * 66)
            self.stdout.write(f"  {'Total Channels/Groups':<20} {total_channels_groups:>4}")
        
        # Overall Summary
        total_dialogs = stats.get('total_dialogs', 0)
        if total_dialogs > 0:
            self.stdout.write("\n" + self.style.SUCCESS("📊 Overall Summary:"))
            self.stdout.write(f"  Total Dialogs:        {total_dialogs:>4}")
            
            # Calculate percentages
            if total_dialogs > 0:
                chats_pct = (stats.get('chats', 0) / total_dialogs) * 100
                channels_pct = (channels / total_dialogs) * 100
                supergroups_pct = (supergroups / total_dialogs) * 100
                groups_pct = (groups / total_dialogs) * 100
                
                self.stdout.write("\n" + self.style.SUCCESS("📈 Distribution:"))
                self.stdout.write(f"  Private Chats:        {chats_pct:>5.1f}%")
                self.stdout.write(f"  Channels:             {channels_pct:>5.1f}%")
                self.stdout.write(f"  Supergroups:          {supergroups_pct:>5.1f}%")
                self.stdout.write(f"  Groups:               {groups_pct:>5.1f}%")
        
        self.stdout.write("=" * 70 + "\n")

