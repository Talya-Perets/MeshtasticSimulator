from collections import deque
import random

class RoutingAlgorithm:
    """Base class for routing algorithms"""
    
    def __init__(self, network):
        self.network = network
    
    def route_message(self, message):
        """Route a message through the network - to be implemented by subclasses"""
        raise NotImplementedError

class FloodingRouter(RoutingAlgorithm):
    """Simple flooding algorithm - send to all neighbors except sender"""
    
    def __init__(self, network):
        super().__init__(network)
        self.name = "Flooding"
    
    def route_message(self, message):
        """Route message using flooding algorithm"""
        current_node_id = message.current_node
        
        # Check if message reached destination
        if current_node_id == message.destination:
            message.mark_as_arrived()
            return []
        
        # Check if message can still hop
        if not message.can_hop():
            message.mark_as_failed("Hop limit reached")
            return []
        
        current_node = self.network.nodes[current_node_id]
        next_hops = []
        
        # Send to all neighbors that haven't seen this message
        for neighbor_id in current_node.neighbors:
            neighbor = self.network.nodes[neighbor_id]
            
            # Don't send back to previous node in path
            if len(message.path) > 1 and neighbor_id == message.path[-2]:
                continue
            
            # Don't send if neighbor already processed this message
            if not neighbor.has_seen_message(message.message_id):
                next_hops.append(neighbor_id)
        
        # Mark current node as having sent this message
        current_node.mark_message_as_sent(message.message_id)
        
        return next_hops

class GreedyRouter(RoutingAlgorithm):
    """Greedy routing - send to neighbor closest to destination"""
    
    def __init__(self, network):
        super().__init__(network)
        self.name = "Greedy"
    
    def route_message(self, message):
        """Route message using greedy algorithm"""
        current_node_id = message.current_node
        
        # Check if message reached destination
        if current_node_id == message.destination:
            message.mark_as_arrived()
            return []
        
        # Check if message can still hop
        if not message.can_hop():
            message.mark_as_failed("Hop limit reached")
            return []
        
        current_node = self.network.nodes[current_node_id]
        destination_node = self.network.nodes[message.destination]
        
        # Find neighbor closest to destination
        best_neighbor = None
        best_distance = float('inf')
        
        for neighbor_id in current_node.neighbors:
            # Don't send back to previous node
            if len(message.path) > 1 and neighbor_id == message.path[-2]:
                continue
            
            neighbor = self.network.nodes[neighbor_id]
            
            # Don't send if neighbor already processed this message
            if neighbor.has_seen_message(message.message_id):
                continue
            
            distance = neighbor.distance_from(destination_node)
            if distance < best_distance:
                best_distance = distance
                best_neighbor = neighbor_id
        
        # Mark current node as having sent this message
        current_node.mark_message_as_sent(message.message_id)
        
        if best_neighbor is not None:
            return [best_neighbor]
        else:
            message.mark_as_failed("No valid neighbors")
            return []

class HybridRouter(RoutingAlgorithm):
    """Hybrid routing - combines flooding and greedy approaches"""
    
    def __init__(self, network, flooding_threshold=3):
        super().__init__(network)
        self.name = "Hybrid"
        self.flooding_threshold = flooding_threshold
    
    def route_message(self, message):
        """Route message using hybrid algorithm"""
        current_node_id = message.current_node
        
        # Check if message reached destination
        if current_node_id == message.destination:
            message.mark_as_arrived()
            return []
        
        # Check if message can still hop
        if not message.can_hop():
            message.mark_as_failed("Hop limit reached")
            return []
        
        current_node = self.network.nodes[current_node_id]
        
        # Use flooding for first few hops, then switch to greedy
        if message.current_hop_count < self.flooding_threshold:
            # Use flooding
            flooding_router = FloodingRouter(self.network)
            return flooding_router.route_message(message)
        else:
            # Use greedy
            greedy_router = GreedyRouter(self.network)
            return greedy_router.route_message(message)