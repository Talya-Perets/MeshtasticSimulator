class Node:
    """
    Represents a node in the network
    Each node has status, position, and message handling capabilities
    Now with Adaptive Routing capabilities
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
        self.x = x_pos
        self.y = y_pos
        
        # Node status
        self.status_flags = {
            self.STATUS_NORMAL: True,
            self.STATUS_COLLISION: False,
            self.STATUS_SOURCE: False,
            self.STATUS_TARGET: False,
            self.STATUS_SENDING: False,
            self.STATUS_RECEIVING: False 
        }
        
        # Messages
        self.pending_messages = []
        self.received_messages = []
        self.seen_message_ids = set()
        self.received_message_ids = set()
        
        # Neighbors
        self.neighbors = set()
        
        # ADAPTIVE ROUTING: Enhanced routing tables
        self.routing_table = {}  # {destination: {next_hop: {'distance': int, 'last_updated': frame}}}
        self.learned_routes = {}  # Legacy - keep for compatibility
        
    def reset_frame_status(self):
        """Reset status flags that change each frame"""
        self.status_flags[self.STATUS_COLLISION] = False
        self.status_flags[self.STATUS_SENDING] = False
        self.status_flags[self.STATUS_RECEIVING] = False
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
        """Mark node as receiving a message this frame"""
        if not self.status_flags[self.STATUS_SOURCE] and not self.status_flags[self.STATUS_TARGET]:
            self.status_flags[self.STATUS_RECEIVING] = True
       
    def receive_message_copy(self, message, sender_id, sender_path):
        """Receive a specific copy of a message with its path"""
        # SMART FLOODING: Check if we already have this message
        if hasattr(self, 'received_message_ids'):
            if message.id in self.received_message_ids:
                return False
        else:
            self.received_message_ids = set()
        
        # Check duplicates
        message_key = (message.id, sender_id)
        if hasattr(self, 'seen_message_copies'):
            if message_key in self.seen_message_copies:
                return False
        else:
            self.seen_message_copies = set()
            
        # Accept the message
        self.seen_message_copies.add(message_key)
        self.received_messages.append((message, sender_id, sender_path))
        self.received_message_ids.add(message.id)
        
        return True

    def get_routing_decision(self, message, hop_limit_remaining):
        """Decide which neighbors to send to based on routing table - SEND TO ALL VALID ROUTES"""
        target = message.target
        
        print(f"📋 Node {self.id} routing decision for Message {message.id} (target: {target}):")
        print(f"   Hop limit remaining: {hop_limit_remaining}")
        
        # Check if we have routing info for this target
        if target not in self.routing_table:
            print(f"   ❓ No routes to destination {target} → fallback to FLOODING")
            return list(self.neighbors)  # Fallback to flooding
        
        # Analyze available routes to the TARGET - SEND TO ALL VALID ROUTES
        print(f"   Checking routes to target {target}:")
        valid_neighbors = []
        
        for next_hop, route_info in self.routing_table[target].items():
            distance = route_info['distance']
            
            if hop_limit_remaining >= distance and next_hop in self.neighbors:
                print(f"   ├─ via neighbor {next_hop} → distance {distance}, hop_limit_left: {hop_limit_remaining} ✅ SEND")
                valid_neighbors.append(next_hop)
            elif next_hop not in self.neighbors:
                print(f"   ├─ via {next_hop} → distance {distance} ❌ NOT A NEIGHBOR")
            else:
                print(f"   ├─ via neighbor {next_hop} → distance {distance}, hop_limit_left: {hop_limit_remaining} ❌ TOO FAR")
        
        if not valid_neighbors:
            print(f"   ⚠️ No valid routes found → fallback to FLOODING")
            return list(self.neighbors)  # Fallback to flooding if no good routes
        
        print(f"   ✅ Decision: Send to neighbors {valid_neighbors}")
        return valid_neighbors

    def learn_route_from_message(self, message_source, path, current_frame):
        """Learn routing information from received message with BIDIRECTIONAL LEARNING"""
        if len(path) < 2:
            return  # No routing info to learn
        
        # Find my position in the path
        try:
            my_index = path.index(self.id)
        except ValueError:
            print(f"      ⚠️ Node {self.id} not found in path {path}")
            return
        
        print(f"      🧠 Node {self.id} learning from path: {' → '.join(map(str, path))}")
        
        # Learn routes to ALL nodes that appeared BEFORE me in the path
        for i in range(my_index):
            target_node = path[i]
            distance_to_target = my_index - i
            next_hop_to_target = path[my_index - 1]  # The node that sent me this message
            
            # Update routing table for this target
            if target_node not in self.routing_table:
                self.routing_table[target_node] = {}
            
            # Check if this is a better or new route
            current_best = None
            if next_hop_to_target in self.routing_table[target_node]:
                current_best = self.routing_table[target_node][next_hop_to_target]
            
            if current_best is None or distance_to_target < current_best['distance']:
                self.routing_table[target_node][next_hop_to_target] = {
                    'distance': distance_to_target,
                    'last_updated': current_frame
                }
                print(f"         📝 Learned: to reach {target_node}, go via {next_hop_to_target} (distance {distance_to_target} hops)")

    def get_best_next_hops(self, destination):
        """Get the best next hops for a destination based on routing table"""
        if destination not in self.routing_table:
            return None  # No routing info - use flooding
            
        # Find the shortest distance
        routes = self.routing_table[destination]
        if not routes:
            return None
            
        min_distance = min(route['distance'] for route in routes.values())
        
        # Get all next hops with the shortest distance
        best_hops = [
            next_hop for next_hop, route_info in routes.items()
            if route_info['distance'] == min_distance
        ]
        
        return best_hops
    
    def should_use_routing_table(self, destination):
        """Decide whether to use routing table or flooding"""
        best_hops = self.get_best_next_hops(destination)
        if best_hops is None:
            return False, []  # No routing info - use flooding
            
        # Filter to only neighbors (in case routing table has outdated info)
        valid_hops = [hop for hop in best_hops if hop in self.neighbors]
        
        if not valid_hops:
            return False, []  # No valid routes - use flooding
            
        return True, valid_hops

    def process_received_messages(self, current_frame=0):
        """Process all message copies received this frame with routing learning"""
        processed_messages = []
        for message, sender_id, sender_path in self.received_messages:
            
            # Create new path
            new_path = message.create_new_copy(sender_id, self.id, sender_path)
            
            # LEARN ROUTING: Update routing table from this message (BIDIRECTIONAL)
            self.learn_route_from_message(message.source, new_path, current_frame)
            
            # Calculate hop limit
            hops_used = len(new_path) - 1
            local_hop_limit = message.hop_limit - hops_used
            
            print(f"      📊 Node {self.id}: Path={' → '.join(map(str, new_path))}, Hops used={hops_used}, Remaining={local_hop_limit}")
            
            # Check if target
            if message.target == self.id:
                if not message.target_received:
                    message.target_reached()
                    print(f"      🎯 Message {message.id} reached target {self.id} - but continues flooding")
                else:
                    print(f"      ℹ️  Message {message.id} target already reached, continues flooding")
                
            # Check hop limit
            if local_hop_limit <= 0:
                if not message.is_completed:
                    message.complete_message("hop_limit_exceeded")
                    print(f"      🛑 Message {message.id} hop limit exceeded at node {self.id}")
                processed_messages.append((message, new_path))
            else:
                self.pending_messages.append((message, new_path, local_hop_limit))
                print(f"      📤 Message {message.id} added to pending (local hops left: {local_hop_limit})")
                processed_messages.append((message, new_path))
                    
        return processed_messages
    
    def print_routing_table(self):
        """Print current routing table for debugging"""
        print(f"      📋 Node {self.id} Routing Table:")
        if not self.routing_table:
            print(f"         (empty)")
            return
            
        for destination, routes in self.routing_table.items():
            print(f"         To reach {destination}:")
            for next_hop, info in routes.items():
                print(f"           via {next_hop} -> distance {info['distance']} (frame {info['last_updated']})")

    def get_display_color(self):
        """Get the color for displaying this node"""
        if self.status_flags[self.STATUS_SOURCE]:
            return "green"
        elif self.status_flags[self.STATUS_TARGET]:
            return "red"
        elif self.status_flags[self.STATUS_COLLISION]:
            return "pink"
        elif self.status_flags[self.STATUS_RECEIVING]:
            return "orange"
        else:
            return "lightblue"
            
    def __str__(self):
        """String representation of the node"""
        active_statuses = [status for status, active in self.status_flags.items() if active and status != self.STATUS_NORMAL]
        return f"Node {self.id} at ({self.x:.1f}, {self.y:.1f}) | Status: {active_statuses}"