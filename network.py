import networkx as nx
import math
import random
import numpy as np
from collections import defaultdict

from message import Message
from node import Node

class Network:
    """
    Network class that manages node distribution and connections
    """
    
    def __init__(self, space_size=10):
        self.graph = nx.Graph()
        self.nodes = {}
        self.node_positions = {}
        
        self.space_size = space_size
        self.communication_radius = 0
        self.target_avg_neighbors = 4
        self.radius_variation = 0.1
        
    def set_transmission_radius(self, radius, variation=0.1):
        """Set communication radius manually"""
        self.communication_radius = radius
        self.radius_variation = variation
        
    def create_nodes(self, num_nodes, distribution_type="improved_random"):
        """Create nodes with specified distribution pattern"""
        self.nodes.clear()
        self.graph.clear()
        
        # Adjust space size based on number of nodes
        self.space_size = max(8, math.sqrt(num_nodes) * 1.8)
        
        if distribution_type == "improved_random":
            self._create_improved_random_layout(num_nodes)
        elif distribution_type == "poisson":
            self._create_poisson_layout(num_nodes)
        else:
            self._create_pure_random_layout(num_nodes)
            
    def _create_improved_random_layout(self, num_nodes):
        """Grid-based distribution with randomness within cells"""
        grid_size = int(np.sqrt(num_nodes)) + 1
        cell_size = self.space_size / grid_size
        
        for i in range(num_nodes):
            grid_x = i % grid_size
            grid_y = i // grid_size
            
            # Random position within cell
            x = grid_x * cell_size + random.uniform(0, cell_size * 0.8) + cell_size * 0.1
            y = grid_y * cell_size + random.uniform(0, cell_size * 0.8) + cell_size * 0.1
            
            # Keep within bounds
            x = min(max(x, 0), self.space_size)
            y = min(max(y, 0), self.space_size)
            
            # Center around (0,0)
            centered_x = x - self.space_size / 2
            centered_y = y - self.space_size / 2
            
            node = Node(i, centered_x, centered_y)
            self.nodes[i] = node
            self.node_positions[i] = (centered_x, centered_y)
            self.graph.add_node(i, pos=(centered_x, centered_y))
            
    def _create_poisson_layout(self, num_nodes):
        """Poisson disk sampling for uniform distribution"""
        positions = self._poisson_disk_sampling(num_nodes)
        for i, (x, y) in enumerate(positions[:num_nodes]):
            # Center around (0,0)
            centered_x = x - self.space_size / 2
            centered_y = y - self.space_size / 2
            
            node = Node(i, centered_x, centered_y)
            self.nodes[i] = node
            self.node_positions[i] = (centered_x, centered_y)
            self.graph.add_node(i, pos=(centered_x, centered_y))
            
    def _create_pure_random_layout(self, num_nodes):
        """Completely random node placement"""
        for i in range(num_nodes):
            x = random.uniform(0, self.space_size)
            y = random.uniform(0, self.space_size)
            
            # Center around (0,0)
            centered_x = x - self.space_size / 2
            centered_y = y - self.space_size / 2
            
            node = Node(i, centered_x, centered_y)
            self.nodes[i] = node
            self.node_positions[i] = (centered_x, centered_y)
            self.graph.add_node(i, pos=(centered_x, centered_y))
            
    def _poisson_disk_sampling(self, num_nodes):
        """Generate points with minimum distance constraint"""
        min_distance = self.space_size / (np.sqrt(num_nodes) * 1.5)
        positions = []
        attempts = 0
        max_attempts = num_nodes * 100
        
        # Start with random point
        positions.append((random.uniform(0, self.space_size), 
                         random.uniform(0, self.space_size)))
        
        while len(positions) < num_nodes and attempts < max_attempts:
            attempts += 1
            
            x = random.uniform(0, self.space_size)
            y = random.uniform(0, self.space_size)
            
            # Check minimum distance from existing points
            valid = True
            for px, py in positions:
                if math.sqrt((x - px)**2 + (y - py)**2) < min_distance:
                    valid = False
                    break
            
            if valid:
                positions.append((x, y))
        
        # Fill remaining with random points if needed
        while len(positions) < num_nodes:
            positions.append((random.uniform(0, self.space_size),
                            random.uniform(0, self.space_size)))
        
        return positions

    def calculate_optimal_radius(self):
        """Find radius that gives target average neighbors"""
        if len(self.nodes) <= 1:
            return 2.0
        
        # Calculate all pairwise distances
        distances = []
        for i in self.nodes:
            for j in self.nodes:
                if i != j:
                    pos1 = self.node_positions[i]
                    pos2 = self.node_positions[j]
                    distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                    distances.append(distance)
        
        distances.sort()
        
        # Start from first quartile distance
        initial_radius = distances[len(distances) // 4]
        
        # Find radius closest to target neighbor count
        best_radius = initial_radius
        best_diff = float('inf')
        
        for radius in np.linspace(initial_radius * 0.3, initial_radius * 3, 30):
            avg_neighbors = self.calculate_avg_neighbors(radius)
            diff = abs(avg_neighbors - self.target_avg_neighbors)
            if diff < best_diff:
                best_diff = diff
                best_radius = radius
        
        return best_radius
    
    def calculate_avg_neighbors(self, radius):
        """Calculate average number of neighbors for given radius"""
        if len(self.nodes) == 0:
            return 0
            
        total_neighbors = 0
        for node_id in self.nodes:
            pos1 = self.node_positions[node_id]
            neighbors = 0
            for other_id in self.nodes:
                if node_id != other_id:
                    pos2 = self.node_positions[other_id]
                    distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                    if distance <= radius:
                        neighbors += 1
            total_neighbors += neighbors
        
        return total_neighbors / len(self.nodes)

    def create_network_connections(self):
        """Create connections based on communication radius"""
        # Calculate optimal radius if not set
        if self.communication_radius == 0:
            self.communication_radius = self.calculate_optimal_radius()
        
        # Clear existing connections
        for node in self.nodes.values():
            node.neighbors.clear()
        self.graph.clear_edges()
        
        # Create connections within radius
        for i in self.nodes:
            pos1 = self.node_positions[i]
            
            # Small random variation in radius
            variation = random.uniform(-self.radius_variation, self.radius_variation)
            node_radius = self.communication_radius * (1 + variation)
            
            for j in self.nodes:
                if i != j and not self.graph.has_edge(i, j):
                    pos2 = self.node_positions[j]
                    distance = math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)
                    
                    if distance <= node_radius:
                        self.nodes[i].add_neighbor(j)
                        self.nodes[j].add_neighbor(i)
                        self.graph.add_edge(i, j)

    def add_connection(self, node1_id, node2_id):
        """Add bidirectional connection between nodes"""
        if not self.graph.has_edge(node1_id, node2_id):
            self.graph.add_edge(node1_id, node2_id)
            self.nodes[node1_id].add_neighbor(node2_id)
            self.nodes[node2_id].add_neighbor(node1_id)

    def reset_all_nodes(self):
        """Reset all node states"""
        for node in self.nodes.values():
            node.reset_frame_status()
            node.set_as_source(False)
            node.set_as_target(False)
            node.pending_messages.clear()
            node.received_messages.clear()
            if hasattr(node, 'seen_message_copies'):
                node.seen_message_copies.clear()
            if hasattr(node, 'received_message_ids'):
                node.received_message_ids.clear()

    def print_network_summary(self):
        """Print network statistics"""
        total_edges = self.graph.number_of_edges()
        avg_degree = (2 * total_edges) / len(self.nodes) if self.nodes else 0
        
        print(f"Network: {len(self.nodes)} nodes, {total_edges} edges")
        print(f"Area: {self.space_size:.1f} x {self.space_size:.1f}")
        print(f"Communication radius: {self.communication_radius:.2f}")
        print(f"Average neighbors: {avg_degree:.1f}")
        
        if self.nodes:
            degrees = [len(node.neighbors) for node in self.nodes.values()]
            print(f"Connection range: {min(degrees)} to {max(degrees)} per node")
            
            max_possible_edges = len(self.nodes) * (len(self.nodes) - 1) // 2
            density = (total_edges / max_possible_edges) * 100 if max_possible_edges > 0 else 0
            print(f"Network density: {density:.1f}%")
            print(f"Connected: {nx.is_connected(self.graph)}")
    
    def get_transmission_radius(self):
        """Get current communication radius"""
        return self.communication_radius