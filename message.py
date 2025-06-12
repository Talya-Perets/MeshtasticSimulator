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
        
        # Random start frame (when the message begins transmission)
        # Start between frame 1 and total_frames - 10 (give time to complete)
        latest_start = max(1, total_frames - 15)
        self.start_frame = random.randint(1, latest_start)
        
        # Current hop count (starts at hop_limit)
        self.current_hops = self.hop_limit
        
        # Message status
        self.is_active = False  # Not started yet
        self.is_completed = False  # Hop limit reached or manually stopped
        self.target_received = False  # NEW: Did target receive the message?
        self.completion_reason = None  # "hop_limit_exceeded" only
        
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
        """Mark that target has received the message - but continue running"""
        self.target_received = True
        print(f"      🎯 Message {self.id} TARGET REACHED - but continues running until hop limit")
        
    def complete_message(self, reason):
        """Mark message as completed - only when hop limit exceeded"""
        if reason == "hop_limit_exceeded":
            self.is_completed = True
            self.is_active = False
            self.completion_reason = reason
            print(f"      🛑 Message {self.id} COMPLETED: {reason}")
        else:
            # Don't complete for other reasons - just mark target received
            self.target_reached()
            
    def get_status(self):
        """Get current status of the message"""
        if self.is_completed:
            if self.target_received:
                return "SUCCESS"  # Target received AND hop limit exceeded
            else:
                return "EXPIRED"  # Hop limit exceeded but target never received
        elif self.is_active:
            if self.target_received:
                return "SUCCESS_RUNNING"  # Target received but still running
            else:
                return "ACTIVE"  # Still running, target not reached yet
        else:
            return "WAITING"  # Not started yet
        
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
        status = self.get_status()
        target_marker = " 🎯" if self.target_received else ""
        return f"Msg {self.id}: {self.source}→{self.target} | Hops: {self.current_hops}/{self.hop_limit} | Frame: {self.start_frame} | Status: {status}{target_marker}"