import random
import time
from network import Network
from message import Message
from routing import FloodingRouter, GreedyRouter, HybridRouter
import matplotlib.pyplot as plt

class MeshtasticSimulator:
    """
    Simple realistic Meshtastic simulator - ONE MESSAGE AT A TIME.
    
    Rules:
    1. Only one message active in the network at any time
    2. Each node remembers which messages it already saw
    3. When message reaches destination OR fails → start next message
    4. Clear step-by-step progression
    """
    
    def __init__(self):
        self.network = None
        self.all_messages = []          # All messages ever created
        self.completed_messages = []    # Messages that finished (delivered or failed)
        self.current_time = 0
        self.router = None
        self.simulation_step = 0
        self.message_queue = []         # Queue of messages waiting to start
        
        # Current active message tracking
        self.current_message = None     # The ONE message currently active
        self.active_nodes = set()       # Nodes that currently have the message
        
        # NEW: History tracking for visualization
        self.all_paths = []             # All paths taken by completed messages
        self.all_visited_nodes = set()  # All nodes that received any message
    
    def create_network(self, num_nodes, space_size=100, target_neighbors=4, distribution="improved_random"):
        """Create a new network with specified parameters."""
        if not (0 <= num_nodes <= 100):
            raise ValueError("Number of nodes must be between 0 and 100")
        
        self.network = Network(space_size)
        self.network.target_avg_neighbors = target_neighbors
        self.network.add_nodes(num_nodes, distribution)
        self.network.create_connections()
        self.router = FloodingRouter(self.network)
        return self.network
    
    def set_routing_algorithm(self, algorithm="flooding", **kwargs):
        """Set the routing algorithm for message propagation."""
        if algorithm == "flooding":
            self.router = FloodingRouter(self.network)
        elif algorithm == "greedy":
            self.router = GreedyRouter(self.network)
        elif algorithm == "hybrid":
            self.router = HybridRouter(self.network, **kwargs)
        else:
            raise ValueError("Unknown routing algorithm")
    
    def generate_random_message_pairs(self, num_messages, start_times=None):
        """Generate random messages with random source-destination pairs."""
        if not self.network or len(self.network.nodes) < 2:
            print("Need at least 2 nodes to generate messages")
            return []
        
        new_messages = []
        node_ids = list(self.network.nodes.keys())
        
        for i in range(num_messages):
            # Pick random source and destination (different nodes)
            source = random.choice(node_ids)
            destination = random.choice([n for n in node_ids if n != source])
            
            # Random hop limit between 4-8
            hop_limit = random.randint(4, 8)
            
            message = Message(source, destination, f"Auto message {i+1}", hop_limit, 0)
            new_messages.append(message)
            print(f"Generated message: {source} -> {destination} (hop limit: {hop_limit})")
        
        # Add to message queue
        self.all_messages.extend(new_messages)
        self.message_queue.extend(new_messages)
        return new_messages
    
    def step_simulation(self):
        """
        Execute ONE step of message propagation - SIMPLE VERSION.
        
        Rules:
        1. If no active message → start next message from queue
        2. If active message → propagate it one hop
        3. Check if message delivered or failed → move to next
        """
        print(f"\n🔧 DEBUG: step_simulation() called - Step {self.simulation_step + 1}")
        self.simulation_step += 1
        
        # CASE 1: No active message - start next one
        if self.current_message is None:
            if not self.message_queue:
                print("No more messages to process")
                return False
            
            # Start new message
            self.current_message = self.message_queue.pop(0)
            self.current_message.activate()
            self.current_message.current_node = self.current_message.source
            self.current_message.path = [self.current_message.source]
            self.current_message.current_hop_count = 0
            self.active_nodes = {self.current_message.source}
            
            # Clear all node histories for new message
            for node in self.network.nodes.values():
                node.sent_messages.clear()
                node.received_messages.clear()
            
            # Mark source as having the message
            self.network.nodes[self.current_message.source].mark_message_as_sent(self.current_message.message_id)
            
            print(f"\n=== NEW MESSAGE STARTED ===")
            print(f"📧 Message #{len(self.completed_messages) + 1}: {self.current_message.source} -> {self.current_message.destination}")
            print(f"🔹 ID: {self.current_message.message_id}")
            print(f"📊 Hop limit: {self.current_message.hop_limit}")
            print(f"📍 Message placed at source node {self.current_message.source}")
            print("Press SPACE to begin transmission...")
            return True
        
        # CASE 2: Active message exists - propagate it
        print(f"\n=== STEP {self.simulation_step} ===")
        print(f"📧 Message: {self.current_message.source} -> {self.current_message.destination}")
        print(f"🔹 ID: {self.current_message.message_id}")
        print(f"📊 Current hop: {self.current_message.current_hop_count}/{self.current_message.hop_limit}")
        print(f"📡 Nodes with message: {sorted(list(self.active_nodes))}")
        print(f"🎯 Is destination {self.current_message.destination} in active nodes? {self.current_message.destination in self.active_nodes}")
        
        # CHECK 1: Message reached destination? - CHECK IMMEDIATELY!
        if self.current_message.destination in self.active_nodes:
            # Add current path to history before completing
            current_path = self.current_message.path.copy()
            if current_path not in self.all_paths:
                self.all_paths.append(current_path)
            
            # Add all nodes in current path to visited nodes
            self.all_visited_nodes.update(current_path)
            # Also add all active nodes (in case destination was reached this step)
            self.all_visited_nodes.update(self.active_nodes)
            
            self.current_message.mark_as_arrived()
            self.completed_messages.append(self.current_message)
            
            print(f"\n🎉 MESSAGE DELIVERED! 🎉")
            print(f"Message {self.current_message.message_id} reached destination {self.current_message.destination}!")
            print(f"Total hops: {self.current_message.current_hop_count}")
            path_str = " -> ".join(map(str, current_path))
            print(f"Path taken: {path_str}")
            print(f"Historical paths now: {len(self.all_paths)}")
            print(f"Historical nodes now: {sorted(list(self.all_visited_nodes))}")
            
            # Reset for next message - but keep history!
            self.current_message = None
            self.active_nodes.clear()
            print("Press SPACE for next message...")
            return True
        
        # CHECK 2: Message exceeded hop limit?
        if self.current_message.current_hop_count >= self.current_message.hop_limit:
            # Add current path to history before failing
            current_path = self.current_message.path.copy()
            if current_path not in self.all_paths:
                self.all_paths.append(current_path)
            
            # Add all nodes in path to visited nodes
            self.all_visited_nodes.update(current_path)
            
            self.current_message.mark_as_failed("Hop limit reached")
            self.completed_messages.append(self.current_message)
            
            print(f"\n❌ MESSAGE FAILED ❌")
            print(f"Message {self.current_message.message_id} exceeded hop limit ({self.current_message.hop_limit})")
            path_str = " -> ".join(map(str, current_path))
            print(f"Path taken: {path_str}")
            
            # Reset for next message - but keep history!
            self.current_message = None
            self.active_nodes.clear()
            print("Press SPACE for next message...")
            return True
        
        # STEP 3: Find neighbors to transmit to
        next_receivers = set()
        transmission_details = {}
        
        print("These nodes will now transmit to their neighbors...")
        
        for sender_id in self.active_nodes:
            sender_node = self.network.nodes[sender_id]
            sender_neighbors = []
            
            for neighbor_id in sender_node.neighbors:
                neighbor_node = self.network.nodes[neighbor_id]
                
                # Only send to neighbors that haven't seen this message
                if not neighbor_node.has_seen_message(self.current_message.message_id):
                    next_receivers.add(neighbor_id)
                    sender_neighbors.append(neighbor_id)
            
            if sender_neighbors:
                transmission_details[sender_id] = sender_neighbors
                print(f"   📡 Node {sender_id} → {sender_neighbors}")
            else:
                print(f"   📡 Node {sender_id} → (no new neighbors)")
        
        # CHECK 3: No new receivers?
        if not next_receivers:
            # Add current path to history before failing
            current_path = self.current_message.path.copy()
            if current_path not in self.all_paths:
                self.all_paths.append(current_path)
            
            # Add all nodes in path to visited nodes
            self.all_visited_nodes.update(current_path)
            
            self.current_message.mark_as_failed("No more reachable neighbors")
            self.completed_messages.append(self.current_message)
            
            print(f"\n❌ MESSAGE FAILED ❌")
            print(f"Message {self.current_message.message_id} has no more neighbors to reach")
            path_str = " -> ".join(map(str, current_path))
            print(f"Path taken: {path_str}")
            
            # Reset for next message - but keep history!
            self.current_message = None
            self.active_nodes.clear()
            print("Press SPACE for next message...")
            return True
        
        # STEP 4: Mark current senders as processed and receivers as new holders
        for sender_id in self.active_nodes:
            self.network.nodes[sender_id].mark_message_as_sent(self.current_message.message_id)
        
        for receiver_id in next_receivers:
            self.network.nodes[receiver_id].mark_message_as_sent(self.current_message.message_id)
        
        # STEP 5: Update message state and check for completion AFTER transmission
        self.current_message.current_hop_count += 1
        
        # Update path (simplified - just add one receiver as example)
        if next_receivers:
            sample_receiver = list(next_receivers)[0]
            if sample_receiver not in self.current_message.path:
                self.current_message.path.append(sample_receiver)
        
        # Update active nodes
        self.active_nodes = next_receivers.copy()
        
        print(f"\n✅ TRANSMISSION COMPLETED")
        print(f"   - Message reached {len(next_receivers)} new nodes")
        print(f"   - Next hop: {self.current_message.current_hop_count}")
        print(f"   - New active nodes: {sorted(list(self.active_nodes))}")
        
        total_seen = len([n for n in self.network.nodes.values() if n.has_seen_message(self.current_message.message_id)])
        print(f"   - Total nodes that have seen message: {total_seen}")
        
        # CRITICAL: Check if destination was reached AFTER transmission!
        print(f"🎯 Checking if destination {self.current_message.destination} is now in active nodes...")
        if self.current_message.destination in self.active_nodes:
            # Add ALL PATHS from current transmission to history
            # We need to save the path for each active node that reached the destination
            current_base_path = self.current_message.path.copy()[:-1]  # Remove the sample receiver
            
            # Add paths for all nodes that have the message, especially the destination
            for node_id in self.active_nodes:
                # Create a proper path to this node
                node_path = current_base_path.copy()
                if node_id not in node_path:
                    node_path.append(node_id)
                
                if node_path not in self.all_paths:
                    self.all_paths.append(node_path)
                    print(f"   📝 Added path to history: {' -> '.join(map(str, node_path))}")
            
            # Add all nodes that were part of this message transmission to visited nodes  
            for node_id, node in self.network.nodes.items():
                if node.has_seen_message(self.current_message.message_id):
                    self.all_visited_nodes.add(node_id)
            
            self.current_message.mark_as_arrived()
            self.completed_messages.append(self.current_message)
            
            print(f"\n🎉 MESSAGE DELIVERED AFTER TRANSMISSION! 🎉")
            print(f"Message {self.current_message.message_id} reached destination {self.current_message.destination}!")
            print(f"Total hops: {self.current_message.current_hop_count}")
            print(f"All paths added to history: {len(self.all_paths)} total paths")
            print(f"Historical nodes now: {sorted(list(self.all_visited_nodes))}")
            
            # Reset for next message - but keep history!
            self.current_message = None
            self.active_nodes.clear()
            print("Press SPACE for next message...")
            return True
        
        print(f"\nPress SPACE to continue transmission...")
        return True
    
    def get_active_messages_for_visualization(self):
        """Create active messages list for visualization compatibility."""
        # Always create at least one message object to carry the history
        # Even if no current message is active
        
        if not self.current_message:
            # No active message, but we still want to show history
            if self.all_paths or self.all_visited_nodes:
                # Create a dummy message just to carry history data
                dummy_msg = Message(0, 0, "", 1, 0)
                dummy_msg.message_id = "history"
                dummy_msg.active = False
                dummy_msg.all_paths = self.all_paths.copy()
                dummy_msg.all_visited_nodes = self.all_visited_nodes.copy()
                return [dummy_msg]
            return []
        
        # Create message copies for each active node
        active_messages = []
        for node_id in self.active_nodes:
            msg_copy = Message(self.current_message.source, self.current_message.destination,
                             self.current_message.content, self.current_message.hop_limit, 0)
            msg_copy.message_id = self.current_message.message_id
            msg_copy.active = True
            msg_copy.current_node = node_id
            msg_copy.current_hop_count = self.current_message.current_hop_count
            msg_copy.path = self.current_message.path.copy()
            msg_copy.all_paths = self.all_paths.copy()  # Add history
            msg_copy.all_visited_nodes = self.all_visited_nodes.copy()  # Add visited nodes
            active_messages.append(msg_copy)
        
        return active_messages
    
    def visualize_current_state(self, key_callback=None):
        """Display the current state of the network and messages."""
        if not self.network:
            print("No network to visualize")
            return
        
        title = f"Meshtastic Simulator - Step {self.simulation_step}"
        
        # Get active messages for visualization
        active_messages = self.get_active_messages_for_visualization()
        
        # Pass messages to network for display
        self.network.all_simulator_messages = self.all_messages
        
        print(f"🔧 DEBUG: Calling visualize_interactive with key_callback={'Yes' if key_callback else 'None'}")
        
        try:
            viz_success = self.network.visualize_interactive(
                title=title,
                active_messages=active_messages,
                completed_messages=self.completed_messages,
                message_selection_callback=None,
                key_callback=key_callback  # Only pass if provided
            )
            
            if viz_success is False:
                user_input = input("Visualization failed. Press ENTER for next step or 'q' to quit: ")
                if user_input.lower() == 'q':
                    return False
                    
        except Exception as e:
            print(f"Critical visualization error: {e}")
            import traceback
            traceback.print_exc()
            user_input = input("Press ENTER for next step or 'q' to quit: ")
            if user_input.lower() == 'q':
                return False
    
    def print_simulation_results(self):
        """Print detailed simulation results and statistics."""
        total_messages = len(self.completed_messages)
        delivered = len([m for m in self.completed_messages if m.reached_destination])
        failed = len([m for m in self.completed_messages if m.failed])
        
        print(f"\n=== Simulation Results ===")
        print(f"Total messages processed: {total_messages}")
        
        if total_messages > 0:
            delivered_pct = (delivered/total_messages*100)
            failed_pct = (failed/total_messages*100)
            print(f"Delivered: {delivered} ({delivered_pct:.1f}%)")
            print(f"Failed: {failed} ({failed_pct:.1f}%)")
        
        if delivered > 0:
            avg_hops = sum(len(m.path)-1 for m in self.completed_messages 
                          if m.reached_destination and hasattr(m, 'path')) / delivered
            print(f"Average hops for delivered messages: {avg_hops:.1f}")
        
        print("\nMessage Details:")
        for msg in self.completed_messages:
            path_str = " -> ".join(map(str, msg.path)) if hasattr(msg, 'path') else f"{msg.source} -> {msg.destination}"
            print(f"  {msg.message_id}: {msg.get_status()}")
            print(f"    Path: {path_str}")
            if hasattr(msg, 'path'):
                print(f"    Hops: {len(msg.path)-1}")
        
        # Show remaining messages
        remaining = len(self.message_queue)
        if remaining > 0:
            print(f"\nMessages still in queue: {remaining}")
    
    def print_network_stats(self):
        """Print network topology statistics."""
        if not self.network:
            print("No network created yet")
            return
        
        stats = self.network.get_network_stats()
        print("\n=== Network Statistics ===")
        print(f"Number of nodes: {stats['num_nodes']}")
        print(f"Number of connections: {stats['num_edges']}")
        print(f"Communication radius: {stats['communication_radius']:.2f}")
        print(f"Average neighbors per node: {stats['avg_neighbors']:.2f}")
        print(f"Network is connected: {stats['is_connected']}")
        print(f"Graph radius: {stats['graph_radius']}")
        print(f"Graph diameter: {stats['graph_diameter']}")
        print(f"Network density: {stats['density']:.3f}")
    
    def reset_simulation(self):
        """Reset the simulation to initial state."""
        self.completed_messages.clear()
        self.all_messages.clear()
        self.message_queue.clear()
        self.simulation_step = 0
        self.current_message = None
        self.active_nodes.clear()
        
        # NEW: Clear history
        self.all_paths.clear()
        self.all_visited_nodes.clear()
        
        # Clear all nodes
        if self.network:
            for node in self.network.nodes.values():
                node.sent_messages.clear()
                if hasattr(node, 'received_messages'):
                    node.received_messages.clear()
        
        print("Simulation reset!")