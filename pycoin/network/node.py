from .protocol import Message
import pythonp2p
import logging

logger = logging.getLogger('pycoin')

class Node(pythonp2p.Node):
    def on_message(self, data, sender, private):
        message = Message.model_validate(data)
        logger.debug(f'Received command {message.command} from {sender}')

        action = getattr(self, f'command_{message.command}')
        action(**message.payload)
    
    def command_ping(self, stream: str):
        logger.debug(stream)
    
    def command_block(self):
        logger.debug(f'Command Block!')
