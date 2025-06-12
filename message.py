import random

class Message:
    """
    Represents a message in the network simulation
    Each message has: ID, source, destination, hop limit, and start frame
    """
    
    def __init__(self, message_id, source_node, target_node, total_frames):
        self.id = message_id
        self.source = source_node  # Source node ID
        self.target = target_node  # Target node ID
        
        # Random hop limit between 3-6
        self.hop_limit = random.randint(3, 6)
        
        # Random start frame (when the message begins transmission)
        self.start_frame = random.randint(0, total_frames - 1)
        
        # Current hop count (starts at hop_limit)
        self.current_hops = self.hop_limit
        
        # Message status
        self.is_active = False  # Not started yet
        self.is_completed = False  # Reached destination or expired
        self.completion_reason = None  # "reached_target" or "hop_limit_exceeded"
        
        # Track multiple message paths (flooding creates multiple routes)
        self.paths = []  # List of paths - each path is a list of node IDs
        self.active_copies = {}  # Dictionary: node_id -> path_to_that_node
        
    def start_transmission(self):
        """Mark message as active and initialize first path from source"""
        self.is_active = True
        initial_path = [self.source]
        self.paths.append(initial_path)
        self.active_copies[self.source] = initial_path.copy()
        
    def decrease_hop(self):
        """Decrease hop count by 1"""
        self.current_hops -= 1
        
    def complete_message(self, reason):
        """Mark message as completed with reason"""
        self.is_completed = True
        self.is_active = False
        self.completion_reason = reason
        
    def create_new_copy(self, current_node, next_node, current_path):
        """Create a new copy of the message for flooding to neighbor"""
        new_path = current_path.copy()
        new_path.append(next_node)
        
        # Add new path if it's unique
        if new_path not in self.paths:
            self.paths.append(new_path)
            
        # Update active copy for this node
        self.active_copies[next_node] = new_path
        
        return new_path
        
    def get_routing_table_data(self):
        """Extract routing information for building routing tables"""
        routing_info = {}
        
        for path in self.paths:
            if len(path) < 2:
                continue
                
            # For each node in path, record how to reach the source
            for i in range(1, len(path)):
                current_node = path[i]
                previous_node = path[i-1]
                
                # This tells us: from current_node, to reach source, go via previous_node
                if current_node not in routing_info:
                    routing_info[current_node] = {}
                    
                routing_info[current_node][self.source] = {
                    'next_hop': previous_node,
                    'distance': i,
                    'full_path': path[:i+1]
                }
                
        return routing_info
            
    def __str__(self):
        """String representation of the message"""
        status = "Completed" if self.is_completed else ("Active" if self.is_active else "Waiting")
        return f"Msg {self.id}: {self.source}→{self.target} | Hops: {self.current_hops}/{self.hop_limit} | Frame: {self.start_frame} | Status: {status}"