import random
import time
from network import Network
from message import Message
from routing import FloodingRouter, GreedyRouter, HybridRouter
import matplotlib.pyplot as plt

class MeshtasticSimulator:
    def __init__(self):
        self.network = None
        self.all_messages = []
        self.active_messages = []
        self.completed_messages = []
        self.current_time = 0
        self.router = None
        self.simulation_step = 0
    
    def create_network(self, num_nodes, space_size=100, target_neighbors=4, distribution="improved_random"):
        if not (0 <= num_nodes <= 100):
            raise ValueError("Number of nodes must be between 0 and 100")
        
        self.network = Network(space_size)
        self.network.target_avg_neighbors = target_neighbors
        self.network.add_nodes(num_nodes, distribution)
        self.network.create_connections()
        self.router = FloodingRouter(self.network)
        return self.network
    
    def set_routing_algorithm(self, algorithm="flooding", **kwargs):
        if algorithm == "flooding":
            self.router = FloodingRouter(self.network)
        elif algorithm == "greedy":
            self.router = GreedyRouter(self.network)
        elif algorithm == "hybrid":
            self.router = HybridRouter(self.network, **kwargs)
        else:
            raise ValueError("Unknown routing algorithm")
    
    def generate_random_message_pairs(self, num_messages, start_times=None):
        if not self.network or len(self.network.nodes) < 2:
            print("Need at least 2 nodes to generate messages")
            return []
        
        new_messages = []
        node_ids = list(self.network.nodes.keys())
        
        for i in range(num_messages):
            source = random.choice(node_ids)
            destination = random.choice([n for n in node_ids if n != source])
            
            # Random hop limit between 3-6
            hop_limit = random.randint(3, 6)
            
            start_time = start_times[i] if start_times else i * 2
            message = Message(source, destination, f"Msg-{i+1}", hop_limit, start_time)
            new_messages.append(message)
            print(f"Generated Msg-{i+1}: {source} -> {destination} (hop limit: {hop_limit})")
        
        self.all_messages.extend(new_messages)
        return new_messages
    
    def step_simulation(self):
        """Execute ONE single node sending step"""
        self.simulation_step += 1
        
        # If no active messages, try to start next message
        if not self.active_messages:
            waiting_messages = [m for m in self.all_messages if not m.active and not m.reached_destination and not m.failed and m.start_time == -1]
            if waiting_messages:
                # Start the first waiting message
                next_msg = waiting_messages[0]
                next_msg.start_time = 0
                next_msg.activate()
                
                # Place message at source (not sending yet)
                initial_msg = Message(next_msg.source, next_msg.destination, next_msg.content, next_msg.hop_limit, 0)
                initial_msg.message_id = next_msg.message_id
                initial_msg.active = True
                initial_msg.current_node = next_msg.source
                initial_msg.path = [next_msg.source]
                initial_msg.current_hop_count = 0
                self.active_messages.append(initial_msg)
                print(f"Started {next_msg.message_id}: {next_msg.source} -> {next_msg.destination}")
                return True
        
        # Start very first message
        for msg in self.all_messages:
            if not msg.active and msg.start_time == 0 and not msg.reached_destination and not msg.failed:
                msg.activate()
                initial_msg = Message(msg.source, msg.destination, msg.content, msg.hop_limit, 0)
                initial_msg.message_id = msg.message_id
                initial_msg.active = True
                initial_msg.current_node = msg.source
                initial_msg.path = [msg.source]
                initial_msg.current_hop_count = 0
                self.active_messages.append(initial_msg)
                print(f"Started first {msg.message_id}: {msg.source} -> {msg.destination}")
                return True
        
        if not self.active_messages:
            return False
        
        # Get current message info
        current_message = self.active_messages[0]
        message_id = current_message.message_id
        
        print(f"\nStep {self.simulation_step}: {message_id}")
        
        # Check if any message reached destination
        reached_destination = any(msg.current_node == msg.destination for msg in self.active_messages)
        if reached_destination:
            completed_msg = next(msg for msg in self.active_messages if msg.current_node == msg.destination)
            completed_msg.mark_as_arrived()
            
            # Update the original message in all_messages
            for original_msg in self.all_messages:
                if original_msg.message_id == message_id:
                    original_msg.reached_destination = True
                    break
            
            self.completed_messages.append(completed_msg)
            self.active_messages.clear()
            
            # Clear histories for next message
            for node in self.network.nodes.values():
                node.sent_messages.clear()
            
            print(f"{message_id} DELIVERED!")
            return True
        
        # Check hop limit
        if current_message.current_hop_count >= current_message.hop_limit:
            current_message.mark_as_failed("Hop limit reached")
            
            # Update the original message in all_messages
            for original_msg in self.all_messages:
                if original_msg.message_id == message_id:
                    original_msg.failed = True
                    original_msg.failure_reason = "Hop limit reached"
                    break
            
            self.completed_messages.append(current_message)
            self.active_messages.clear()
            
            # Clear histories for next message
            for node in self.network.nodes.values():
                node.sent_messages.clear()
            
            print(f"{message_id} FAILED: Hop limit reached")
            return True
        
        # Find ONE sender to send from (not all at once!)
        current_senders = [msg.current_node for msg in self.active_messages]
        
        # Pick the first sender that hasn't sent yet
        active_sender = None
        for sender in current_senders:
            sender_node = self.network.nodes[sender]
            if not sender_node.has_seen_message(message_id):
                active_sender = sender
                break
        
        if not active_sender:
            # All current senders have already sent - this shouldn't happen
            current_message.mark_as_failed("All senders exhausted")
            for original_msg in self.all_messages:
                if original_msg.message_id == message_id:
                    original_msg.failed = True
                    original_msg.failure_reason = "All senders exhausted"
                    break
            self.completed_messages.append(current_message)
            self.active_messages.clear()
            for node in self.network.nodes.values():
                node.sent_messages.clear()
            print(f"{message_id} FAILED: All senders exhausted")
            return True
        
        # Find neighbors of this ONE sender
        sender_node = self.network.nodes[active_sender]
        next_receivers = []
        for neighbor_id in sender_node.neighbors:
            neighbor_node = self.network.nodes[neighbor_id]
            if not neighbor_node.has_seen_message(message_id):
                next_receivers.append(neighbor_id)
        
        print(f"Node {active_sender} sending to: {next_receivers}")
        
        if not next_receivers:
            # This sender has no new neighbors, mark as sent and continue
            sender_node.mark_message_as_sent(message_id)
            print(f"Node {active_sender} has no new neighbors")
            return True
        
        # Mark this sender as having sent the message
        sender_node.mark_message_as_sent(message_id)
        
        # Create new messages for this sender's neighbors
        hop_count = current_message.current_hop_count + 1
        
        for receiver in next_receivers:
            new_msg = Message(current_message.source, current_message.destination, 
                            current_message.content, current_message.hop_limit, 0)
            new_msg.message_id = message_id
            new_msg.active = True
            new_msg.current_node = receiver
            new_msg.current_hop_count = hop_count
            # Build path by extending current path
            new_msg.path = current_message.path.copy()
            new_msg.path.append(receiver)
            self.active_messages.append(new_msg)
        
        print(f"Added {len(next_receivers)} new message copies")
        return True
    
    def visualize_current_state(self, key_callback=None):
        if not self.network:
            print("No network to visualize")
            return
        
        title = f"Meshtastic Simulator - Step {self.simulation_step}"
        
        # Pass all messages to the network for display
        self.network.all_simulator_messages = self.all_messages
        
        self.network.visualize_interactive(
            title=title,
            active_messages=self.active_messages,
            completed_messages=self.completed_messages,
            message_selection_callback=None,
            key_callback=key_callback
        )
    
    def print_simulation_results(self):
        total_messages = len(self.completed_messages)
        delivered = len([m for m in self.completed_messages if m.reached_destination])
        failed = len([m for m in self.completed_messages if m.failed])
        
        print(f"\n=== Simulation Results ===")
        print(f"Total messages: {total_messages}")
        delivered_pct = (delivered/total_messages*100) if total_messages > 0 else 0
        failed_pct = (failed/total_messages*100) if total_messages > 0 else 0
        print(f"Delivered: {delivered} ({delivered_pct:.1f}%)")
        print(f"Failed: {failed} ({failed_pct:.1f}%)")
        
        if delivered > 0:
            avg_hops = sum(len(m.path)-1 for m in self.completed_messages if m.reached_destination) / delivered
            print(f"Average hops for delivered messages: {avg_hops:.1f}")
        
        print("\nMessage Details:")
        for msg in self.completed_messages:
            path_str = " -> ".join(map(str, msg.path))
            print(f"  {msg.message_id}: {msg.get_status()}")
            print(f"    Path: {path_str}")
            print(f"    Hops: {len(msg.path)-1}")
    
    def print_network_stats(self):
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