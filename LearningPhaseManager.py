import random
from message import Message

class LearningPhaseManager:
    """
    Manages the learning phase of the simulation
    Handles generation and execution of learning messages to build knowledge trees
    """
    
    def __init__(self, network):
        self.network = network
        self.learning_messages = {}
        self.current_frame = 0
        self.learning_frames = 0
        self.learning_complete = False
        
    def generate_learning_messages(self, num_nodes):
        """Generate predetermined learning messages for network topology learning"""
        self.learning_messages.clear()
        learning_pairs = self._get_learning_pairs(num_nodes)
        
        print(f"\nLearning phase: {len(learning_pairs)} predetermined message pairs")
        print("Messages will be sent every 4 frames:")
        
        msg_id = 0
        current_frame = 1
        message_interval = 4  # New message every 4 frames
        
        for source, target in learning_pairs:
            message = Message(msg_id, source, target, current_frame + 20)
            message.start_frame = current_frame
            message.hop_limit = 4
            
            self.learning_messages[msg_id] = message
            print(f"  Learning Msg {msg_id}: {source} -> {target} (Frame {current_frame})")
            
            msg_id += 1
            current_frame += message_interval
        
        self.learning_frames = current_frame - 1
        print(f"Learning phase will take approximately {self.learning_frames} frames")
        return self.learning_frames
    
    def _get_learning_pairs(self, num_nodes):
        """Get predetermined learning message pairs for each graph size"""
        original_state = random.getstate()
        random.seed(num_nodes * 1000)  # Deterministic seed
        
        try:
            node_ids = list(range(num_nodes))
            pairs = []
            
            # Different learning counts for different graph sizes
            learning_counts = {10: 18, 50: 40, 100: 60}
            learning_count = learning_counts.get(num_nodes, max(15, num_nodes // 2))
            
            for _ in range(learning_count):
                source = random.choice(node_ids)
                target = random.choice([n for n in node_ids if n != source])
                pairs.append((source, target))
            
            return pairs
        finally:
            random.setstate(original_state)
    
    def execute_learning_frame(self, message_processor):
        """Execute one learning frame"""
        print(f"\n--- LEARNING FRAME {self.current_frame + 1} START ---")
        
        # Reset all nodes COMPLETELY
        for node in self.network.nodes.values():
            node.reset_frame_status()
            # ALSO clear source/target status - we'll set them fresh
            node.set_as_source(False)
            node.set_as_target(False)
        
        # Mark ONLY currently active message source/target nodes
        active_sources = set()
        active_targets = set()
        
        for message in self.learning_messages.values():
            if message.is_active and not message.is_completed:
                active_sources.add(message.source)
                active_targets.add(message.target)
                self.network.nodes[message.source].set_as_source(True)
                self.network.nodes[message.target].set_as_target(True)
        
        print(f"Active sources: {sorted(active_sources)}")
        print(f"Active targets: {sorted(active_targets)}")
        
        # Start new messages for this frame
        self._start_learning_messages_for_frame()
        
        # Process message transmissions using the message processor
        transmission_queue, sending_nodes, successful_receives, completed_messages = \
            message_processor.process_transmissions(self.learning_messages, "learning")
        
        # Clean up completed learning messages IMMEDIATELY
        for message in completed_messages:
            self._clear_learning_message_status(message)
            print(f"Cleared colors for completed Learning Message {message.id}")
        
        self.current_frame += 1
        
        # Print learning progress
        self._print_learning_progress()
        
        # FINAL CLEANUP: Verify colors are correct
        self._verify_colors()
        
        print(f"--- LEARNING FRAME {self.current_frame} END ---")
        
        return transmission_queue
    
    def _verify_colors(self):
        """Verify that source/target colors match active messages"""
        print("Verifying colors...")
        
        # Get expected sources and targets
        expected_sources = set()
        expected_targets = set()
        
        for message in self.learning_messages.values():
            if message.is_active and not message.is_completed:
                expected_sources.add(message.source)
                expected_targets.add(message.target)
        
        # Check actual colors
        actual_sources = set()
        actual_targets = set()
        
        for node_id, node in self.network.nodes.items():
            if node.status_flags[node.STATUS_SOURCE]:
                actual_sources.add(node_id)
            if node.status_flags[node.STATUS_TARGET]:
                actual_targets.add(node_id)
        
        print(f"  Expected sources: {sorted(expected_sources)}")
        print(f"  Actual sources: {sorted(actual_sources)}")
        print(f"  Expected targets: {sorted(expected_targets)}")
        print(f"  Actual targets: {sorted(actual_targets)}")
        
        # Fix any mismatches
        wrong_sources = actual_sources - expected_sources
        wrong_targets = actual_targets - expected_targets
        
        for node_id in wrong_sources:
            self.network.nodes[node_id].set_as_source(False)
            print(f"  FIXED: Removed wrong SOURCE color from node {node_id}")
            
        for node_id in wrong_targets:
            self.network.nodes[node_id].set_as_target(False)
            print(f"  FIXED: Removed wrong TARGET color from node {node_id}")
        
        if not wrong_sources and not wrong_targets:
            print("  All colors are correct")
    
    def _start_learning_messages_for_frame(self):
        """Start learning messages that should begin this frame"""
        started_messages = []
        
        for message in self.learning_messages.values():
            if message.start_frame == (self.current_frame + 1) and not message.is_active:
                message.start_transmission()
                
                # Mark source and target nodes
                self.network.nodes[message.source].set_as_source(True)
                self.network.nodes[message.target].set_as_target(True)
                
                # Add message to source node's pending list
                initial_path = [message.source]
                self.network.nodes[message.source].pending_messages.append((message, initial_path))
                
                started_messages.append(message.id)
                print(f"Started Learning Message {message.id}: {message.source} -> {message.target}")
        
        if started_messages:
            # Show status of all learning messages
            self._print_learning_messages_status()
    
    def _print_learning_messages_status(self):
        """Print status of all learning messages"""
        print(f"\nLearning Messages Status (Frame {self.current_frame + 1}):")
        active_count = completed_count = waiting_count = 0
        
        for msg_id, message in sorted(self.learning_messages.items()):
            if message.is_completed:
                status = f"COMPLETED ({message.get_status()})"
                completed_count += 1
            elif message.is_active:
                status = "ACTIVE"
                active_count += 1
            else:
                status = f"WAITING (starts frame {message.start_frame})"
                waiting_count += 1
            
            print(f"  Learning Msg {msg_id}: {message.source}->{message.target} - {status}")
        
        print(f"Summary: {active_count} active, {waiting_count} waiting, {completed_count} completed")
    
    def _print_learning_progress(self):
        """Print learning progress and knowledge trees"""
        print(f"\nLEARNING KNOWLEDGE TREES - End of Frame {self.current_frame}:")
        print("=" * 70)
        
        trees_found = False
        nodes_with_trees = []
        new_entries_this_frame = []
        
        for node_id in sorted(self.network.nodes.keys()):
            node = self.network.nodes[node_id]
            if node.knowledge_tree:
                trees_found = True
                nodes_with_trees.append(node_id)
                
                # Check for new entries learned this frame
                new_entries = []
                for dest, entries_list in node.knowledge_tree.items():
                    for entry in entries_list:
                        if entry.get('learned_frame') == self.current_frame:
                            new_entries.append(dest)
                
                if new_entries:
                    new_entries_this_frame.extend([(node_id, dest) for dest in new_entries])
                    print(f"\nNode {node_id} Learning Tree (NEW: learned about {new_entries} this frame):")
                else:
                    print(f"\nNode {node_id} Learning Tree (no new entries this frame):")
                
                node.print_knowledge_tree()
                print()
        
        if not trees_found:
            print("\n   (No knowledge trees built yet in learning phase)")
        else:
            # Calculate total destinations
            total_destinations = 0
            for node_id in nodes_with_trees:
                total_destinations += len(self.network.nodes[node_id].knowledge_tree)
            
            print(f"\nLearning Progress: {len(nodes_with_trees)}/{len(self.network.nodes)} nodes have built trees")
            print(f"Total destinations learned so far: {total_destinations}")
            
            if new_entries_this_frame:
                print(f"New knowledge gained this frame:")
                for node_id, dest in new_entries_this_frame:
                    print(f"    Node {node_id} learned about destination {dest}")
            else:
                print(f"No new knowledge gained this frame")
        
        print("=" * 70)
  
    def _clear_learning_message_status(self, completed_message):
        """Clear source/target status when learning message completes"""
        source_id = completed_message.source
        target_id = completed_message.target
        message_id = completed_message.id
        
        print(f"Clearing status for Learning Message {message_id} ({source_id}->{target_id})")
        
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
        
        # Check if source has OTHER active LEARNING messages
        source_has_other_active = any(
            msg.is_active and not msg.is_completed and msg.source == source_id 
            for msg in self.learning_messages.values() 
            if msg != completed_message
        )
        
        print(f"  Source node {source_id}: other active messages = {source_has_other_active}")
        
        if not source_has_other_active:
            self.network.nodes[source_id].set_as_source(False)
            print(f"  Cleared SOURCE color from node {source_id}")
            
        # Check if target has OTHER active LEARNING messages
        target_has_other_active = any(
            msg.is_active and not msg.is_completed and msg.target == target_id 
            for msg in self.learning_messages.values() 
            if msg != completed_message
        )
        
        print(f"  Target node {target_id}: other active messages = {target_has_other_active}")
        
        if not target_has_other_active:
            self.network.nodes[target_id].set_as_target(False)
            print(f"  Cleared TARGET color from node {target_id}")
        
        print(f"Status cleanup complete for Learning Message {message_id}")
    
    def is_complete(self):
        """Check if learning phase is complete"""
        return (self.current_frame >= self.learning_frames or 
                all(msg.is_completed for msg in self.learning_messages.values()))
    
    def clean_up_colors(self):
        """Clean up any remaining source/target colors after learning phase"""
        print("Cleaning up learning phase colors...")
        for node in self.network.nodes.values():
            node.set_as_source(False)
            node.set_as_target(False)
            node.reset_frame_status()
        print("All learning colors cleared")
    
    def show_final_results(self):
        """Show final learning results"""
        print(f"\nLEARNING PHASE COMPLETED!")
        print("="*60)
        
        # Count trees built
        trees_built = 0
        total_destinations_learned = 0
        
        for node in self.network.nodes.values():
            if node.knowledge_tree:
                trees_built += 1
                total_destinations_learned += len(node.knowledge_tree)
        
        print(f"Learning Statistics:")
        print(f"  • Nodes that built knowledge trees: {trees_built}/{len(self.network.nodes)}")
        print(f"  • Total destination mappings learned: {total_destinations_learned}")
        print(f"  • Average destinations per node: {total_destinations_learned/len(self.network.nodes):.1f}")
        
        print(f"\nFinal Knowledge Trees:")
        for node_id in sorted(self.network.nodes.keys()):
            node = self.network.nodes[node_id]
            if node.knowledge_tree:
                print(f"\nNode {node_id} learned about {len(node.knowledge_tree)} destinations:")
                node.print_knowledge_tree()
        
        print("="*60)
        print("Ready to proceed to algorithm comparison phase!")
        
        return trees_built, total_destinations_learned