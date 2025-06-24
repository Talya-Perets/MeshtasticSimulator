class MessageProcessor:
    """
    Handles message transmission, collision detection, and reception processing
    Shared logic for both learning and comparison phases
    Enhanced with detailed statistics tracking
    """
    
    def __init__(self, network):
        self.network = network
        self.algorithm_mode = "flooding"  # Default algorithm
        
    def set_algorithm_mode(self, mode):
        """Set the algorithm mode: 'flooding' or 'tree'"""
        self.algorithm_mode = mode
        print(f"🔧 MessageProcessor algorithm mode set to: {mode}")
        
    def process_transmissions(self, messages, message_type="learning", stats_manager=None):
        """
        Process all message transmissions for current frame
        
        Args:
            messages: Dictionary of messages to process
            message_type: "learning" or "comparison" for different handling
            stats_manager: ComparisonPhaseManager for statistics tracking (optional)
            
        Returns:
            tuple: (transmission_queue, sending_nodes, successful_receives, completed_messages)
        """
        # Phase 1: Check for expired messages and collect transmissions
        expired_messages = self._check_expired_messages(messages, message_type)
        transmission_queue, sending_nodes = self._collect_transmissions(messages, message_type)
        
        # Phase 2: Detect collisions
        collision_nodes = self._detect_collisions(transmission_queue)
        
        # Phase 3: Process successful receptions
        successful_receives = self._process_receptions(transmission_queue, collision_nodes)
        
        # Phase 4: Process received messages and build knowledge trees
        completed_messages = self._process_received_messages(collision_nodes, message_type, messages)
        
        # Phase 5: Clean up colors for expired/stalled messages (FIXED!)
        for message in expired_messages:
            if message.is_completed:
                self._immediate_color_cleanup(message, message_type, messages)
        
        # Phase 6: Record statistics if stats manager provided (for comparison phase)
        if stats_manager and message_type == "comparison":
            collision_count = len(collision_nodes)
            stats_manager.record_transmission_statistics(transmission_queue, successful_receives, collision_count)
        
        # Print summary
        self._print_transmission_summary(sending_nodes, successful_receives, completed_messages, message_type)
        
        return transmission_queue, sending_nodes, successful_receives, completed_messages
    
    def _check_expired_messages(self, messages, message_type):
        """Check for messages that have exceeded their hop limit"""
        expired_messages = []
        
        for node in self.network.nodes.values():
            expired_indices = []
            for i, pending_item in enumerate(node.pending_messages):
                if len(pending_item) >= 3:
                    message, path, local_hop_limit = pending_item
                    if local_hop_limit <= 0 and not message.is_completed:
                        expired_messages.append(message)
                        message.complete_message("hop_limit_exceeded")
                        expired_indices.append(i)
                elif len(pending_item) == 2:
                    # Handle old format
                    message, path = pending_item
                    hops_used = len(path) - 1
                    local_hop_limit = message.hop_limit - hops_used
                    if local_hop_limit <= 0 and not message.is_completed:
                        expired_messages.append(message)
                        message.complete_message("hop_limit_exceeded")
                        expired_indices.append(i)
            
            # Remove expired messages from pending (in reverse order)
            for i in reversed(expired_indices):
                node.pending_messages.pop(i)
        
        if expired_messages:
            print(f"Expired {message_type} messages:")
            for msg in expired_messages:
                print(f"  Message {msg.id}: Hop limit exceeded")
        
        # Check for stalled messages (no pending copies anywhere)
        stalled_messages = self._check_stalled_messages(messages)
        expired_messages.extend(stalled_messages)  # Add stalled messages to cleanup list
        
        return expired_messages
    
    def _check_stalled_messages(self, messages):
        """Check for messages that have no pending copies and should be completed"""
        stalled_messages = []
        
        for message in messages.values():
            if message.is_active and not message.is_completed:
                # Check if this message has any pending copies anywhere
                has_pending = False
                
                for node in self.network.nodes.values():
                    for pending_item in node.pending_messages:
                        if len(pending_item) >= 2:
                            pending_msg = pending_item[0]
                            if pending_msg.id == message.id:
                                has_pending = True
                                break
                    if has_pending:
                        break
                
                if not has_pending:
                    stalled_messages.append(message)
                    message.complete_message("hop_limit_exceeded")
        
        if stalled_messages:
            print("Stalled messages completed:")
            for msg in stalled_messages:
                print(f"  Message {msg.id}: No pending copies remaining")
        
        return stalled_messages  # Return the list so colors can be cleaned up
    
    def _collect_transmissions(self, messages, message_type):
        """Collect all transmissions from all nodes"""
        transmission_queue = []
        sending_nodes = []
        
        for sender_id, sender_node in self.network.nodes.items():
            if sender_node.pending_messages:
                # Filter out completed/inactive messages
                active_pending = self._filter_active_messages(sender_node.pending_messages)
                sender_node.pending_messages = active_pending
                
                # Get transmissions from this node
                node_transmissions = self._get_node_transmissions(sender_id, sender_node, active_pending, message_type)
                
                if node_transmissions:
                    transmission_queue.extend(node_transmissions)
                    sender_node.set_sending()
                    sending_nodes.append(sender_id)
                
                # Clear pending messages after processing
                sender_node.pending_messages.clear()
        
        return transmission_queue, sending_nodes
    
    def _filter_active_messages(self, pending_messages):
        """Filter out completed/inactive messages from pending list"""
        active_pending = []
        
        for pending_item in pending_messages:
            if len(pending_item) == 2:
                # Old format - calculate hop limit
                message, current_path = pending_item
                hops_used = len(current_path) - 1
                local_hop_limit = message.hop_limit - hops_used
            else:
                # New format - hop limit already calculated
                message, current_path, local_hop_limit = pending_item
            
            if message.is_completed:
                continue
            elif not message.is_active:
                continue
            elif local_hop_limit <= 0:
                # Complete the message when hop limit is exhausted
                if not message.is_completed:
                    message.complete_message("hop_limit_exceeded")
                continue
            else:
                active_pending.append((message, current_path, local_hop_limit))
        
        return active_pending
    
    def _get_node_transmissions(self, sender_id, sender_node, active_pending, message_type):
        """Get all transmissions from a specific node"""
        transmissions = []
        
        for message, current_path, local_hop_limit in active_pending:
            # Determine which algorithm to use
            if message_type == "learning":
                # Learning phase always uses flooding
                algorithm_mode = "flooding"
            else:
                # Comparison phase uses the selected algorithm
                algorithm_mode = self.algorithm_mode
            
            valid_neighbors = sender_node.get_routing_decision(message, local_hop_limit, algorithm_mode)
            
            for neighbor_id in valid_neighbors:
                transmissions.append((sender_id, neighbor_id, message, current_path, local_hop_limit))
        
        return transmissions
    
    def _detect_collisions(self, transmission_queue):
        """Detect collision nodes (multiple senders to same receiver)"""
        transmissions_by_receiver = {}
        
        # Group transmissions by receiver
        for sender_id, receiver_id, message, sender_path, hop_limit in transmission_queue:
            if receiver_id not in transmissions_by_receiver:
                transmissions_by_receiver[receiver_id] = []
            transmissions_by_receiver[receiver_id].append((sender_id, message, sender_path, hop_limit))
        
        # Check for collisions and mark nodes
        collision_nodes = set()
        for receiver_id, transmissions in transmissions_by_receiver.items():
            if len(transmissions) > 1:
                # COLLISION: Multiple senders sending to same receiver
                collision_nodes.add(receiver_id)
                sender_list = [sender_id for sender_id, _, _, _ in transmissions]
                message_list = [message.id for _, message, _, _ in transmissions]
                print(f"COLLISION at node {receiver_id} from nodes {sender_list} (messages {message_list})")
                
                # Mark receiver as having collision
                self.network.nodes[receiver_id].set_collision()
        
        return collision_nodes
    
    def _process_receptions(self, transmission_queue, collision_nodes):
        """Process successful message receptions (no collisions)"""
        successful_receives = []
        
        for sender_id, receiver_id, message, sender_path, hop_limit in transmission_queue:
            receiver_node = self.network.nodes[receiver_id]
            
            if receiver_id in collision_nodes:
                # This receiver has collision - reject ALL messages
                pass  # No processing for collided transmissions
            else:
                # No collision - try to receive normally
                accepted = receiver_node.receive_message_copy(message, sender_id, sender_path)
                
                if accepted:
                    successful_receives.append((sender_id, receiver_id, message.id))
        
        return successful_receives
    
    def _process_received_messages(self, collision_nodes, message_type, messages):
        """Process received messages and build knowledge trees"""
        completed_messages_this_frame = []
        receiving_nodes = []
        
        for node_id, node in self.network.nodes.items():
            if node_id in collision_nodes:
                # Clear any received messages due to collision
                node.received_messages.clear()
                continue
                
            if node.received_messages:
                node.set_receiving()
                receiving_nodes.append(node_id)
                
                # Print detailed reception info for learning mode
                if message_type == "learning":
                    print(f"\n🔍 Node {node_id} processing received {message_type} messages:")
                    for msg_copy in node.received_messages:
                        if len(msg_copy) >= 3:
                            message, sender_id, sender_path = msg_copy
                            print(f"  📨 Message {message.id} from node {sender_id}")
                            print(f"      Path so far: {' → '.join(map(str, sender_path))}")
                
                # Process the received messages and build knowledge trees
                processed = node.process_received_messages()
                
                for message, path in processed:
                    if message.is_completed:
                        completed_messages_this_frame.append(message)
                        if message_type == "learning":
                            print(f"✅ Learning Message {message.id} completed at node {node_id}")
                        # Clean up colors for completed message
                        self._immediate_color_cleanup(message, message_type, messages)
        
        return completed_messages_this_frame
    
    def _immediate_color_cleanup(self, completed_message, message_type, all_messages):
        """Immediately clean up colors when a message completes - FIXED VERSION"""
        if message_type == "learning":
            print(f"🧹 Immediate cleanup for Learning Message {completed_message.id}")
        else:
            print(f"🧹 Immediate cleanup for Comparison Message {completed_message.id}")
        
        source_id = completed_message.source
        target_id = completed_message.target
        
        # Check if source/target nodes have other active messages
        source_has_other = any(
            msg.is_active and not msg.is_completed and msg.source == source_id
            for msg in all_messages.values()
            if msg != completed_message
        )
        target_has_other = any(
            msg.is_active and not msg.is_completed and msg.target == target_id 
            for msg in all_messages.values()
            if msg != completed_message
        )
        
        # Clear colors if no other active messages
        if not source_has_other:
            self.network.nodes[source_id].set_as_source(False)
            print(f"  🎨 Cleared SOURCE color from node {source_id}")
            
        if not target_has_other:
            self.network.nodes[target_id].set_as_target(False)
            print(f"  🎨 Cleared TARGET color from node {target_id}")
    
    def _print_transmission_summary(self, sending_nodes, successful_receives, completed_messages, message_type):
        """Print summary of transmission results with enhanced statistics"""
        if sending_nodes:
            algorithm_text = f"({self.algorithm_mode})" if message_type == "comparison" else ""
            print(f"{message_type.title()} transmissions {algorithm_text} from nodes: {sending_nodes}")
        
        if successful_receives:
            print(f"Successful {message_type} transmissions:")
            for sender_id, receiver_id, msg_id in successful_receives:
                print(f"  {sender_id} -> {receiver_id} (Message {msg_id})")
        
        if completed_messages:
            print(f"\n🎯 {message_type.title()} messages completed this frame:")
            for msg in completed_messages:
                status = "SUCCESS" if msg.get_status() == "SUCCESS" else "FAILED"
                print(f"  ✅ Message {msg.id} ({msg.source}→{msg.target}): {status}")
        else:
            print(f"\n📝 No {message_type} messages completed this frame")