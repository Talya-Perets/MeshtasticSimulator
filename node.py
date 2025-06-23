class Node:
    """
    Represents a node in the network
    Each node has status, position, and message handling capabilities
    Now with Tree Building capabilities and Tree-Based Routing
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
        
        # TREE STRUCTURE: Each node builds a tree of known paths
        self.knowledge_tree = {}  # {destination_node: {parent: node_id, children: [node_ids], distance: int, learned_frame: int}}
        
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

    def get_routing_decision(self, message, hop_limit_remaining, algorithm_mode="flooding"):
        """Routing decision based on selected algorithm"""
        source = message.source
        target = message.target
        
        # FIRST CHECK: If I'm the target, never forward (for both algorithms)
        if target == self.id:
            if algorithm_mode == "flooding":
                print(f"📋 Node {self.id} flooding decision for Message {message.id} ({source}→{target}):")
                print(f"   🎯 I AM THE TARGET - not forwarding")
            else:
                print(f"📋 Node {self.id} tree-based decision for Message {message.id} ({source}→{target}):")
                print(f"   🎯 I AM THE TARGET - not forwarding")
            return []
        
        if algorithm_mode == "flooding":
            return self._flooding_decision(message, hop_limit_remaining)
        else:
            return self._tree_based_decision(message, hop_limit_remaining)
    
    def _flooding_decision(self, message, hop_limit_remaining):
        """FLOODING ALGORITHM: Send to all neighbors (except if I'm target)"""
        source = message.source
        target = message.target
        
        print(f"📋 Node {self.id} flooding decision for Message {message.id} ({source}→{target}):")
        print(f"   Hop limit remaining: {hop_limit_remaining}")
        print(f"   ✅ Decision: PURE FLOODING to all neighbors {list(self.neighbors)}")
        
        # Always return all neighbors - pure flooding
        return list(self.neighbors)
    
    def _tree_based_decision(self, message, hop_limit_remaining):
        """TREE-BASED ALGORITHM: Use knowledge tree for smart routing"""
        source = message.source
        target = message.target
        
        print(f"📋 Node {self.id} tree-based decision for Message {message.id} ({source}→{target}):")
        print(f"   Hop limit remaining: {hop_limit_remaining}")
        
        # Check if both source and target are in my knowledge tree
        source_in_tree = source in self.knowledge_tree
        target_in_tree = target in self.knowledge_tree
        
        print(f"   Source {source} in tree: {source_in_tree}")
        print(f"   Target {target} in tree: {target_in_tree}")
        
        # If I don't know about both source and target, flood to all neighbors
        if not (source_in_tree and target_in_tree):
            print(f"   ✅ Decision: FLOOD (missing knowledge) to all neighbors {list(self.neighbors)}")
            return list(self.neighbors)
        
        # Both source and target are in my tree - check if they're in same subtree
        print(f"   Both source and target known - checking subtrees...")
        
        # Check if source and target are in the same subtree
        if self._are_in_same_subtree(source, target):
            print(f"   🚫 Decision: DON'T SEND - source and target in same subtree")
            print(f"      → There's a path {source}→{target} that doesn't go through me")
            return []  # Don't send to anyone
        else:
            # They're in different subtrees - flood to all neighbors
            print(f"   ✅ Decision: FLOOD (different subtrees) to all neighbors {list(self.neighbors)}")
            return list(self.neighbors)

    def _are_in_same_subtree(self, source, target):
        """Check if source and target are in the same subtree"""
        
        # Get all my direct children in the tree
        my_direct_children = self._get_direct_children()
        
        print(f"      My direct children: {my_direct_children}")
        
        # Check each subtree - if ANY subtree contains both source and target, return True
        for child in my_direct_children:
            source_in_subtree = self._is_in_subtree(source, child)
            target_in_subtree = self._is_in_subtree(target, child)
            
            print(f"      Child {child}: source({source})={source_in_subtree}, target({target})={target_in_subtree}")
            
            if source_in_subtree and target_in_subtree:
                print(f"      ✅ Both source and target found in subtree of child {child}")
                return True
        
        print(f"      ❌ No single subtree contains both source and target")
        return False

    def _get_direct_children(self):
        """Get all direct children of this node in the knowledge tree"""
        direct_children = []
        for dest, info in self.knowledge_tree.items():
            if info['parent'] == self.id:
                direct_children.append(dest)
        return direct_children

    def _is_in_subtree(self, node, subtree_root):
        """Check if a node is in the subtree rooted at subtree_root"""
        if node == subtree_root:
            return True
        
        # Check if node exists in tree and its path goes through subtree_root
        if node not in self.knowledge_tree:
            return False
        
        # Follow the path from node back to me - if it goes through subtree_root, it's in that subtree
        current = node
        while current != self.id:
            if current == subtree_root:
                return True
            
            if current not in self.knowledge_tree:
                return False
                
            current = self.knowledge_tree[current]['parent']
            
            # Safety check
            if current == node:  # Avoid infinite loops
                break
        
        return False

    def build_knowledge_tree_from_message(self, message_source, path, current_frame):
        """Build knowledge tree from received message path - learn ALL paths even if destination already known"""
        if len(path) < 2:
            return  # No tree info to learn
        
        # Find my position in the path
        try:
            my_index = path.index(self.id)
        except ValueError:
            print(f"      ⚠️ Node {self.id} not found in path {path}")
            return
        
        print(f"      🌳 Node {self.id} building tree from path: {' → '.join(map(str, path))}")
        
        # Build tree by learning the REVERSE path (from me back to source)
        # This creates a tree showing how to reach all nodes in the path
        for i in range(my_index):
            target_node = path[i]
            distance_to_target = my_index - i
            
            # The next hop is always my direct neighbor in the path (the one who sent me the message)
            next_hop = path[my_index - 1] if my_index > 0 else None
            
            # The parent in the tree is the next node in the path towards the target
            if distance_to_target == 1:
                # Direct neighbor
                parent_in_tree = self.id
            else:
                # The parent is the next node in the path towards the target
                parent_in_tree = path[i + 1]
            
            # ALWAYS add to knowledge tree - learn every path, even duplicate destinations
            self.knowledge_tree[target_node] = {
                'parent': parent_in_tree,
                'distance': distance_to_target,
                'learned_frame': current_frame,
                'next_hop': next_hop
            }
            print(f"         🌲 Tree entry: {target_node} (distance: {distance_to_target}, parent: {parent_in_tree})")

    def process_received_messages(self, current_frame=0):
        """Process all message copies received this frame with tree building"""
        processed_messages = []
        for message, sender_id, sender_path in self.received_messages:
            
            # Create new path
            new_path = message.create_new_copy(sender_id, self.id, sender_path)
            
            # BUILD TREE: Update knowledge tree from this message
            self.build_knowledge_tree_from_message(message.source, new_path, current_frame)
            
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
    
    def print_knowledge_tree(self):
        """Print current knowledge tree as actual tree structure"""
        print(f"      🌳 Node {self.id} Knowledge Tree:")
        if not self.knowledge_tree:
            print(f"         (empty)")
            return
        
        # Build the actual tree structure
        self._print_tree_structure()
    
    def _print_tree_structure(self):
        """Print the tree showing the path structure from me to all known destinations"""
        # Start from myself as root
        print(f"         {self.id} (ME)")
        
        # Find all direct children (nodes with parent = me)
        direct_children = []
        for node, info in self.knowledge_tree.items():
            if info['parent'] == self.id:
                direct_children.append(node)
        
        # Sort for consistent output
        direct_children.sort()
        
        # Print each direct child and its subtree
        for i, child in enumerate(direct_children):
            is_last = (i == len(direct_children) - 1)
            self._print_subtree(child, "", is_last, set())
    
    def _print_subtree(self, node, prefix, is_last, printed_nodes):
        """Print a subtree starting from given node"""
        if node in printed_nodes:
            return
        printed_nodes.add(node)
        
        # Print current node
        connector = "└── " if is_last else "├── "
        distance = self.knowledge_tree.get(node, {}).get('distance', '?')
        print(f"         {prefix}{connector}{node} (d:{distance})")
        
        # Find children of this node
        children = []
        for other_node, info in self.knowledge_tree.items():
            if info['parent'] == node and other_node not in printed_nodes:
                children.append(other_node)
        
        # Sort children for consistent output
        children.sort()
        
        # Print each child
        for i, child in enumerate(children):
            is_child_last = (i == len(children) - 1)
            child_prefix = prefix + ("    " if is_last else "│   ")
            self._print_subtree(child, child_prefix, is_child_last, printed_nodes)

    def get_tree_summary(self):
        """Get a summary of the knowledge tree for display"""
        if not self.knowledge_tree:
            return "Empty tree"
        
        summary_lines = []
        for dest, info in sorted(self.knowledge_tree.items()):
            summary_lines.append(f"→{dest} (d:{info['distance']}, via:{info['next_hop']})")
        
        return " | ".join(summary_lines)

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
        tree_summary = self.get_tree_summary()
        return f"Node {self.id} at ({self.x:.1f}, {self.y:.1f}) | Status: {active_statuses} | Tree: {tree_summary}"