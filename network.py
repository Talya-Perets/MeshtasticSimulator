import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import random
from math import sqrt
from node import Node

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
    
    def visualize_interactive(self, title="Meshtastic Network", active_messages=None, completed_messages=None, 
                            message_selection_callback=None, key_callback=None, clear_previous=True):
        """Interactive visualization with keyboard support - FIXED VERSION"""
        
        try:
            if clear_previous:
                plt.clf()
            
            # Set up the figure
            fig = plt.gcf()
            fig.set_size_inches(16, 10)
            
            # Main network plot (left side)
            ax_network = plt.subplot2grid((1, 4), (0, 0), colspan=3)
            plt.sca(ax_network)
            
            # Get positions
            pos = {node_id: (node.x, node.y) for node_id, node in self.nodes.items()}
            
            # Default colors
            node_colors = ['lightblue'] * len(self.nodes)
            edge_colors = ['gray'] * self.graph.number_of_edges()
            edge_widths = [1] * self.graph.number_of_edges()
            
            # Color nodes and edges based on active messages
            if active_messages:
                # Group messages by message_id
                message_groups = {}
                for msg in active_messages:
                    if msg.message_id not in message_groups:
                        message_groups[msg.message_id] = []
                    message_groups[msg.message_id].append(msg)
                
                for message_id, message_copies in message_groups.items():
                    sample_msg = message_copies[0]
                    
                    # Color source node (green)
                    if sample_msg.source < len(node_colors):
                        node_colors[sample_msg.source] = 'green'
                    
                    # Color destination node (red)
                    if sample_msg.destination < len(node_colors):
                        node_colors[sample_msg.destination] = 'red'
                    
                    # Get current nodes that have the message
                    current_nodes = set(msg.current_node for msg in message_copies)
                    
                    # Get all nodes that have been visited (from paths)
                    all_visited_nodes = set()
                    for msg in message_copies:
                        all_visited_nodes.update(msg.path)
                    
                    # Previous nodes (visited but not current) - YELLOW
                    previous_nodes = all_visited_nodes - current_nodes
                    for node_id in previous_nodes:
                        if node_id < len(node_colors) and node_colors[node_id] not in ['green', 'red']:
                            node_colors[node_id] = 'yellow'
                    
                    # Current nodes (have message now) - ORANGE
                    for node_id in current_nodes:
                        if node_id < len(node_colors) and node_colors[node_id] not in ['green', 'red']:
                            node_colors[node_id] = 'orange'
                    
                    # Color edges in the paths (already traveled) - LIGHT BLUE
                    edges_list = list(self.graph.edges())
                    for msg in message_copies:
                        for i in range(len(msg.path) - 1):
                            current = msg.path[i]
                            next_node = msg.path[i + 1]
                            
                            for idx, (u, v) in enumerate(edges_list):
                                if (u == current and v == next_node) or (u == next_node and v == current):
                                    edge_colors[idx] = 'lightblue'  # Light blue for history
                                    edge_widths[idx] = 2
                                    break
                    
                    # Color edges from current senders to their unvisited neighbors - BRIGHT BLUE (ACTIVE NOW)
                    # Find next receivers (neighbors of current nodes that haven't seen the message)
                    next_receivers = set()
                    for sender_id in current_nodes:
                        sender_node = self.nodes[sender_id]
                        for neighbor_id in sender_node.neighbors:
                            neighbor_node = self.nodes[neighbor_id]
                            if not neighbor_node.has_seen_message(message_id):
                                next_receivers.add(neighbor_id)
                    
                    # Color edges from current senders to next receivers - BRIGHT BLUE (SENDING NOW)
                    for sender_id in current_nodes:
                        sender_node = self.nodes[sender_id]
                        for neighbor_id in sender_node.neighbors:
                            if neighbor_id in next_receivers:
                                # Find this edge and color it
                                for idx, (u, v) in enumerate(edges_list):
                                    if (u == sender_id and v == neighbor_id) or (u == neighbor_id and v == sender_id):
                                        edge_colors[idx] = 'blue'  # Bright blue for current transmission
                                        edge_widths[idx] = 4
                                        break
            
            # Draw network
            nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors, 
                                  node_size=500, alpha=0.8)
            nx.draw_networkx_edges(self.graph, pos, alpha=0.6, 
                                  edge_color=edge_colors, width=edge_widths)
            nx.draw_networkx_labels(self.graph, pos, font_size=10, font_weight='bold')
            
            plt.title(f"{title}\nNodes: {len(self.nodes)}, Active: {len(active_messages) if active_messages else 0}, Completed: {len(completed_messages) if completed_messages else 0}")
            plt.xlim(-5, self.space_size + 5)
            plt.ylim(-5, self.space_size + 5)
            plt.grid(True, alpha=0.3)
            plt.axis('equal')
            
            # Message panel (right side)
            ax_messages = plt.subplot2grid((1, 4), (0, 3))
            ax_messages.set_xlim(0, 1)
            ax_messages.set_ylim(0, 1)
            ax_messages.axis('off')
            
            # Display messages info
            y_pos = 0.95
            ax_messages.text(0.05, y_pos, "MESSAGES", fontsize=14, fontweight='bold')
            y_pos -= 0.08
            
            # Show current message details if there are active messages
            if active_messages:
                current_msg = active_messages[0]
                ax_messages.text(0.05, y_pos, f"Current Message:", fontsize=12, fontweight='bold')
                y_pos -= 0.05
                ax_messages.text(0.1, y_pos, f"ID: {current_msg.message_id}", fontsize=9)
                y_pos -= 0.04
                ax_messages.text(0.1, y_pos, f"From: {current_msg.source} To: {current_msg.destination}", fontsize=9)
                y_pos -= 0.04
                ax_messages.text(0.1, y_pos, f"Hop: {current_msg.current_hop_count}/{current_msg.hop_limit}", fontsize=9)
                y_pos -= 0.04
                
                # Show current senders
                current_senders = sorted(set(msg.current_node for msg in active_messages))
                ax_messages.text(0.1, y_pos, f"Sending from: {current_senders}", fontsize=8, color='orange')
                y_pos -= 0.04
                
                # Show next receivers
                next_receivers = set()
                for sender_id in current_senders:
                    sender_node = self.nodes[sender_id]
                    for neighbor_id in sender_node.neighbors:
                        neighbor_node = self.nodes[neighbor_id]
                        if not neighbor_node.has_seen_message(current_msg.message_id):
                            next_receivers.add(neighbor_id)
                
                if next_receivers:
                    ax_messages.text(0.1, y_pos, f"Will reach: {sorted(list(next_receivers))}", fontsize=8, color='blue')
                    y_pos -= 0.06
                else:
                    ax_messages.text(0.1, y_pos, "No more neighbors to reach!", fontsize=8, color='red')
                    y_pos -= 0.06
            
            # Show ALL messages with status colors
            if hasattr(self, 'all_simulator_messages'):
                all_messages_to_show = self.all_simulator_messages
                
                ax_messages.text(0.05, y_pos, "All Messages:", fontsize=12, fontweight='bold')
                y_pos -= 0.05
                
                # Sort by creation order
                messages_sorted = sorted(all_messages_to_show, key=lambda m: m.message_id)
                
                for msg in messages_sorted[-8:]:  # Show last 8 messages
                    # Determine status and color
                    if msg.reached_destination:
                        color = 'green'
                        status_text = f"✓ {msg.source}→{msg.destination} (delivered)"
                    elif msg.failed:
                        color = 'red' 
                        status_text = f"✗ {msg.source}→{msg.destination} (failed)"
                    elif msg.active:
                        color = 'blue'
                        # Find current hop count from active messages
                        current_hop = 0
                        if active_messages:
                            for active_msg in active_messages:
                                if active_msg.message_id == msg.message_id:
                                    current_hop = active_msg.current_hop_count
                                    break
                        status_text = f"→ {msg.source}→{msg.destination} (hop {current_hop}/{msg.hop_limit})"
                    else:
                        color = 'black'
                        status_text = f"○ {msg.source}→{msg.destination} (waiting)"
                    
                    ax_messages.text(0.1, y_pos, status_text, fontsize=9, color=color)
                    y_pos -= 0.04
                    
                    if y_pos < 0.2:  # Don't go too low
                        break
            else:
                ax_messages.text(0.05, y_pos, "No messages yet", fontsize=10, color='gray')
                y_pos -= 0.05
            
            # Instructions - always show keyboard controls
            ax_messages.text(0.05, 0.15, "CONTROLS:", fontsize=10, fontweight='bold')
            ax_messages.text(0.05, 0.11, "SPACE = Next step", fontsize=9, color='blue')
            ax_messages.text(0.05, 0.07, "Q = Quit", fontsize=9, color='red')
            ax_messages.text(0.05, 0.03, "Click graph to focus", fontsize=8, style='italic')
            
            # Add legend for colors - UPDATED WITH HISTORY
            legend_elements = [
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='green', markersize=8, label='Source'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Destination'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='orange', markersize=8, label='Visited (history)'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', markersize=8, label='Current path'),
                plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='darkorange', markersize=8, label='Active now'),
                plt.Line2D([0], [0], color='cyan', linewidth=2, label='Historical paths'),
                plt.Line2D([0], [0], color='blue', linewidth=4, label='Current transmission')
            ]
            
            # Add legend to network plot
            ax_network.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
            
            # Add keyboard handler
            def on_key(event):
                if key_callback:
                    key_callback(event.key)
            
            # Add click handler for focusing
            def on_click(event):
                # Just focus the window when clicked
                fig.canvas.draw_idle()
            
            # Connect event handlers
            fig.canvas.mpl_connect('key_press_event', on_key)
            fig.canvas.mpl_connect('button_press_event', on_click)
            
            # Make sure window can receive focus (with error handling)
            try:
                if hasattr(fig.canvas, 'set_window_title'):
                    fig.canvas.set_window_title('Meshtastic Simulator - Press SPACE to advance')
            except (AttributeError, Exception):
                pass  # Some backends don't support this, ignore silently
            
            plt.tight_layout()
            
            # Force update and focus
            plt.draw()
            plt.pause(0.01)
            
            return True  # Visualization succeeded
            
        except Exception as e:
            print(f"Visualization error: {e}")
            print("Continuing without visualization...")
    
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