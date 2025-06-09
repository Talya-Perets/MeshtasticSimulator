from math import sqrt

class Node:
    """Represents a single Meshtastic device"""
    
    def __init__(self, node_id, x, y):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.neighbors = []  # List of node IDs this node can communicate with directly
        self.sent_messages = set()  # Message IDs that already passed through this node
        self.routing_table = {}  # destination_id -> next_hop_id
        self.message_queue = []  # Messages waiting to be processed
        self.is_active = True  # Whether this node is active
    
    def distance_from(self, other_node):
        """Calculate distance from another node"""
        return sqrt((self.x - other_node.x)**2 + (self.y - other_node.y)**2)
    
    def add_neighbor(self, neighbor_id):
        """Add a new neighbor"""
        if neighbor_id not in self.neighbors:
            self.neighbors.append(neighbor_id)
    
    def remove_neighbor(self, neighbor_id):
        """Remove a neighbor"""
        if neighbor_id in self.neighbors:
            self.neighbors.remove(neighbor_id)
    
    def has_seen_message(self, message_id):
        """Check if this node has already processed this message"""
        return message_id in self.sent_messages
    
    def mark_message_as_sent(self, message_id):
        """Mark message as already processed"""
        self.sent_messages.add(message_id)
    
    def add_message_to_queue(self, message):
        """Add message to processing queue"""
        self.message_queue.append(message)
    
    def get_next_message(self):
        """Get next message from queue"""
        if self.message_queue:
            return self.message_queue.pop(0)
        return None
    
    def __str__(self):
        return f"Node {self.node_id} at ({self.x:.1f}, {self.y:.1f}) with {len(self.neighbors)} neighbors"