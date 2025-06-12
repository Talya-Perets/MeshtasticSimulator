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
        self.hop_limit = 4
        
        # Better random start frame distribution
        # Start between frame 1 and 2/3 of total frames (give more time to complete)
        max_start_frame = max(1, int(total_frames * 0.67))  # Use 2/3 of total frames
        self.start_frame = random.randint(1, max_start_frame)
        
        # Current hop count (starts at hop_limit)
        self.current_hops = self.hop_limit
        
        # Message status
        self.is_active = False  # Not started yet
        self.is_completed = False  # Hop limit reached or manually stopped
        self.target_received = False  # Did target receive the message?
        self.completion_reason = None  # "hop_limit_exceeded" only
        
        # Status starts as FAILED, changes to SUCCESS when target receives
        self.status = "FAILED"  # SUCCESS or FAILED
        
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
        
    def target_reached(self):
        """Mark that target has received the message - change status to SUCCESS"""
        self.target_received = True
        self.status = "SUCCESS"  # Change status to SUCCESS
        print(f"      🎯 Message {self.id} TARGET REACHED - Status changed to SUCCESS")
        
    def complete_message(self, reason):
        """Mark message as completed"""
        if reason == "reached_target":
            # Target reached - mark as received but complete immediately
            self.target_received = True
            self.is_completed = True
            self.is_active = False
            self.completion_reason = reason
            print(f"      🎯 Message {self.id} COMPLETED: TARGET REACHED!")
        elif reason == "hop_limit_exceeded":
            # Hop limit exceeded - complete
            self.is_completed = True
            self.is_active = False
            self.completion_reason = reason
            print(f"      🛑 Message {self.id} COMPLETED: HOP LIMIT EXCEEDED")
            
    def get_state(self):
        """Get current state of the message"""
        if self.is_completed:
            return "COMPLETED"  # Message finished
        elif self.is_active:
            return "ACTIVE"  # Message is running
        else:
            return "WAITING"  # Message not started yet
    
    def get_status(self):
        """Get current status of the message"""
        return self.status  # Always return the current status (SUCCESS or FAILED)
        
    def create_new_copy(self, sender_id, receiver_id, sender_path):
        """Create a new copy of the message for flooding to neighbor
        
        Args:
            sender_id: The node that is sending the message
            receiver_id: The node that will receive the message  
            sender_path: The path the message took to reach the sender
            
        Returns:
            new_path: The new path including the receiver
        """
        # FIXED: Create new path correctly
        new_path = sender_path.copy()
        new_path.append(receiver_id)  # Add the receiver to the path
        
        # Add new path if it's unique
        if new_path not in self.paths:
            self.paths.append(new_path)
            print(f"        📍 New path discovered: {' → '.join(map(str, new_path))}")
            
        # Update active copy for this node
        self.active_copies[receiver_id] = new_path
        
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
        state = self.get_state()
        status_marker = ""
        if self.is_completed:
            # Add status when completed
            status_marker = f" | Status: {self.get_status()}"
        elif self.target_received:
            status_marker = " 🎯"
        return f"Msg {self.id}: {self.source}→{self.target} | Hops: {self.current_hops}/{self.hop_limit} | Frame: {self.start_frame} | State: {state}{status_marker}"