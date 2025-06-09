from math import sqrt
from collections import deque

class Node:
    """Represents a single Meshtastic device with realistic message handling"""
    
    def __init__(self, node_id, x, y):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.neighbors = []  # List of node IDs this node can communicate with directly
        
        # Message handling - IMPROVED
        self.received_messages = set()  # Message IDs that this node already processed
        self.message_queue = deque()    # Queue of messages waiting to be processed
        self.currently_processing = None  # Message currently being processed
        self.is_busy = False           # Whether node is currently processing a message
        
        # Legacy support (keep for compatibility)
        self.sent_messages = set()     # For compatibility with existing code
        self.routing_table = {}        # destination_id -> next_hop_id  
        self.is_active = True          # Whether this node is active
    
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
    
    def receive_message(self, message):
        """
        Receive a message from a neighbor.
        
        Returns:
            bool: True if message was accepted, False if already seen
        """
        # Check if we already processed this message
        if message.message_id in self.received_messages:
            print(f"   🔄 Node {self.node_id}: Already seen message {message.message_id}, ignoring")
            return False
        
        # Add to queue for processing
        self.message_queue.append(message.copy())
        print(f"   📥 Node {self.node_id}: Queued message {message.message_id} (queue size: {len(self.message_queue)})")
        return True
    
    def can_process_message(self):
        """Check if node can process a message (not busy and has messages in queue)"""
        return not self.is_busy and len(self.message_queue) > 0
    
    def start_processing_next_message(self):
        """
        Start processing the next message in queue.
        
        Returns:
            Message or None: The message being processed, or None if no messages
        """
        if not self.can_process_message():
            return None
        
        # Take next message from queue
        self.currently_processing = self.message_queue.popleft()
        self.is_busy = True
        
        # Mark as received/processed
        self.received_messages.add(self.currently_processing.message_id)
        self.sent_messages.add(self.currently_processing.message_id)  # Legacy compatibility
        
        print(f"   🔧 Node {self.node_id}: Started processing message {self.currently_processing.message_id}")
        return self.currently_processing
    
    def finish_processing(self):
        """
        Finish processing current message.
        
        Returns:
            list: List of neighbor IDs to forward the message to
        """
        if not self.is_busy or self.currently_processing is None:
            return []
        
        message = self.currently_processing
        neighbors_to_forward = []
        
        # Check if this is the destination
        if message.destination == self.node_id:
            print(f"   🎯 Node {self.node_id}: Message {message.message_id} reached destination!")
            self.is_busy = False
            self.currently_processing = None
            return []  # Don't forward - message delivered
        
        # Forward to all neighbors (flooding algorithm)
        neighbors_to_forward = self.neighbors.copy()
        
        print(f"   📤 Node {self.node_id}: Finished processing, will forward to {len(neighbors_to_forward)} neighbors")
        
        # Reset processing state
        self.is_busy = False
        self.currently_processing = None
        
        return neighbors_to_forward
    
    def get_queue_status(self):
        """Get current queue status for debugging"""
        status = {
            'queue_size': len(self.message_queue),
            'is_busy': self.is_busy,
            'processing': self.currently_processing.message_id if self.currently_processing else None,
            'received_count': len(self.received_messages)
        }
        return status
    
    # Legacy methods for compatibility
    def has_seen_message(self, message_id):
        """Check if this node has already processed this message"""
        return message_id in self.received_messages
    
    def mark_message_as_sent(self, message_id):
        """Mark message as already processed (for legacy compatibility)"""
        self.received_messages.add(message_id)
        self.sent_messages.add(message_id)
    
    def add_message_to_queue(self, message):
        """Add message to processing queue (legacy compatibility)"""
        return self.receive_message(message)
    
    def get_next_message(self):
        """Get next message from queue (legacy compatibility)"""
        if self.message_queue:
            return self.message_queue.popleft()
        return None
    
    def __str__(self):
        return f"Node {self.node_id} at ({self.x:.1f}, {self.y:.1f}) with {len(self.neighbors)} neighbors (Queue: {len(self.message_queue)}, Busy: {self.is_busy})"