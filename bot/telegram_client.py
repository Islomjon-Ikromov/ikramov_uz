"""
Telegram Client Configuration and Setup using Telethon
"""
from telethon import TelegramClient as TelethonClient
from decouple import config
import logging
import asyncio

logger = logging.getLogger(__name__)


class TelegramClient:
    """
    Telegram Bot Client with configuration settings using Telethon
    Reads settings directly from .env file
    """
    
    def __init__(self):
        """
        Initialize Telegram client with settings from .env file
        """
        # Read required settings from .env file
        self.api_id = config('TELEGRAM_API_ID', default='', cast=int)
        self.api_hash = config('TELEGRAM_API_HASH', default='')
        self.bot_token = config('TELEGRAM_BOT_TOKEN', default='')
        self.phone_number = config('TELEGRAM_PHONE_NUMBER', default='')
        self.admin_id = config('TELEGRAM_ADMIN_ID', default='739089730')
        self.webhook_url = config('TELEGRAM_WEBHOOK_URL', default='https://ikramov.uz/bot/update/')
        self.session_name = config('TELEGRAM_SESSION_NAME', default='bot_session')
        self.user_session_name = config('TELEGRAM_USER_SESSION_NAME', default='user_session')
        self.use_user_account = config('TELEGRAM_USE_USER_ACCOUNT', default=False, cast=bool)
        
        self.client = None
        self.user_client = None
        
        # Validate configuration
        self._validate_settings()
    
    def _validate_settings(self):
        """
        Validate that all required settings are configured in .env file
        """
        if not self.api_id:
            logger.warning("TELEGRAM_API_ID is not set in .env file")
        
        if not self.api_hash:
            logger.warning("TELEGRAM_API_HASH is not set in .env file")
        
        if not self.bot_token:
            logger.warning("TELEGRAM_BOT_TOKEN is not set in .env file")
        
        if not self.admin_id:
            logger.warning("TELEGRAM_ADMIN_ID is not set in .env file")
        
        if not self.webhook_url:
            logger.warning("TELEGRAM_WEBHOOK_URL is not set in .env file")
    
    def get_client(self, use_user_account=False):
        """
        Get or create Telethon client instance
        If use_user_account is True, returns a separate user client
        """
        if not self.api_id or not self.api_hash:
            logger.error("Cannot create client: TELEGRAM_API_ID or TELEGRAM_API_HASH is not configured")
            return None
        
        if use_user_account:
            # Use separate client for user account operations
            if not self.user_client:
                try:
                    self.user_client = TelethonClient(
                        self.user_session_name,
                        self.api_id,
                        self.api_hash
                    )
                    logger.info("Telethon user client initialized successfully")
                except Exception as e:
                    logger.error(f"Error initializing Telethon user client: {str(e)}")
                    return None
            return self.user_client
        else:
            # Use bot client
            if not self.client:
                try:
                    self.client = TelethonClient(
                        self.session_name,
                        self.api_id,
                        self.api_hash
                    )
                    logger.info("Telethon bot client initialized successfully")
                except Exception as e:
                    logger.error(f"Error initializing Telethon bot client: {str(e)}")
                    return None
            return self.client
    
    async def connect_client(self, use_user_account=None):
        """
        Connect the Telethon client
        If use_user_account is True, connects as user (for listing channels)
        If False or None, uses bot_token (for sending messages)
        """
        use_user = use_user_account if use_user_account is not None else self.use_user_account
        
        # Get the appropriate client (user or bot)
        client = self.get_client(use_user_account=use_user)
        if not client:
            return False
        
        try:
            if use_user and self.phone_number:
                # Connect as user account (required for listing channels)
                # Use a separate session to avoid conflicts with bot session
                await client.start(phone=self.phone_number)
                logger.info("Telethon client connected as user account")
            elif self.bot_token:
                # Connect as bot (for sending messages)
                await client.start(bot_token=self.bot_token)
                logger.info("Telethon client connected as bot")
            else:
                logger.error("No phone number or bot token provided")
                return False
            
            return True
        except Exception as e:
            logger.error(f"Error connecting Telethon client: {str(e)}")
            return False
    
    async def send_message_async(self, chat_id, message_text):
        """
        Send a message asynchronously
        """
        try:
            client = self.get_client()
            if not client:
                return False
            
            if not client.is_connected():
                await self.connect_client()
            
            await client.send_message(chat_id, message_text)
            logger.info(f"Message sent to {chat_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return False
    
    def send_message(self, chat_id, message_text):
        """
        Send a message synchronously (wrapper for async method)
        """
        try:
            client = self.get_client()
            if not client:
                return False
            
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run async function
            return loop.run_until_complete(self.send_message_async(chat_id, message_text))
        except Exception as e:
            logger.error(f"Error in send_message: {str(e)}")
            return False
    
    def get_admin_id(self):
        """
        Get admin ID as integer
        """
        try:
            return int(self.admin_id)
        except (ValueError, TypeError):
            logger.error(f"Invalid admin ID: {self.admin_id}")
            return None
    
    def get_webhook_url(self):
        """
        Get webhook URL
        """
        return self.webhook_url
    
    def is_configured(self):
        """
        Check if all required settings are configured
        """
        return all([
            self.api_id,
            self.api_hash,
            self.bot_token,
            self.admin_id,
            self.webhook_url
        ])
    
    async def get_joined_channels_async(self):
        """
        Get all joined channels and groups asynchronously
        Returns a list of dictionaries with channel information
        NOTE: Requires user account (phone number), not bot token
        """
        try:
            # Use separate user client to avoid session conflicts
            client = self.get_client(use_user_account=True)
            if not client:
                return []
            
            # Disconnect if already connected (might be from previous operation)
            if client.is_connected():
                await client.disconnect()
            
            # Must use user account to list channels (bots can't do this)
            if not await self.connect_client(use_user_account=True):
                logger.error("Failed to connect as user account. Make sure TELEGRAM_PHONE_NUMBER is set in .env")
                return []
            
            channels_list = []
            
            # Get all dialogs (chats, groups, channels, supergroups)
            async for dialog in client.iter_dialogs():
                # Filter for channels, supergroups, and groups
                if dialog.is_channel or dialog.is_group:
                    # Determine the type more accurately
                    is_broadcast = getattr(dialog.entity, 'broadcast', False)
                    is_megagroup = getattr(dialog.entity, 'megagroup', False)
                    
                    if dialog.is_channel:
                        if is_broadcast:
                            dialog_type = 'channel'  # Broadcast channel
                        elif is_megagroup:
                            dialog_type = 'supergroup'  # Supergroup (megagroup)
                        else:
                            dialog_type = 'supergroup'  # Supergroup (default for channels that aren't broadcast)
                    else:
                        dialog_type = 'group'  # Regular group
                    
                    channel_info = {
                        'id': dialog.id,
                        'title': dialog.title,
                        'username': dialog.entity.username if hasattr(dialog.entity, 'username') else None,
                        'type': dialog_type,
                        'participants_count': getattr(dialog.entity, 'participants_count', None),
                        'unread_count': dialog.unread_count,
                        'is_verified': getattr(dialog.entity, 'verified', False),
                        'is_broadcast': is_broadcast,
                        'is_megagroup': is_megagroup,
                    }
                    channels_list.append(channel_info)
            
            logger.info(f"Found {len(channels_list)} channels/supergroups/groups")
            return channels_list
            
        except Exception as e:
            logger.error(f"Error getting joined channels: {str(e)}")
            return []
    
    def get_joined_channels(self):
        """
        Get all joined channels and groups synchronously
        """
        try:
            client = self.get_client()
            if not client:
                return []
            
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run async function
            return loop.run_until_complete(self.get_joined_channels_async())
        except Exception as e:
            logger.error(f"Error in get_joined_channels: {str(e)}")
            return []
    
    async def get_all_dialogs_async(self):
        """
        Get all dialogs (chats, groups, channels) asynchronously
        NOTE: Requires user account (phone number), not bot token
        """
        try:
            # Use separate user client to avoid session conflicts
            client = self.get_client(use_user_account=True)
            if not client:
                return []
            
            # Disconnect if already connected (might be from previous operation)
            if client.is_connected():
                await client.disconnect()
            
            # Must use user account to list dialogs (bots can't do this)
            if not await self.connect_client(use_user_account=True):
                logger.error("Failed to connect as user account. Make sure TELEGRAM_PHONE_NUMBER is set in .env")
                return []
            
            dialogs_list = []
            
            async for dialog in client.iter_dialogs():
                # Determine the type more accurately
                if dialog.is_channel:
                    is_broadcast = getattr(dialog.entity, 'broadcast', False)
                    is_megagroup = getattr(dialog.entity, 'megagroup', False)
                    if is_broadcast:
                        dialog_type = 'channel'  # Broadcast channel
                    elif is_megagroup:
                        dialog_type = 'supergroup'  # Supergroup (megagroup)
                    else:
                        dialog_type = 'supergroup'  # Supergroup (default for channels that aren't broadcast)
                elif dialog.is_group:
                    dialog_type = 'group'  # Regular group
                else:
                    dialog_type = 'user'  # Private chat
                
                dialog_info = {
                    'id': dialog.id,
                    'title': dialog.title,
                    'name': dialog.name,
                    'username': dialog.entity.username if hasattr(dialog.entity, 'username') else None,
                    'type': dialog_type,
                    'unread_count': dialog.unread_count,
                    'is_verified': getattr(dialog.entity, 'verified', False),
                    'is_broadcast': getattr(dialog.entity, 'broadcast', False),
                    'is_megagroup': getattr(dialog.entity, 'megagroup', False),
                }
                dialogs_list.append(dialog_info)
            
            logger.info(f"Found {len(dialogs_list)} dialogs")
            return dialogs_list
            
        except Exception as e:
            logger.error(f"Error getting all dialogs: {str(e)}")
            return []
    
    def get_all_dialogs(self):
        """
        Get all dialogs synchronously
        """
        try:
            client = self.get_client()
            if not client:
                return []
            
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run async function
            return loop.run_until_complete(self.get_all_dialogs_async())
        except Exception as e:
            logger.error(f"Error in get_all_dialogs: {str(e)}")
            return []
    
    async def get_statistics_async(self):
        """
        Get statistics about contacts, chats, channels, groups, etc.
        Returns a dictionary with counts
        """
        try:
            # Use separate user client to avoid session conflicts
            client = self.get_client(use_user_account=True)
            if not client:
                return {}
            
            # Disconnect if already connected
            if client.is_connected():
                await client.disconnect()
            
            # Must use user account
            if not await self.connect_client(use_user_account=True):
                logger.error("Failed to connect as user account. Make sure TELEGRAM_PHONE_NUMBER is set in .env")
                return {}
            
            stats = {
                'channels': 0,
                'supergroups': 0,
                'groups': 0,
                'chats': 0,  # Private chats
                'contacts': 0,
                'total_dialogs': 0
            }
            
            async for dialog in client.iter_dialogs():
                stats['total_dialogs'] += 1
                
                if dialog.is_channel:
                    is_broadcast = getattr(dialog.entity, 'broadcast', False)
                    is_megagroup = getattr(dialog.entity, 'megagroup', False)
                    if is_broadcast:
                        stats['channels'] += 1
                    else:
                        stats['supergroups'] += 1
                elif dialog.is_group:
                    stats['groups'] += 1
                else:
                    # Private chat
                    stats['chats'] += 1
                    # Check if it's a contact (has phone number or is saved contact)
                    if hasattr(dialog.entity, 'phone'):
                        stats['contacts'] += 1
            
            logger.info(f"Statistics collected: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {}
    
    def get_statistics(self):
        """
        Get statistics synchronously
        """
        try:
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run async function
            return loop.run_until_complete(self.get_statistics_async())
        except Exception as e:
            logger.error(f"Error in get_statistics: {str(e)}")
            return {}
    
    async def get_current_user_id_async(self):
        """
        Get current user's ID
        """
        try:
            client = self.get_client(use_user_account=True)
            if not client:
                return None
            
            if not client.is_connected():
                await self.connect_client(use_user_account=True)
            
            me = await client.get_me()
            return me.id if me else None
        except Exception as e:
            logger.error(f"Error getting current user ID: {str(e)}")
            return None
    
    def get_current_user_id(self):
        """
        Get current user's ID synchronously
        """
        try:
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            return loop.run_until_complete(self.get_current_user_id_async())
        except Exception as e:
            logger.error(f"Error in get_current_user_id: {str(e)}")
            return None
    
    async def get_messages_async(self, peer_id, limit=100, offset_id=0, from_user_only=False):
        """
        Get messages from a specific peer (user/chat/channel)
        If from_user_only is True, only returns messages sent by the current user
        """
        try:
            # Use separate user client
            client = self.get_client(use_user_account=True)
            if not client:
                return []
            
            # Disconnect if already connected
            if client.is_connected():
                await client.disconnect()
            
            # Must use user account
            if not await self.connect_client(use_user_account=True):
                logger.error("Failed to connect as user account. Make sure TELEGRAM_PHONE_NUMBER is set in .env")
                return []
            
            # Get current user ID if filtering
            current_user_id = None
            if from_user_only:
                current_user_id = await self.get_current_user_id_async()
                if not current_user_id:
                    logger.warning("Could not get current user ID, cannot filter by user")
            
            messages_list = []
            
            # Prepare parameters for iter_messages
            kwargs = {'limit': limit}
            if offset_id and offset_id > 0:
                kwargs['offset_id'] = offset_id
            
            # Get messages
            async for message in client.iter_messages(peer_id, **kwargs):
                # Filter by sender if requested
                if from_user_only and current_user_id:
                    if message.sender_id != current_user_id:
                        continue
                # Extract message information
                msg_info = {
                    'id': message.id,
                    'date': message.date.isoformat() if message.date else None,
                    'text': message.text or '',
                    'sender_id': message.sender_id,
                    'sender_name': None,
                    'is_reply': message.is_reply,
                    'reply_to_msg_id': message.reply_to.reply_to_msg_id if message.reply_to else None,
                    'media_type': None,
                    'has_media': message.media is not None,
                }
                
                # Get sender name
                if message.sender:
                    if hasattr(message.sender, 'first_name'):
                        sender_name = message.sender.first_name
                        if hasattr(message.sender, 'last_name') and message.sender.last_name:
                            sender_name += f" {message.sender.last_name}"
                        msg_info['sender_name'] = sender_name
                    elif hasattr(message.sender, 'title'):
                        msg_info['sender_name'] = message.sender.title
                    elif hasattr(message.sender, 'username'):
                        msg_info['sender_name'] = f"@{message.sender.username}"
                
                # Get media type if present
                if message.media:
                    media_type = type(message.media).__name__
                    msg_info['media_type'] = media_type.replace('MessageMedia', '').replace('_', ' ')
                
                messages_list.append(msg_info)
            
            logger.info(f"Retrieved {len(messages_list)} messages from peer {peer_id}")
            return messages_list
            
        except Exception as e:
            logger.error(f"Error getting messages: {str(e)}")
            return []
    
    def get_messages(self, peer_id, limit=100, offset_id=0, from_user_only=False):
        """
        Get messages synchronously
        If from_user_only is True, only returns messages sent by the current user
        """
        try:
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Run async function
            return loop.run_until_complete(self.get_messages_async(peer_id, limit, offset_id, from_user_only))
        except Exception as e:
            logger.error(f"Error in get_messages: {str(e)}")
            return []
    
    async def disconnect(self):
        """
        Disconnect the client
        """
        if self.client and self.client.is_connected():
            await self.client.disconnect()
            logger.info("Telethon client disconnected")


# Global client instance
_telegram_client = None


def get_telegram_client():
    """
    Get or create global Telegram client instance
    """
    global _telegram_client
    if _telegram_client is None:
        _telegram_client = TelegramClient()
    return _telegram_client


def get_client():
    """
    Convenience function to get Telethon client instance
    """
    telegram_client = get_telegram_client()
    return telegram_client.get_client()

