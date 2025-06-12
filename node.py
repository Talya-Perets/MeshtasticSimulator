class Node:
    """
    Represents a node in the network
    Each node has status, position, and message handling capabilities
    """
    
    # Node status constants
    STATUS_NORMAL = "normal"
    STATUS_COLLISION = "collision"
    STATUS_SOURCE = "source" 
    STATUS_TARGET = "target"
    STATUS_SENDING = "sending"
    STATUS_RECEIVING = "receiving"  
    
    def __init__(self, node_id, x_pos, y_pos):
        self.id = node_id
        self.x = x_pos  # X coordinate for display
        self.y = y_pos  # Y coordinate for display
        
        # Node status - can have multiple statuses
        self.status_flags = {
            self.STATUS_NORMAL: True,
            self.STATUS_COLLISION: False,
            self.STATUS_SOURCE: False,
            self.STATUS_TARGET: False,
            self.STATUS_SENDING: False,
            self.STATUS_RECEIVING: False 
        }
        
        # Messages this node needs to forward
        self.pending_messages = []  # Messages waiting to be sent
        self.received_messages = []  # Messages received this frame
        
        # Messages this node has already seen (to prevent loops)
        self.seen_message_ids = set()
        
        # SMART FLOODING: Track which messages this node has received
        self.received_message_ids = set()
        
        # Neighbors (connected nodes)
        self.neighbors = set()
        self.routing_table = {}
    
        # Track which destinations we can reach and via which neighbor
        self.learned_routes = {}  # {destination: [list_of_next_hops_with_distances]}

        
    def reset_frame_status(self):
        """Reset status flags that change each frame"""
        
        # CRITICAL: Always reset these flags each frame
        self.status_flags[self.STATUS_COLLISION] = False
        self.status_flags[self.STATUS_SENDING] = False
        self.status_flags[self.STATUS_RECEIVING] = False
        
        # Clear received messages for this frame
        self.received_messages.clear()
      
    def add_neighbor(self, neighbor_id):
        """Add a neighbor node"""
        self.neighbors.add(neighbor_id)
        
    def set_as_source(self, is_source=True):
        """Mark node as message source"""
        self.status_flags[self.STATUS_SOURCE] = is_source
        
    def set_as_target(self, is_target=True):
        """Mark node as message target"""
        self.status_flags[self.STATUS_TARGET] = is_target
        
    def set_collision(self):
        """Mark node as having collision this frame"""
        self.status_flags[self.STATUS_COLLISION] = True
        
    def set_sending(self):
        """Mark node as sending this frame"""
        self.status_flags[self.STATUS_SENDING] = True
        
    def set_receiving(self):
        """Mark node as receiving a message this frame - only if not source/target"""
        # Don't override source/target status
        if not self.status_flags[self.STATUS_SOURCE] and not self.status_flags[self.STATUS_TARGET]:
            self.status_flags[self.STATUS_RECEIVING] = True
       
    def receive_message_copy(self, message, sender_id, sender_path):
        """Receive a specific copy of a message with its path"""
        
        # SMART FLOODING: Check if we already have this message
        if hasattr(self, 'received_message_ids'):
            if message.id in self.received_message_ids:
                return False  # Reject the message
        else:
            self.received_message_ids = set()
        
        # Check if we've already seen this message from this specific sender (avoid duplicates)
        message_key = (message.id, sender_id)
        
        if hasattr(self, 'seen_message_copies'):
            if message_key in self.seen_message_copies:
                return False
        else:
            self.seen_message_copies = set()
            
        # Accept the message
        self.seen_message_copies.add(message_key)
        self.received_messages.append((message, sender_id, sender_path))
        
        # Mark that we now have this message (for future rejections)
        self.received_message_ids.add(message.id)
        
        return True

    def process_received_messages(self):
        """Process all message copies received this frame"""
        # No need to check collision here - it's handled in _process_transmissions
        
        processed_messages = []
        for message, sender_id, sender_path in self.received_messages:
            
            # FIXED: Create new path correctly with proper parameter names
            new_path = message.create_new_copy(sender_id, self.id, sender_path)
            
            # FIXED: Calculate hop limit correctly
            # Number of hops used = path length - 1 (since path includes source)
            hops_used = len(new_path) - 1
            local_hop_limit = message.hop_limit - hops_used
            
            print(f"      📊 Node {self.id}: Path={' → '.join(map(str, new_path))}, Hops used={hops_used}, Remaining={local_hop_limit}")
            
            # Check if this is the target
            if message.target == self.id:
                # TARGET REACHED - mark but DON'T add to pending (target doesn't forward)
                if not message.target_received:
                    message.target_reached()  # This just marks target_received = True
                    print(f"      🎯 Message {message.id} reached target {self.id} - TARGET DOES NOT FORWARD")
                else:
                    print(f"      ℹ️  Message {message.id} already reached target, arrived again at {self.id}")
                
                # Target doesn't forward the message, just receives it
                processed_messages.append((message, new_path))
                continue
            
            # Check hop limit and decide what to do
            if local_hop_limit <= 0:
                # HOP LIMIT EXCEEDED - COMPLETE IT
                if not message.is_completed:
                    message.complete_message("hop_limit_exceeded")
                    print(f"      ⚠️  Message {message.id} hop limit exceeded at node {self.id} (used {hops_used}/{message.hop_limit})")
                processed_messages.append((message, new_path))
            else:
                # Message continues - add to pending for next frame (only if not target)
                self.pending_messages.append((message, new_path, local_hop_limit))
                print(f"      📤 Message {message.id} added to pending (local hops left: {local_hop_limit})")
                processed_messages.append((message, new_path))
                    
        return processed_messages
        
    def get_display_color(self):
        """Get the color for displaying this node"""
        # Priority order: Source/Target ALWAYS win over everything else
        if self.status_flags[self.STATUS_SOURCE]:
            return "green"  # Source - HIGHEST priority - ALWAYS GREEN
        elif self.status_flags[self.STATUS_TARGET]:
            return "red"  # Target - SECOND highest priority - ALWAYS RED
        elif self.status_flags[self.STATUS_COLLISION]:
            return "pink"  # Collision - THIRD priority - PINK for multiple messages
        elif self.status_flags[self.STATUS_RECEIVING]:
            return "orange"  # Receiving - FOURTH priority - ORANGE for successful receive
        # Note: SENDING is not displayed as a color - senders stay normal unless they're also receiving
        else:
            return "lightblue"  # Normal - DEFAULT
            
    def __str__(self):
        """String representation of the node"""
        active_statuses = [status for status, active in self.status_flags.items() if active and status != self.STATUS_NORMAL]
        return f"Node {self.id} at ({self.x:.1f}, {self.y:.1f}) | Status: {active_statuses}"