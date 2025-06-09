import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
from math import sqrt
from collections import deque
import uuid

class Node:
    """Represents a single Meshtastic device"""
    
    def __init__(self, node_id, x, y):
        self.node_id = node_id
        self.x = x
        self.y = y
        self.neighbors = []  # List of nodes this node can communicate with directly
        self.sent_messages = set()  # Message IDs that already passed through this node
        self.routing_table = {}  # destination_id -> next_hop_id
    
    def distance_from(self, other_node):
        """Calculate distance from another node"""
        return sqrt((self.x - other_node.x)**2 + (self.y - other_node.y)**2)
    
    def add_neighbor(self, neighbor):
        """Add a new neighbor"""
        if neighbor not in self.neighbors:
            self.neighbors.append(neighbor)
    
    def remove_neighbor(self, neighbor):
        """Remove a neighbor"""
        if neighbor in self.neighbors:
            self.neighbors.remove(neighbor)

class Message:
    """Represents a message sent through the network"""
    
    def __init__(self, source, destination, content=""):
        self.message_id = str(uuid.uuid4())[:8]  # Short message ID
        self.source = source
        self.destination = destination
        self.content = content
        self.path = [source]  # List of nodes the message passed through
        self.creation_time = 0
        self.arrival_time = None
        self.reached_destination = False
    
    def add_to_path(self, node):
        """Add node to message path"""
        self.path.append(node)

class Network:
    """Manages the graph of Meshtastic devices"""
    
    def __init__(self, space_size=100):
        self.nodes = {}  # node_id -> Node
        self.graph = nx.Graph()
        self.space_size = space_size
        self.communication_radius = 0
        self.target_avg_neighbors = 4
    
    def add_nodes(self, num_nodes, distribution_type="improved_random"):
        """Create nodes at positions with better distribution"""
        self.nodes.clear()
        self.graph.clear()
        
        if distribution_type == "improved_random":
            # Grid-based with randomness for better distribution
            grid_size = int(np.sqrt(num_nodes)) + 1
            cell_size = self.space_size / grid_size
            
            for i in range(num_nodes):
                # Calculate grid position
                grid_x = i % grid_size
                grid_y = i // grid_size
                
                # Add randomness within cell
                x = grid_x * cell_size + random.uniform(0, cell_size * 0.8) + cell_size * 0.1
                y = grid_y * cell_size + random.uniform(0, cell_size * 0.8) + cell_size * 0.1
                
                # Keep within bounds
                x = min(max(x, 0), self.space_size)
                y = min(max(y, 0), self.space_size)
                
                new_node = Node(i, x, y)
                self.nodes[i] = new_node
                self.graph.add_node(i, pos=(x, y))
                
        elif distribution_type == "poisson":
            # Poisson disk sampling for more even distribution
            positions = self._poisson_disk_sampling(num_nodes)
            for i, (x, y) in enumerate(positions[:num_nodes]):
                new_node = Node(i, x, y)
                self.nodes[i] = new_node
                self.graph.add_node(i, pos=(x, y))
                
        else:  # pure_random
            for i in range(num_nodes):
                x = random.uniform(0, self.space_size)
                y = random.uniform(0, self.space_size)
                
                new_node = Node(i, x, y)
                self.nodes[i] = new_node
                self.graph.add_node(i, pos=(x, y))
    
    def _poisson_disk_sampling(self, num_nodes):
        """Generate points using Poisson disk sampling for better distribution"""
        min_distance = self.space_size / (np.sqrt(num_nodes) * 1.5)
        positions = []
        attempts = 0
        max_attempts = num_nodes * 100
        
        # Start with a random point
        positions.append((random.uniform(0, self.space_size), 
                         random.uniform(0, self.space_size)))
        
        while len(positions) < num_nodes and attempts < max_attempts:
            attempts += 1
            
            # Generate random point
            x = random.uniform(0, self.space_size)
            y = random.uniform(0, self.space_size)
            
            # Check if it's far enough from existing points
            valid = True
            for px, py in positions:
                if sqrt((x - px)**2 + (y - py)**2) < min_distance:
                    valid = False
                    break
            
            if valid:
                positions.append((x, y))
        
        # If we don't have enough points, fill with random
        while len(positions) < num_nodes:
            positions.append((random.uniform(0, self.space_size),
                            random.uniform(0, self.space_size)))
        
        return positions
    
    def calculate_optimal_radius(self):
        """Find optimal communication radius"""
        if len(self.nodes) <= 1:
            return 0
        
        # Calculate all distances between nodes
        distances = []
        for i in self.nodes:
            for j in self.nodes:
                if i != j:
                    distance = self.nodes[i].distance_from(self.nodes[j])
                    distances.append(distance)
        
        distances.sort()
        
        # Start from first quartile
        initial_radius = distances[len(distances) // 4]
        
        # Find best radius
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
            neighbors = 0
            for other_id in self.nodes:
                if node_id != other_id:
                    distance = self.nodes[node_id].distance_from(self.nodes[other_id])
                    if distance <= radius:
                        neighbors += 1
            total_neighbors += neighbors
        
        return total_neighbors / len(self.nodes)
    
    def create_connections(self):
        """Create connections between nodes based on communication radius"""
        self.communication_radius = self.calculate_optimal_radius()
        
        # Clear existing connections
        for node in self.nodes.values():
            node.neighbors.clear()
        self.graph.clear_edges()
        
        # Create new connections
        for i in self.nodes:
            for j in self.nodes:
                if i != j:
                    distance = self.nodes[i].distance_from(self.nodes[j])
                    if distance <= self.communication_radius:
                        self.nodes[i].add_neighbor(j)
                        self.graph.add_edge(i, j)
    
    def get_radius(self):
        """Get graph radius (max distance from center to any node)"""
        if not nx.is_connected(self.graph):
            return float('inf')  # Graph is not connected
        
        center = nx.center(self.graph)[0]
        distances = nx.single_source_shortest_path_length(self.graph, center)
        return max(distances.values())
    
    def get_diameter(self):
        """Get graph diameter (max distance between any two nodes)"""
        if not nx.is_connected(self.graph):
            return float('inf')  # Graph is not connected
        
        return nx.diameter(self.graph)
    
    def visualize(self, title="Meshtastic Network"):
        """Display the network graph"""
        plt.figure(figsize=(12, 8))
        
        # Get positions
        pos = {node_id: (node.x, node.y) for node_id, node in self.nodes.items()}
        
        # Draw nodes
        nx.draw_networkx_nodes(self.graph, pos, node_color='lightblue', 
                              node_size=300, alpha=0.8)
        
        # Draw edges
        nx.draw_networkx_edges(self.graph, pos, alpha=0.6, edge_color='gray')
        
        # Draw labels
        nx.draw_networkx_labels(self.graph, pos, font_size=8)
        
        plt.title(f"{title}\nNodes: {len(self.nodes)}, "
                 f"Communication Radius: {self.communication_radius:.2f}\n"
                 f"Graph Radius: {self.get_radius()}, "
                 f"Graph Diameter: {self.get_diameter()}")
        plt.xlim(-5, self.space_size + 5)
        plt.ylim(-5, self.space_size + 5)
        plt.grid(True, alpha=0.3)
        plt.axis('equal')
        plt.show()
    
    def get_network_stats(self):
        """Get network statistics"""
        if len(self.nodes) == 0:
            return {}
        
        stats = {
            'num_nodes': len(self.nodes),
            'num_edges': self.graph.number_of_edges(),
            'communication_radius': self.communication_radius,
            'avg_neighbors': self.calculate_avg_neighbors(self.communication_radius),
            'is_connected': nx.is_connected(self.graph),
            'graph_radius': self.get_radius(),
            'graph_diameter': self.get_diameter(),
            'density': nx.density(self.graph)
        }
        
        return stats

class MeshtasticSimulator:
    """Main simulator class"""
    
    def __init__(self):
        self.network = None
        self.messages = []
        self.current_time = 0
    
    def create_network(self, num_nodes, space_size=100, target_neighbors=4, distribution="improved_random"):
        """Create a new network with better distribution options"""
        if not (0 <= num_nodes <= 100):
            raise ValueError("Number of nodes must be between 0 and 100")
        
        self.network = Network(space_size)
        self.network.target_avg_neighbors = target_neighbors
        self.network.add_nodes(num_nodes, distribution)
        self.network.create_connections()
        
        return self.network
    
    def display_network(self):
        """Display the current network"""
        if self.network:
            self.network.visualize()
        else:
            print("No network created yet")
    
    def print_network_stats(self):
        """Print network statistics"""
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

# Example usage
if __name__ == "__main__":
    # Create simulator
    sim = MeshtasticSimulator()
    
    # Try different distribution types:
    # "improved_random" - grid-based with randomness (recommended)
    # "poisson" - more evenly spaced
    # "pure_random" - completely random (original)
    
    network = sim.create_network(num_nodes=20, space_size=100, 
                                target_neighbors=4, distribution="improved_random")
    
    # Display network statistics
    sim.print_network_stats()
    
    # Visualize network
    sim.display_network()