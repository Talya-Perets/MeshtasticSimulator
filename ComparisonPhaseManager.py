import random
from message import Message

class ComparisonPhaseManager:
    """
    Manages the comparison phase of the simulation
    Handles generation and execution of test messages to compare algorithms
    Enhanced with detailed network and message statistics
    """
    
    def __init__(self, network):
        self.network = network
        self.messages = {}
        self.current_frame = 0
        self.total_frames = 60
        
        # Enhanced statistics tracking
        self.stats = {
            # Basic message statistics
            'messages_completed': 0,
            'messages_reached_target': 0,
            'messages_hop_limit_exceeded': 0,
            'total_collisions': 0,
            'collisions_per_frame': [],
            'active_messages_per_frame': [],
            
            # Network statistics
            'total_transmissions_sent': 0,
            'total_transmissions_received': 0,
            'total_transmissions_attempted': 0,
            'total_collisions_occurred': 0,
            'transmissions_per_frame': [],
            'receptions_per_frame': [],
            'collisions_frame_events': [],
            
            # Per-message detailed statistics
            'message_details': {},
            
            # Algorithm-specific statistics
            'algorithm_name': 'unknown',
            'network_efficiency': 0.0,
            'average_path_length': 0.0,
            'resource_efficiency': 0.0,
        }
        
    def set_algorithm_name(self, algorithm_name):
        """Set the algorithm name for statistics tracking"""
        self.stats['algorithm_name'] = algorithm_name
        print(f"Statistics tracking set for algorithm: {algorithm_name}")
        
    def generate_comparison_messages(self, num_messages):
        """Generate RANDOM comparison messages for algorithm testing"""
        self.messages.clear()
        node_ids = list(self.network.nodes.keys())
        
        print(f"\nComparison phase: {num_messages} random test messages")
        print("Messages will be different each run:")
        
        for msg_id in range(num_messages):
            # Choose random source and target (different nodes)
            source = random.choice(node_ids)
            target = random.choice([n for n in node_ids if n != source])
            
            # Random start frame throughout simulation
            start_frame = random.randint(1, self.total_frames - 4)
            
            # Create message 
            message = Message(msg_id, source, target, self.total_frames)
            message.start_frame = start_frame
            
            self.messages[msg_id] = message
            print(f"  Test Msg {msg_id}: {source} -> {target} (Frame {start_frame})")
        
        print("Messages are random - each run tests different scenarios")
        
        # Initialize statistics arrays
        self.stats['collisions_per_frame'] = [0] * self.total_frames
        self.stats['active_messages_per_frame'] = [0] * self.total_frames
        self.stats['transmissions_per_frame'] = [0] * self.total_frames
        self.stats['receptions_per_frame'] = [0] * self.total_frames
        self.stats['collisions_frame_events'] = [0] * self.total_frames
        
        # Initialize per-message statistics
        self.stats['message_details'] = {msg_id: {
            'message_id': msg_id,
            'source': self.messages[msg_id].source,
            'target': self.messages[msg_id].target,
            'success': False, 
            'final_path': [], 
            'all_paths_discovered': [],
            'path_length': 0,
            'total_transmissions_for_this_message': 0,
            'total_receptions_for_this_message': 0,
            'hops_when_target_reached': 0,
            'frames_to_complete': 0
        } for msg_id in self.messages.keys()}
                
    def record_transmission_statistics(self, transmission_queue, successful_receives, collision_count):
        """Record detailed transmission statistics for current frame"""
        current_frame_idx = self.current_frame - 1
        
        if current_frame_idx < 0 or current_frame_idx >= len(self.stats['transmissions_per_frame']):
            return
            
        # Count total transmission attempts this frame
        total_attempts = len(transmission_queue)
        successful_receptions = len(successful_receives)
        
        # Update frame-specific stats
        self.stats['transmissions_per_frame'][current_frame_idx] = total_attempts
        self.stats['receptions_per_frame'][current_frame_idx] = successful_receptions
        self.stats['collisions_frame_events'][current_frame_idx] = collision_count
        
        # Update cumulative stats
        self.stats['total_transmissions_attempted'] += total_attempts
        self.stats['total_transmissions_sent'] += total_attempts
        self.stats['total_transmissions_received'] += successful_receptions
        self.stats['total_collisions_occurred'] += collision_count
        
        # Update per-message transmission counts
        message_transmission_counts = {}
        for sender_id, receiver_id, message, sender_path, hop_limit in transmission_queue:
            msg_id = message.id
            if msg_id not in message_transmission_counts:
                message_transmission_counts[msg_id] = 0
            message_transmission_counts[msg_id] += 1
            
        for msg_id, count in message_transmission_counts.items():
            if msg_id in self.stats['message_details']:
                self.stats['message_details'][msg_id]['total_transmissions_for_this_message'] += count
        
        # Update per-message reception counts
        message_reception_counts = {}
        for sender_id, receiver_id, msg_id in successful_receives:
            if msg_id not in message_reception_counts:
                message_reception_counts[msg_id] = 0
            message_reception_counts[msg_id] += 1
            
        for msg_id, count in message_reception_counts.items():
            if msg_id in self.stats['message_details']:
                self.stats['message_details'][msg_id]['total_receptions_for_this_message'] += count
        
        print(f"Frame {self.current_frame} stats: {total_attempts} transmissions, {successful_receptions} successful, {collision_count} collisions")
            
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
            message_processor.process_transmissions(self.messages, "comparison", self)
        
        # Count collisions for statistics
        collision_count = sum(1 for node in self.network.nodes.values() 
                            if node.status_flags[node.STATUS_COLLISION])
        
        # Clean up completed comparison messages
        for message in completed_messages:
            self._clear_message_status(message)
            # Update message completion stats
            self._update_message_completion_stats(message)
        
        # Update frame statistics
        self._update_frame_statistics()
        
        self.current_frame += 1
        
        print(f"--- COMPARISON FRAME {self.current_frame} END ---")
        
        return transmission_queue
    
    def _update_message_completion_stats(self, completed_message):
        """Update detailed statistics when a message completes"""
        msg_id = completed_message.id
        if msg_id in self.stats['message_details']:
            details = self.stats['message_details'][msg_id]
            
            # Update completion status
            details['success'] = (completed_message.get_status() == "SUCCESS")
            details['frames_to_complete'] = self.current_frame
            
            # Get final path and all discovered paths
            if completed_message.paths:
                details['final_path'] = completed_message.paths[-1] if completed_message.paths else []
                details['all_paths_discovered'] = completed_message.paths.copy()
                details['path_length'] = len(details['final_path']) - 1 if details['final_path'] else 0
            
            # Record when target was reached
            if completed_message.target_received:
                details['hops_when_target_reached'] = details['path_length']
                
    def _start_messages_for_frame(self):
        """Start messages that should begin this frame"""
        started_messages = []
        
        for message in self.messages.values():
            if message.start_frame == (self.current_frame + 1) and not message.is_active:
                message.start_transmission()
                
                # Mark source and target nodes
                self.network.nodes[message.source].set_as_source(True)
                self.network.nodes[message.target].set_as_target(True)
                
                # Mark that source node has "seen" this message
                source_node = self.network.nodes[message.source]
                if not hasattr(source_node, 'received_message_ids'):
                    source_node.received_message_ids = set()
                source_node.received_message_ids.add(message.id)
                print(f"Source node {message.source} marked Message {message.id} as seen")
                
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
                message._stats_counted = True
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
    
    def calculate_final_metrics(self):
        """Calculate final efficiency metrics"""
        # Network efficiency: successful receptions / total transmissions
        if self.stats['total_transmissions_sent'] > 0:
            self.stats['network_efficiency'] = (self.stats['total_transmissions_received'] / 
                                              self.stats['total_transmissions_sent']) * 100
        
        # Average path length for successful messages
        successful_paths = [details['path_length'] for details in self.stats['message_details'].values() 
                          if details['success'] and details['path_length'] > 0]
        if successful_paths:
            self.stats['average_path_length'] = sum(successful_paths) / len(successful_paths)
        
        # Resource efficiency: successful messages / total transmissions  
        if self.stats['total_transmissions_sent'] > 0:
            self.stats['resource_efficiency'] = (self.stats['messages_reached_target'] / 
                                               self.stats['total_transmissions_sent']) * 100
    
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
            # Clear statistics flag
            if hasattr(message, '_stats_counted'):
                delattr(message, '_stats_counted')
        
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
                
        # Reset enhanced statistics
        algorithm_name = self.stats.get('algorithm_name', 'unknown')
        self.stats = {
            'messages_completed': 0,
            'messages_reached_target': 0,
            'messages_hop_limit_exceeded': 0,
            'total_collisions': 0,
            'collisions_per_frame': [0] * self.total_frames,
            'active_messages_per_frame': [0] * self.total_frames,
            
            # Network statistics
            'total_transmissions_sent': 0,
            'total_transmissions_received': 0,
            'total_transmissions_attempted': 0,
            'total_collisions_occurred': 0,
            'transmissions_per_frame': [0] * self.total_frames,
            'receptions_per_frame': [0] * self.total_frames,
            'collisions_frame_events': [0] * self.total_frames,
            
            # Algorithm-specific statistics
            'algorithm_name': algorithm_name,
            'network_efficiency': 0.0,
            'average_path_length': 0.0,
            'resource_efficiency': 0.0,
            
            # Per-message statistics
            'message_details': {msg_id: {
                'message_id': msg_id,
                'source': self.messages[msg_id].source,
                'target': self.messages[msg_id].target,
                'success': False, 
                'final_path': [], 
                'all_paths_discovered': [],
                'path_length': 0,
                'total_transmissions_for_this_message': 0,
                'total_receptions_for_this_message': 0,
                'hops_when_target_reached': 0,
                'frames_to_complete': 0
            } for msg_id in self.messages.keys()}
        }
        
        print("Comparison simulation reset to frame 0 (keeping learned knowledge trees)")
    
    def get_detailed_statistics(self):
        """Get detailed statistics for algorithm comparison"""
        # Calculate final metrics before returning
        self.calculate_final_metrics()
        
        total_messages = len(self.messages)
        successful = self.stats['messages_reached_target']
        failed = self.stats['messages_hop_limit_exceeded']
        
        # Get per-message details
        message_details = []
        for msg_id, message in self.messages.items():
            details = self.stats['message_details'].get(msg_id, {})
            
            success = message.get_status() == "SUCCESS"
            final_path = message.paths[-1] if message.paths else []
            path_length = len(final_path) - 1 if len(final_path) > 1 else 0
            
            message_details.append({
                'id': msg_id,
                'route': f"{message.source}->{message.target}",
                'success': success,
                'final_path': final_path,
                'all_paths': message.paths.copy(),
                'path_length': path_length,
                'transmissions': details.get('total_transmissions_for_this_message', 0),
                'receptions': details.get('total_receptions_for_this_message', 0),
                'frames_to_complete': details.get('frames_to_complete', 0)
            })
        
        return {
            # Basic message statistics
            'algorithm_name': self.stats['algorithm_name'],
            'total_messages': total_messages,
            'successful': successful,
            'failed': failed,
            'success_rate': (successful / total_messages * 100) if total_messages > 0 else 0,
            
            # Network transmission statistics  
            'total_transmissions_sent': self.stats['total_transmissions_sent'],
            'total_transmissions_received': self.stats['total_transmissions_received'],
            'total_transmissions_attempted': self.stats['total_transmissions_attempted'],
            'network_efficiency': self.stats['network_efficiency'],
            
            # Collision and performance statistics
            'total_collisions': self.stats['total_collisions'],
            'total_collisions_occurred': self.stats['total_collisions_occurred'],
            'frames_completed': self.current_frame,
            
            # Path and efficiency metrics
            'average_path_length': self.stats['average_path_length'],
            'resource_efficiency': self.stats['resource_efficiency'],
            
            # Detailed per-message data
            'message_details': message_details
        }
    
    def show_final_statistics(self):
        """Display final simulation statistics"""
        print("\n" + "="*60)
        print("FINAL SIMULATION STATISTICS")
        print("="*60)
        
        # Calculate final metrics
        self.calculate_final_metrics()
        
        total_messages = len(self.messages)
        successful = self.stats['messages_reached_target']
        expired = self.stats['messages_hop_limit_exceeded']
        
        print(f"Algorithm: {self.stats['algorithm_name'].upper()}")
        print(f"Total Messages: {total_messages}")
        print(f"Successful: {successful} ({successful/total_messages*100:.1f}%)")
        print(f"Expired: {expired} ({expired/total_messages*100:.1f}%)")
        print(f"Total Collisions: {self.stats['total_collisions']}")
        
        # Network statistics
        print(f"\nNetwork Transmission Statistics:")
        print(f"  Total Transmissions Sent: {self.stats['total_transmissions_sent']}")
        print(f"  Total Transmissions Received: {self.stats['total_transmissions_received']}")
        print(f"  Network Efficiency: {self.stats['network_efficiency']:.1f}%")
        print(f"  Resource Efficiency: {self.stats['resource_efficiency']:.3f}%")
        print(f"  Average Path Length: {self.stats['average_path_length']:.1f}")
        
        # Collision statistics
        max_collisions = max(self.stats['collisions_per_frame']) if self.stats['collisions_per_frame'] else 0
        avg_collisions = sum(self.stats['collisions_per_frame']) / len(self.stats['collisions_per_frame']) if self.stats['collisions_per_frame'] else 0
        
        print(f"\nCollision Statistics:")
        print(f"  Max Collisions per Frame: {max_collisions}")
        print(f"  Average Collisions per Frame: {avg_collisions:.1f}")
        print(f"  Total Collision Events: {self.stats['total_collisions_occurred']}")
        
        # Message path analysis
        print(f"\nMessage Path Analysis:")
        for msg_id, message in self.messages.items():
            details = self.stats['message_details'].get(msg_id, {})
            print(f"Message {msg_id} ({message.source}->{message.target}):")
            print(f"  Status: {message.get_status()}")
            print(f"  Total paths discovered: {len(message.paths)}")
            print(f"  Transmissions: {details.get('total_transmissions_for_this_message', 0)}")
            print(f"  Successful receptions: {details.get('total_receptions_for_this_message', 0)}")
            
            if message.paths:
                shortest_path = min(message.paths, key=len)
                longest_path = max(message.paths, key=len)
                print(f"  Shortest path: {shortest_path} (length: {len(shortest_path)})")
                print(f"  Longest path: {longest_path} (length: {len(longest_path)})")
                if message.get_status() == "SUCCESS":
                    final_path = message.paths[-1] if message.paths else []
                    print(f"  Final successful path: {final_path}")
        
        print("="*60)