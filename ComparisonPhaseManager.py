import random
from message import Message

class ComparisonPhaseManager:
    """
    Manages the comparison phase of the simulation
    Handles generation and execution of test messages to compare algorithms
    """
    
    def __init__(self, network):
        self.network = network
        self.messages = {}
        self.current_frame = 0
        self.total_frames = 60
        self.stats = {
            'messages_completed': 0,
            'messages_reached_target': 0,
            'messages_hop_limit_exceeded': 0,
            'total_collisions': 0,
            'collisions_per_frame': [],
            'active_messages_per_frame': []
        }
        
    def generate_comparison_messages(self, num_messages):
        """Generate RANDOM comparison messages for algorithm testing"""
        self.messages.clear()
        node_ids = list(self.network.nodes.keys())
        
        # NO SEED - completely random messages each run!
        print(f"\n🔬 COMPARISON PHASE: {num_messages} RANDOM test messages")
        print("These messages will be DIFFERENT each run:")
        
        for msg_id in range(num_messages):
            # Choose random source and target (different nodes)
            source = random.choice(node_ids)
            target = random.choice([n for n in node_ids if n != source])
            
            # Random start frame throughout simulation
            start_frame = random.randint(1, self.total_frames - 4)
            
            # Create message 
            message = Message(msg_id, source, target, self.total_frames)
            message.start_frame = start_frame  # Override with random start
            
            self.messages[msg_id] = message
            print(f"  Test Msg {msg_id}: {source} → {target} (Frame {start_frame})")
        
        print(f"🎲 Messages are completely RANDOM - each run tests different scenarios!")
        
        # Initialize statistics arrays
        self.stats['collisions_per_frame'] = [0] * self.total_frames
        self.stats['active_messages_per_frame'] = [0] * self.total_frames
                
    def execute_comparison_frame(self, message_processor):
        """Execute one comparison frame"""
        print(f"\n--- COMPARISON FRAME {self.current_frame + 1} START ---")
        
        # Reset all nodes FIRST (clear old status)
        for node in self.network.nodes.values():
            node.reset_frame_status()
        
        # Re-mark source and target nodes for ACTIVE messages only
        for message in self.messages.values():
            if message.is_active and not message.is_completed:
                self.network.nodes[message.source].set_as_source(True)
                self.network.nodes[message.target].set_as_target(True)
        
        # Start messages that begin this frame
        self._start_messages_for_frame()
        
        # Process message transmissions using the message processor
        transmission_queue, sending_nodes, successful_receives, completed_messages = \
            message_processor.process_transmissions(self.messages, "comparison")
        
        # Clean up completed comparison messages
        for message in completed_messages:
            self._clear_message_status(message)
        
        # Update statistics
        self._update_frame_statistics()
        
        self.current_frame += 1
        
        print(f"--- COMPARISON FRAME {self.current_frame} END ---")
        
        return transmission_queue
    
    def _start_messages_for_frame(self):
        """Start messages that should begin this frame"""
        started_messages = []
        
        for message in self.messages.values():
            if message.start_frame == (self.current_frame + 1) and not message.is_active:
                message.start_transmission()
                
                # Mark source and target nodes
                self.network.nodes[message.source].set_as_source(True)
                self.network.nodes[message.target].set_as_target(True)
                
                # Add message to source node's pending list
                initial_path = [message.source]
                self.network.nodes[message.source].pending_messages.append((message, initial_path))
                
                started_messages.append(f"Message {message.id}: {message.source} -> {message.target}")
        
        if started_messages:
            print("Messages started:")
            for msg in started_messages:
                print(f"  {msg}")
    
    def _update_frame_statistics(self):
        """Update statistics for current frame"""
        # Count active messages
        active_count = sum(1 for m in self.messages.values() if m.is_active)
        if self.current_frame <= len(self.stats['active_messages_per_frame']):
            # Extend array if needed
            while len(self.stats['active_messages_per_frame']) < self.current_frame:
                self.stats['active_messages_per_frame'].append(0)
            if self.current_frame > 0:
                self.stats['active_messages_per_frame'][self.current_frame - 1] = active_count
        
        # Count collisions this frame
        collision_count = sum(1 for node in self.network.nodes.values() 
                            if node.status_flags[node.STATUS_COLLISION])
        if self.current_frame <= len(self.stats['collisions_per_frame']):
            # Extend array if needed
            while len(self.stats['collisions_per_frame']) < self.current_frame:
                self.stats['collisions_per_frame'].append(0)
            if self.current_frame > 0:
                self.stats['collisions_per_frame'][self.current_frame - 1] = collision_count
                self.stats['total_collisions'] += collision_count
        
        # Count completed messages (but don't double count)
        newly_completed = []
        for message in self.messages.values():
            if message.is_completed and not hasattr(message, '_stats_counted'):
                message._stats_counted = True  # Mark as counted
                newly_completed.append(message)
                
                # Use the message's own status
                if message.get_status() == "SUCCESS":
                    self.stats['messages_reached_target'] += 1
                else:
                    self.stats['messages_hop_limit_exceeded'] += 1
        
        # Print frame summary
        if newly_completed:
            print("Messages completed:")
            for msg in newly_completed:
                status = "SUCCESS" if msg.get_status() == "SUCCESS" else "FAILED"
                print(f"  Message {msg.id}: {status}")
        
        if collision_count > 0:
            print(f"Collisions detected: {collision_count}")
    
    def _clear_message_status(self, completed_message):
        """Clear source/target status when message completes"""
        source_id = completed_message.source
        target_id = completed_message.target
        message_id = completed_message.id
        
        # Remove this message from ALL nodes' pending_messages
        for node in self.network.nodes.values():
            new_pending = []
            for pending_item in node.pending_messages:
                if len(pending_item) == 2:
                    msg, path = pending_item
                    if msg.id != message_id:
                        new_pending.append(pending_item)
                elif len(pending_item) == 3:
                    msg, path, hop_limit = pending_item
                    if msg.id != message_id:
                        new_pending.append(pending_item)
            node.pending_messages = new_pending
        
        # Check if source has OTHER active messages
        source_has_other_active = any(
            msg.is_active and not msg.is_completed and msg.source == source_id 
            for msg in self.messages.values() 
            if msg != completed_message
        )
        if not source_has_other_active:
            self.network.nodes[source_id].set_as_source(False)
            
        # Check if target has OTHER active messages
        target_has_other_active = any(
            msg.is_active and not msg.is_completed and msg.target == target_id 
            for msg in self.messages.values() 
            if msg != completed_message
        )
        if not target_has_other_active:
            self.network.nodes[target_id].set_as_target(False)
    
    def is_complete(self):
        """Check if comparison phase is complete"""
        return (self.current_frame >= self.total_frames or 
                all(msg.is_completed for msg in self.messages.values()))
    
    def reset_simulation(self):
        """Reset simulation to initial state"""
        self.current_frame = 0
        
        # Reset all messages
        for message in self.messages.values():
            message.is_active = False
            message.is_completed = False
            message.completion_reason = None
            message.current_hops = message.hop_limit
            message.paths.clear()
            message.active_copies.clear()
            
        # Reset all nodes (but keep knowledge trees from learning!)
        for node in self.network.nodes.values():
            node.reset_frame_status()
            node.set_as_source(False)
            node.set_as_target(False)
            node.pending_messages.clear()
            node.received_messages.clear()
            if hasattr(node, 'seen_message_copies'):
                node.seen_message_copies.clear()
            if hasattr(node, 'received_message_ids'):
                node.received_message_ids.clear()
            # DON'T reset knowledge trees - they're from learning phase!
                
        # Reset statistics
        self.stats = {
            'messages_completed': 0,
            'messages_reached_target': 0,
            'messages_hop_limit_exceeded': 0,
            'total_collisions': 0,
            'collisions_per_frame': [0] * self.total_frames,
            'active_messages_per_frame': [0] * self.total_frames
        }
        
        print("Comparison simulation reset to frame 0 (keeping learned knowledge trees)")
    
    def show_final_statistics(self):
        """Display final simulation statistics"""
        print("\n" + "="*60)
        print("FINAL SIMULATION STATISTICS")
        print("="*60)
        
        total_messages = len(self.messages)
        successful = self.stats['messages_reached_target']
        expired = self.stats['messages_hop_limit_exceeded']
        
        print(f"Total Messages: {total_messages}")
        print(f"Successful: {successful} ({successful/total_messages*100:.1f}%)")
        print(f"Expired: {expired} ({expired/total_messages*100:.1f}%)")
        print(f"Total Collisions: {self.stats['total_collisions']}")
        
        # Collision statistics
        max_collisions = max(self.stats['collisions_per_frame']) if self.stats['collisions_per_frame'] else 0
        avg_collisions = sum(self.stats['collisions_per_frame']) / len(self.stats['collisions_per_frame']) if self.stats['collisions_per_frame'] else 0
        
        print(f"Max Collisions per Frame: {max_collisions}")
        print(f"Average Collisions per Frame: {avg_collisions:.1f}")
        
        # Message path analysis
        print(f"\nMessage Path Analysis:")
        for msg_id, message in self.messages.items():
            print(f"Message {msg_id} ({message.source}→{message.target}):")
            print(f"  Total paths discovered: {len(message.paths)}")
            if message.paths:
                shortest_path = min(message.paths, key=len)
                longest_path = max(message.paths, key=len)
                print(f"  Shortest path: {shortest_path} (length: {len(shortest_path)})")
                print(f"  Longest path: {longest_path} (length: {len(longest_path)})")
        
        # FINAL KNOWLEDGE TREES SUMMARY
        print(f"\n🌳 FINAL KNOWLEDGE TREES SUMMARY:")
        print("="*60)
        for node_id in sorted(self.network.nodes.keys()):
            node = self.network.nodes[node_id]
            if node.knowledge_tree:
                print(f"\n📍 Node {node_id} Final Tree:")
                node.print_knowledge_tree()
            else:
                print(f"\n📍 Node {node_id}: No knowledge learned")
                
        print("="*60)