import networkx as nx
import math
import random
from collections import defaultdict

# Import our custom classes
from message import Message
from node import Node

class Network:
    """
    Network class that manages the network structure, connections, and node layout
    """
    
    def __init__(self):
        # Network structure
        self.graph = nx.Graph()  # NetworkX graph
        self.nodes = {}  # Dictionary: node_id -> Node object
        self.node_positions = {}
        
    def create_nodes(self, num_nodes):
        """Create nodes with better distributed layout"""
        self.nodes.clear()
        self.graph.clear()
        
        # Calculate grid/area parameters based on number of nodes
        if num_nodes <= 25:
            # Grid layout for smaller networks
            cols = int(math.ceil(math.sqrt(num_nodes)))
            rows = int(math.ceil(num_nodes / cols))
            
            # Grid spacing
            spacing = 1.5
            start_x = -(cols - 1) * spacing / 2
            start_y = -(rows - 1) * spacing / 2
            
            node_id = 0
            for row in range(rows):
                for col in range(cols):
                    if node_id >= num_nodes:
                        break
                        
                    # Calculate position with small random offset
                    x = start_x + col * spacing + random.uniform(-0.2, 0.2)
                    y = start_y + row * spacing + random.uniform(-0.2, 0.2)
                    
                    # Create node
                    node = Node(node_id, x, y)
                    self.nodes[node_id] = node
                    self.node_positions[node_id] = (x, y)
                    self.graph.add_node(node_id, pos=(x, y))
                    
                    node_id += 1
                    
        else:
            # Random scatter for larger networks
            width = math.sqrt(num_nodes) * 1.2
            height = math.sqrt(num_nodes) * 0.8
            min_distance = 0.6
            
            positions = []
            
            for i in range(num_nodes):
                placed = False
                attempts = 0
                
                while not placed and attempts < 50:
                    x = random.uniform(-width/2, width/2)
                    y = random.uniform(-height/2, height/2)
                    
                    # Check minimum distance
                    valid = True
                    for px, py in positions:
                        if math.sqrt((x-px)**2 + (y-py)**2) < min_distance:
                            valid = False
                            break
                    
                    if valid:
                        positions.append((x, y))
                        
                        node = Node(i, x, y)
                        self.nodes[i] = node
                        self.node_positions[i] = (x, y)
                        self.graph.add_node(i, pos=(x, y))
                        
                        placed = True
                    
                    attempts += 1
                
                # If couldn't place with minimum distance, place anyway
                if not placed:
                    x = random.uniform(-width/2, width/2)
                    y = random.uniform(-height/2, height/2)
                    
                    node = Node(i, x, y)
                    self.nodes[i] = node
                    self.node_positions[i] = (x, y)
                    self.graph.add_node(i, pos=(x, y))

    def create_network_connections(self):
        """Create network connections between nodes"""
        node_ids = list(self.nodes.keys())
        num_nodes = len(node_ids)
        
        # Each node connects to 3-4 nearest neighbors on average
        target_connections_per_node = 3.5
        total_target_edges = int((num_nodes * target_connections_per_node) / 2)
        
        # Strategy: Connect each node to its k nearest neighbors + some random connections
        k = 2  # Each node connects to 2 nearest neighbors
        
        # Connect to nearest neighbors (creates base connectivity)
        for node_id in node_ids:
            # Calculate distances to all other nodes
            distances = []
            node_pos = self.node_positions[node_id]
            
            for other_id in node_ids:
                if other_id != node_id:
                    other_pos = self.node_positions[other_id]
                    dist = math.sqrt((node_pos[0] - other_pos[0])**2 + 
                                   (node_pos[1] - other_pos[1])**2)
                    distances.append((dist, other_id))
            
            # Sort by distance and connect to k nearest
            distances.sort()
            for _, neighbor_id in distances[:k]:
                if not self.graph.has_edge(node_id, neighbor_id):
                    self.add_connection(node_id, neighbor_id)
        
        # Add random connections to reach target
        current_edges = self.graph.number_of_edges()
        while current_edges < total_target_edges:
            node1 = random.choice(node_ids)
            node2 = random.choice(node_ids)
            
            if node1 != node2 and not self.graph.has_edge(node1, node2):
                self.add_connection(node1, node2)
                current_edges += 1

    def add_connection(self, node1_id, node2_id):
        """Add bidirectional connection between two nodes"""
        self.graph.add_edge(node1_id, node2_id)
        self.nodes[node1_id].add_neighbor(node2_id)
        self.nodes[node2_id].add_neighbor(node1_id)

    def reset_all_nodes(self):
        """Reset all nodes frame status"""
        for node in self.nodes.values():
            node.reset_frame_status()
            node.set_as_source(False)
            node.set_as_target(False)
            node.pending_messages.clear()
            node.received_messages.clear()
            if hasattr(node, 'seen_message_copies'):
                node.seen_message_copies.clear()
            # CLEAR MESSAGE TRACKING
            if hasattr(node, 'received_message_ids'):
                node.received_message_ids.clear()

    def print_network_summary(self):
        """Print summary of network structure"""
        print(f"Network: {len(self.nodes)} nodes, {self.graph.number_of_edges()} edges")
        print("\nNode Connections:")
        for node_id, node in self.nodes.items():
            neighbors = sorted(list(node.neighbors))
            print(f"  Node {node_id}: connected to {neighbors}")