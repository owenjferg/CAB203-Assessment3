#Owen Ferguson 
#n11595744
#CAB203 Assesment 3 - FSA Task

import re

class ChatState:
    #represents the current state of the chat connection
    def __init__(self):
        self.mode = 'command'  # Initial mode is command
        self.current_channel = None
        self.current_user = None
    
    def to_dict(self):
        #convert state to dictionary format for return
        return {
            'mode': self.mode,
            'current_channel': self.current_channel,
            'current_user': self.current_user
        }
    
    @classmethod
    def from_dict(cls, state_dict):
        #create state from dictionary
        if state_dict is None:
            return cls()
        
        state = cls()
        state.mode = state_dict.get('mode', 'command')
        state.current_channel = state_dict.get('current_channel')
        state.current_user = state_dict.get('current_user')
        return state
    
    def enter_command_mode(self):
        self.mode = 'command'
        self.current_channel = None
        self.current_user = None
    
    def enter_channel_mode(self, channel):
        self.mode = 'channel'
        self.current_channel = channel
        self.current_user = None
    
    def enter_dm_mode(self, user):
        self.mode = 'dm'
        self.current_user = user
        self.current_channel = None

def is_valid_channel(channel):
    #checks if a channel is valid, by starting with #, followed by letters and numbers, must being with a letter
    if not channel.startswith('#'):
        return False
    
    # text after #
    name = channel[1:]
    
    # empty/doesnt start with a letter
    if not name or not name[0].isalpha():
        return False
    
    return all(c.isalnum() for c in name)

def is_valid_username(username):
    #must start with @ and be a valid email
    if not username.startswith('@'):
        return False
    
    # part after @
    email = username[1:]
    
    # Email pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def extract_mentions(message):
    #finds all valid @usernames in a message and returns them as a set
    words = message.split()
    return {word for word in words if word.startswith('@') and is_valid_username(word)}

def get_action(current_state, message):
    # Handle commands
    if message.startswith('\\'):
        parts = message[1:].split(' ', 1)
        command = parts[0].lower()
        if current_state.mode == 'command':
            if command == 'list' and len(parts) > 1:
                spec = parts[1]
                if spec in ['channels', 'users']:
                    return {'action': 'list', 'param': spec}
            elif command == 'quit':
                return {'action': 'quit'}
            elif command == 'join' and len(parts) > 1:
                channel = parts[1]
                if is_valid_channel(channel):
                    return {'action': 'join', 'channel': channel}
            elif command == 'dm' and len(parts) > 1:
                username = parts[1]
                if is_valid_username(username):
                    return {'action': 'dm', 'user': username}
        elif current_state.mode == 'channel':
            if command == 'leave':
                return {'action': 'leaveChannel', 'channel': current_state.current_channel}
            elif command == 'read':
                return {'action': 'readChannel', 'channel': current_state.current_channel}
        elif current_state.mode == 'dm':
            if command == 'leave':
                return {'action': 'leaveDM', 'user': current_state.current_user}
            elif command == 'read':
                return {'action': 'readDM', 'user': current_state.current_user}
    else:
        mentions = extract_mentions(message)
        if current_state.mode == 'channel':
            return {
                'action': 'postChannel',
                'channel': current_state.current_channel,
                'message': message,
                'mentions': mentions
            }
        elif current_state.mode == 'dm':
            return {
                'action': 'postDM',
                'user': current_state.current_user,
                'message': message,
                'mentions': mentions
            }
    return {'error': 'Invalid command'}

def get_next_state(current_state, message):
    #determines the next state based on current state and user input
    if message.startswith('\\'):
        parts = message[1:].split(' ', 1)
        command = parts[0].lower()
        
        # Command mode transitions
        if current_state.mode == 'command':
            if command == 'join' and len(parts) > 1:
                channel = parts[1]
                if is_valid_channel(channel):
                    current_state.enter_channel_mode(channel)
            elif command == 'dm' and len(parts) > 1:
                username = parts[1]
                if is_valid_username(username):
                    current_state.enter_dm_mode(username)
        
        # Channel mode transitions
        elif current_state.mode == 'channel':
            if command == 'leave':
                current_state.enter_command_mode()
        
        # DM mode transitions
        elif current_state.mode == 'dm':
            if command == 'leave':
                current_state.enter_command_mode()
    
    return current_state

def reChatParseCommand(message, state):
    # Handle initial connection before any state conversion
    if message == '' and state is None:
        return {'action': 'greeting'}, {'mode': 'command', 'current_channel': None, 'current_user': None}
    chat_state = ChatState.from_dict(state)
    action = get_action(chat_state, message)
    if 'error' not in action:
        chat_state = get_next_state(chat_state, message)
    return action, chat_state.to_dict()

