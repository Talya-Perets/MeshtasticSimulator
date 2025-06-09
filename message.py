import uuid
import time

class Message:
    """Represents a message sent through the network"""
    
    def __init__(self, source, destination, content="", hop_limit=30, start_time=0):
        self.message_id = str(uuid.uuid4())[:8]  # Short message ID
        self.source = source
        self.destination = destination
        self.content = content
        self.hop_limit = hop_limit
        self.current_hop_count = 0
        self.path = [source]  # List of node IDs the message passed through
        self.creation_time = time.time()
        self.start_time = start_time  # Simulation time when message should start
        self.arrival_time = None
        self.reached_destination = False
        self.current_node = source
        self.next_hops = []  # For visualization - nodes that will receive in next step
        self.failed = False
        self.failure_reason = ""
        self.active = False  # Whether message is currently active in simulation
        self.received_from = None  # NEW: Track who sent this message to current node
    
    def add_to_path(self, node_id, sender_id=None):
        """Add node to message path and track sender"""
        self.path.append(node_id)
        self.current_node = node_id
        self.current_hop_count += 1
        self.received_from = sender_id  # Track who sent this message
    
    def can_hop(self):
        """Check if message can still hop"""
        return self.current_hop_count < self.hop_limit and not self.failed and self.active
    
    def set_next_hops(self, node_ids):
        """Set nodes that will receive this message in next step"""
        self.next_hops = node_ids.copy()
    
    def mark_as_arrived(self):
        """Mark message as successfully arrived"""
        self.reached_destination = True
        self.arrival_time = time.time()
        self.active = False
    
    def mark_as_failed(self, reason):
        """Mark message as failed"""
        self.failed = True
        self.failure_reason = reason
        self.active = False
    
    def activate(self):
        """Activate message for transmission"""
        self.active = True
    
    def get_delivery_time(self):
        """Get delivery time in seconds"""
        if self.arrival_time:
            return self.arrival_time - self.creation_time
        return None
    
    def get_status(self):
        """Get current message status"""
        if self.reached_destination:
            return "DELIVERED"
        elif self.failed:
            return f"FAILED: {self.failure_reason}"
        elif not self.can_hop():
            return "EXPIRED"
        elif not self.active:
            return "WAITING"
        else:
            return "IN_TRANSIT"
    
    def get_full_path_info(self):
        """Get detailed path information including senders"""
        if len(self.path) <= 1:
            return f"At source: {self.source}"
        
        path_info = f"{self.source}"
        for i in range(1, len(self.path)):
            path_info += f" -> {self.path[i]}"
        
        if self.received_from is not None and self.current_node != self.source:
            path_info += f" (from {self.received_from})"
        
        return path_info
    
    def copy(self):
        """Create a copy of this message for forwarding."""
        new_msg = Message(self.source, self.destination, self.content, self.hop_limit, self.start_time)
        new_msg.message_id = self.message_id  # Keep same ID
        new_msg.current_hop_count = self.current_hop_count
        new_msg.path = self.path.copy()
        new_msg.active = self.active
        new_msg.received_from = self.received_from
        return new_msg
    
    def __str__(self):
        return f"Message {self.message_id}: {self.source} -> {self.destination} (Hops: {self.current_hop_count}/{self.hop_limit})"