import random
from network import Network
from LearningPhaseManager import LearningPhaseManager
from ComparisonPhaseManager import ComparisonPhaseManager
from DisplayManager import DisplayManager
from MessageProcessor import MessageProcessor

class Simulator:
    """
    Main simulator class - coordinates between different managers
    Much cleaner and focused on orchestration rather than implementation details
    """
    
    def __init__(self):
        # Core components
        self.network = Network()
        
        # Managers
        self.learning_manager = LearningPhaseManager(self.network)
        self.comparison_manager = ComparisonPhaseManager(self.network)
        self.display_manager = DisplayManager(self.network)
        self.message_processor = MessageProcessor(self.network)
        
        # Simulation control
        self.is_running = False
        
        # Set up display callback
        self.display_manager.set_key_callback(self.on_key_press)
        
    def setup_simulation(self, num_nodes, num_messages, total_frames=60):
        """Initialize simulation with user parameters"""
        
        self.num_comparison_messages = num_messages
        self.comparison_total_frames = total_frames
        
        print(f"Setting up simulation with {num_nodes} nodes")
        print(f"Parameters: {num_messages} messages, {total_frames} frames")
        
        # Create network
        self.network.create_nodes(num_nodes)
        self.network.create_network_connections()
        
        # Print basic setup summary
        self._print_basic_setup_summary()
        
        print("Basic simulation setup complete")
        
    def setup_learning_phase(self):
        """Setup learning phase when chosen from menu"""
        print("Setting up learning phase...")
        
        num_nodes = len(self.network.nodes)
        
        # Generate learning messages
        learning_frames = self.learning_manager.generate_learning_messages(num_nodes)
        
        # Print setup summary for learning phase
        self._print_learning_setup_summary()
        
        print("Learning phase setup complete")
        return learning_frames
    
    def setup_comparison_phase(self):
        """Setup comparison phase after learning is complete"""
        print("Setting up comparison phase...")
        
        # Set the total_frames FIRST before generating messages
        self.comparison_manager.total_frames = self.comparison_total_frames
        
        print(f"Using {self.num_comparison_messages} messages and {self.comparison_total_frames} frames")
        
        # NOW generate comparison messages using the correct total_frames
        self.comparison_manager.generate_comparison_messages(self.num_comparison_messages)
        
        # Print setup summary for comparison phase
        self._print_comparison_setup_summary()
        
        print("Comparison phase setup complete")
    
    def _print_basic_setup_summary(self):
        """Print summary of basic setup"""
        print("\n" + "="*50)
        print("SIMULATION SETUP SUMMARY")
        print("="*50)
        
        self.network.print_network_summary()
        print(f"Planned comparison messages: {self.num_comparison_messages}")
        print(f"Planned comparison frames: {self.comparison_total_frames}")
        
        print("="*50)
    
    def _print_learning_setup_summary(self):
        """Print summary of learning phase setup"""
        print("\n" + "="*50)
        print("LEARNING PHASE SETUP")
        print("="*50)
        
        print(f"Learning messages: {len(self.learning_manager.learning_messages)}")
        print(f"Learning frames: {self.learning_manager.learning_frames}")
        
        print("="*50)
    
    def _print_comparison_setup_summary(self):
        """Print summary of comparison phase setup"""
        print("\n" + "="*50)
        print("COMPARISON PHASE SETUP")
        print("="*50)
        
        print(f"Comparison messages: {len(self.comparison_manager.messages)}")
        print(f"Comparison frames: {self.comparison_manager.total_frames}")
        
        print("\nMessage details:")
        for msg_id, message in self.comparison_manager.messages.items():
            print(f"  {message}")
            
        print("="*50)
    
    def get_user_input(self):
        """Get simulation parameters from user with fixed graph options"""
        print("Network Flooding Simulator Setup")
        print("-" * 30)
        
        # Show only supported fixed graph options
        fixed_sizes = self.network.get_supported_fixed_sizes()
        print(f"Available graph sizes: {fixed_sizes}")
        print("Each size has an optimized layout for message passing algorithms")
        print()
        
        try:
            while True:
                num_nodes = int(input("Enter number of nodes (10, 50, or 100): "))
                if num_nodes in fixed_sizes:
                    print(f"Using optimized layout for {num_nodes} nodes")
                    break
                else:
                    print(f"Only sizes {fixed_sizes} are supported. Please choose one of these.")
                    continue
                
            num_messages = int(input("Enter number of messages: "))
            if num_messages < 1:
                print("Using default: 5 messages")
                num_messages = 5
                
            total_frames = int(input("Enter total simulation frames (default 60): ") or "60")
            if total_frames < 10:
                print("Using minimum: 60 frames")
                total_frames = 60
                
        except ValueError:
            print("Invalid input, using defaults: 10 nodes, 5 messages, 60 frames")
            num_nodes, num_messages, total_frames = 10, 5, 60
            
        return num_nodes, num_messages, total_frames
    
    def run_simulation(self):
        """Run the complete simulation with 5-option menu"""
        print("\n" + "="*60)
        print("NETWORK FLOODING SIMULATION")
        print("="*60)
        print("Available operations:")
        print("1. Learning phase - build knowledge trees")
        print("2. Flooding algorithm - pure flooding approach")
        print("3. Tree-based algorithm - smart routing with learned knowledge") 
        print("4. Algorithm comparison - run both and compare results")
        print("5. Exit simulation")
        print("="*60)
        
        # Show main menu loop
        while True:
            choice = self._show_main_menu()
            
            if choice == "1":
                print("\nRunning Learning Phase...")
                self._run_learning_phase()
            elif choice == "2":
                print("\nRunning Flooding Algorithm...")
                if not self.learning_manager.learning_complete:
                    print("Note: Running without learning phase (no knowledge trees)")
                self._run_flooding_algorithm()
            elif choice == "3":
                print("\nRunning Tree-Based Algorithm...")
                if not self.learning_manager.learning_complete:
                    print("Warning: No learning completed! Tree algorithm may not work optimally.")
                self._run_tree_algorithm()
            elif choice == "4":
                print("\nRunning Algorithm Comparison...")
                if not self.learning_manager.learning_complete:
                    print("Note: Comparing without learning phase")
                self._run_comparison()
            elif choice == "5":
                print("\nExiting simulation.")
                break
            else:
                print("Invalid choice. Please try again.")
        
        print("Simulation completed.")
    
    def _show_main_menu(self):
        """Show main menu and get user choice"""
        print("\n" + "="*50)
        print("SIMULATION MENU")
        print("="*50)
        
        learning_status = "Completed" if self.learning_manager.learning_complete else "Not run"
        
        print("1. Learning Phase")
        print(f"   Status: {learning_status}")
        print("2. Flooding Algorithm")
        print("3. Tree-Based Algorithm") 
        print("4. Compare Both Algorithms")
        print("5. Exit")
        print("="*50)
        
        choice = input("Enter your choice (1-5): ").strip()
        return choice
    
    def _run_learning_phase(self):
        """Run the learning phase"""
        if self.learning_manager.learning_complete:
            print("Learning phase already completed.")
            rerun = input("Do you want to run it again? (y/n): ").lower().strip()
            if rerun not in ['y', 'yes']:
                return
            else:
                # Reset learning phase
                self.learning_manager.learning_complete = False
                self.learning_manager.current_frame = 0
        
        # Setup learning phase
        self.setup_learning_phase()
        
        # Ask how to run learning
        print("\nLearning phase options:")
        print("1. Interactive mode (step-by-step)")
        print("2. Fast mode (automatic)")
        
        while True:
            mode_choice = input("Choose mode (1 or 2): ").strip()
            if mode_choice == "1":
                self._run_interactive_learning()
                break
            elif mode_choice == "2":
                self._run_fast_learning()
                break
            else:
                print("Invalid choice. Please enter 1 or 2.")
        
        print("\nLearning phase completed.")
        input("Press Enter to return to main menu...")
    
    def _run_flooding_algorithm(self):
        """Run the flooding algorithm"""
        print("Setting up flooding algorithm simulation...")
        
        # Setup comparison phase if not already done
        if not hasattr(self.comparison_manager, 'messages') or not self.comparison_manager.messages:
            self.setup_comparison_phase()
        
        # Reset comparison manager
        self.comparison_manager.current_frame = 0
        self.comparison_manager.reset_simulation()
        
        # Set algorithm mode and name for statistics
        self._set_algorithm_mode("flooding")
        self.comparison_manager.set_algorithm_name("Flooding")
        
        # Initialize display for comparison
        self.display_manager.initialize_display()
        self.is_running = True
        
        # Set display mode
        self.display_manager.set_mode("comparison", 
                                    self.comparison_manager.current_frame, 
                                    self.comparison_manager.total_frames)
        
        # Update display
        self.display_manager.update_display(self.comparison_manager.messages, "comparison")
        
        print("\nFlooding algorithm ready.")
        print("Every node will forward to ALL neighbors")
        print("\nControls:")
        print("  SPACE: Advance to next frame")
        print("  Q: Finish this algorithm")
        print("  R: Reset simulation")
        print("\nClick on the simulation window and press SPACE to begin.")
        
        # Run until complete or user quits
        try:
            while self.is_running and not self.comparison_manager.is_complete():
                import matplotlib.pyplot as plt
                plt.pause(0.1)
                if not plt.get_fignums():
                    self.is_running = False
                    break
        except KeyboardInterrupt:
            print("\nSimulation interrupted")
        
        # Show results
        if self.comparison_manager.is_complete():
            print("\nFlooding algorithm completed.")
            self.comparison_manager.show_final_statistics()
        
        # Close display
        self.display_manager.close_display()
        self.is_running = True  # Reset for menu
        input("Press Enter to return to main menu...")

    def _run_tree_algorithm(self):
        """Run the tree-based algorithm"""
        print("Setting up tree-based algorithm simulation...")
        
        # Setup comparison phase if not already done
        if not hasattr(self.comparison_manager, 'messages') or not self.comparison_manager.messages:
            self.setup_comparison_phase()
        
        # Reset comparison manager
        self.comparison_manager.current_frame = 0
        self.comparison_manager.reset_simulation()
        
        # Set algorithm mode and name for statistics
        self._set_algorithm_mode("tree")
        self.comparison_manager.set_algorithm_name("Tree-Based")
        
        # Initialize display for comparison
        self.display_manager.initialize_display()
        self.is_running = True
        
        # Set display mode
        self.display_manager.set_mode("comparison", 
                                    self.comparison_manager.current_frame, 
                                    self.comparison_manager.total_frames)
        
        # Update display
        self.display_manager.update_display(self.comparison_manager.messages, "comparison")
        
        print("\nTree-based algorithm ready.")
        print("Nodes will use learned knowledge trees for smart routing")
        print("\nControls:")
        print("  SPACE: Advance to next frame")
        print("  Q: Finish this algorithm")
        print("  R: Reset simulation")
        print("\nClick on the simulation window and press SPACE to begin.")
        
        # Run until complete or user quits
        try:
            while self.is_running and not self.comparison_manager.is_complete():
                import matplotlib.pyplot as plt
                plt.pause(0.1)
                if not plt.get_fignums():
                    self.is_running = False
                    break
        except KeyboardInterrupt:
            print("\nSimulation interrupted")
        
        # Show results
        if self.comparison_manager.is_complete():
            print("\nTree-based algorithm completed.")
            self.comparison_manager.show_final_statistics()
        
        # Close display
        self.display_manager.close_display()
        self.is_running = True  # Reset for menu
        input("Press Enter to return to main menu...")

    def _run_comparison(self):
        """Run both algorithms and compare results"""
        print("Running comprehensive comparison of both algorithms...")
        print("This will take a moment...")
        
        # Setup comparison phase if not already done
        if not hasattr(self.comparison_manager, 'messages') or not self.comparison_manager.messages:
            self.setup_comparison_phase()
        
        results = {}
        
        # Run flooding algorithm (fast mode)
        print("\nRunning Flooding Algorithm (fast mode)...")
        self._set_algorithm_mode("flooding")
        self.comparison_manager.set_algorithm_name("Flooding")
        flooding_stats = self._run_algorithm_fast("flooding")
        results["flooding"] = flooding_stats
        
        # Run tree algorithm (fast mode)
        print("Running Tree-Based Algorithm (fast mode)...")
        self._set_algorithm_mode("tree")
        self.comparison_manager.set_algorithm_name("Tree-Based")
        tree_stats = self._run_algorithm_fast("tree")
        results["tree"] = tree_stats
        
        # Show comparison
        print("\nALGORITHM COMPARISON RESULTS")
        print("="*80)
        
        self._show_detailed_algorithm_comparison(results)
        
        print("="*80)
        input("\nPress Enter to return to menu...")
        
    def _set_algorithm_mode(self, mode):
        """Set the algorithm mode for message processing"""
        # This will be used by MessageProcessor to decide routing strategy
        self.current_algorithm = mode
        # Pass the mode to all relevant components
        if hasattr(self.message_processor, 'set_algorithm_mode'):
            self.message_processor.set_algorithm_mode(mode)
    
    def _run_algorithm_fast(self, algorithm_name):
        """Run an algorithm in fast mode and return detailed statistics"""
        # Reset comparison manager
        self.comparison_manager.current_frame = 0
        self.comparison_manager.reset_simulation()
        
        # Run simulation without display
        while not self.comparison_manager.is_complete():
            transmission_queue = self.comparison_manager.execute_comparison_frame(self.message_processor)
            
            # Prevent infinite loops
            if self.comparison_manager.current_frame > self.comparison_manager.total_frames:
                break
        
        # Get detailed statistics
        detailed_stats = self.comparison_manager.get_detailed_statistics()
        return detailed_stats

    def _show_detailed_algorithm_comparison(self, results):
        """Show comprehensive detailed comparison between algorithms"""
        flooding = results["flooding"]
        tree = results["tree"]
        
        print(f"\nCOMPREHENSIVE ALGORITHM COMPARISON")
        print("=" * 80)
        
        # === MESSAGE-LEVEL STATISTICS ===
        print("\nMESSAGE SUCCESS STATISTICS:")
        print(f"{'Metric':<35} {'Flooding':<15} {'Tree-Based':<15} {'Winner':<15}")
        print("-" * 80)
        
        # Message success rate
        flood_msg_success = flooding['success_rate']
        tree_msg_success = tree['success_rate']
        msg_winner = self._determine_winner(tree_msg_success, flood_msg_success, higher_better=True)
        print(f"{'Message Success Rate (%)':<35} {flood_msg_success:<15.1f} {tree_msg_success:<15.1f} {msg_winner:<15}")
        
        # Successful vs failed messages
        print(f"{'Successful Messages':<35} {flooding['successful']:<15} {tree['successful']:<15} {self._determine_winner(tree['successful'], flooding['successful'], higher_better=True):<15}")
        print(f"{'Failed Messages':<35} {flooding['failed']:<15} {tree['failed']:<15} {self._determine_winner(tree['failed'], flooding['failed'], higher_better=False):<15}")
        
        # === NETWORK-LEVEL STATISTICS ===
        print(f"\nNETWORK TRANSMISSION STATISTICS:")
        print(f"{'Metric':<35} {'Flooding':<15} {'Tree-Based':<15} {'Winner':<15}")
        print("-" * 80)
        
        # Total transmissions
        print(f"{'Total Transmissions Sent':<35} {flooding['total_transmissions_sent']:<15} {tree['total_transmissions_sent']:<15} {self._determine_winner(tree['total_transmissions_sent'], flooding['total_transmissions_sent'], higher_better=False):<15}")
        print(f"{'Total Transmissions Received':<35} {flooding['total_transmissions_received']:<15} {tree['total_transmissions_received']:<15} {self._determine_winner(tree['total_transmissions_received'], flooding['total_transmissions_received'], higher_better=True):<15}")
        
        # Network efficiency
        flood_net_eff = flooding['network_efficiency']
        tree_net_eff = tree['network_efficiency']
        net_eff_winner = self._determine_winner(tree_net_eff, flood_net_eff, higher_better=True)
        print(f"{'Network Efficiency (%)':<35} {flood_net_eff:<15.1f} {tree_net_eff:<15.1f} {net_eff_winner:<15}")
        
        # Resource efficiency
        flood_res_eff = flooding['resource_efficiency']
        tree_res_eff = tree['resource_efficiency']
        res_eff_winner = self._determine_winner(tree_res_eff, flood_res_eff, higher_better=True)
        print(f"{'Resource Efficiency (%)':<35} {flood_res_eff:<15.3f} {tree_res_eff:<15.3f} {res_eff_winner:<15}")
        
        # === COLLISION AND PERFORMANCE STATISTICS ===
        print(f"\nCOLLISION AND PERFORMANCE STATISTICS:")
        print(f"{'Metric':<35} {'Flooding':<15} {'Tree-Based':<15} {'Winner':<15}")
        print("-" * 80)
        
        # Collisions
        collision_winner = self._determine_winner(tree['total_collisions'], flooding['total_collisions'], higher_better=False)
        print(f"{'Total Collisions':<35} {flooding['total_collisions']:<15} {tree['total_collisions']:<15} {collision_winner:<15}")
        
        # Completion time
        time_winner = self._determine_winner(tree['frames_completed'], flooding['frames_completed'], higher_better=False)
        print(f"{'Frames to Complete':<35} {flooding['frames_completed']:<15} {tree['frames_completed']:<15} {time_winner:<15}")
        
        # Average path length
        flood_avg_path = flooding['average_path_length']
        tree_avg_path = tree['average_path_length']
        path_winner = self._determine_winner(tree_avg_path, flood_avg_path, higher_better=False)
        print(f"{'Average Path Length':<35} {flood_avg_path:<15.1f} {tree_avg_path:<15.1f} {path_winner:<15}")
        
        # === DETAILED MESSAGE ANALYSIS ===
        print(f"\nDETAILED MESSAGE ANALYSIS:")
        print("-" * 80)
        
        self._show_message_details_comparison(flooding, tree)
        
        # === OVERALL WINNER CALCULATION ===
        print(f"\nOVERALL WINNER ANALYSIS:")
        print("-" * 80)
        
        # Count wins in each category
        winners = [
            msg_winner,           # Message success rate
            net_eff_winner,       # Network efficiency  
            res_eff_winner,       # Resource efficiency
            collision_winner,     # Collisions (fewer is better)
            time_winner,          # Completion time (fewer is better)
            path_winner           # Path length (shorter is better)
        ]
        
        tree_wins = winners.count("Tree-Based")
        flood_wins = winners.count("Flooding")
        ties = winners.count("Tie")
        
        print(f"Tree-Based Algorithm Wins: {tree_wins}")
        print(f"Flooding Algorithm Wins: {flood_wins}")
        print(f"Ties: {ties}")
        print()
        
        if tree_wins > flood_wins:
            print("TREE-BASED ALGORITHM is the overall winner!")
            print("Better performance using learned knowledge trees")
            print("Smart routing decisions lead to more efficient network usage")
        elif flood_wins > tree_wins:
            print("FLOODING ALGORITHM is the overall winner!")
            print("Simple flooding proves more effective for this scenario")
            print("Pure flooding approach handles network conditions better")
        else:
            print("IT'S A TIE!")
            print("Both algorithms performed similarly in this scenario")
            print("Different network conditions might favor one over the other")
        
        # === INSIGHTS AND RECOMMENDATIONS ===
        print(f"\nINSIGHTS AND RECOMMENDATIONS:")
        print("-" * 80)
        self._provide_algorithm_insights(flooding, tree)

    def _show_message_details_comparison(self, flooding_stats, tree_stats):
        """Show detailed comparison of individual message performance"""
        print("Individual Message Performance:")
        print()
        
        # Show message success details
        flood_messages = flooding_stats['message_details']
        tree_messages = tree_stats['message_details']
        
        print(f"{'Message':<10} {'Route':<15} {'Flooding Result':<20} {'Tree Result':<20} {'Better':<10}")
        print("-" * 80)
        
        for i in range(len(flood_messages)):
            flood_msg = flood_messages[i]
            tree_msg = tree_messages[i]
            
            flood_result = "SUCCESS" if flood_msg['success'] else "FAILED"
            tree_result = "SUCCESS" if tree_msg['success'] else "FAILED"
            
            # Determine which performed better for this message
            if flood_msg['success'] and tree_msg['success']:
                # Both succeeded - compare path length or transmissions
                if flood_msg['path_length'] == tree_msg['path_length']:
                    better = "Tie"
                elif flood_msg['path_length'] < tree_msg['path_length']:
                    better = "Flooding"
                else:
                    better = "Tree"
            elif flood_msg['success'] and not tree_msg['success']:
                better = "Flooding"
            elif tree_msg['success'] and not flood_msg['success']:
                better = "Tree"
            else:
                better = "Both Failed"
            
            print(f"{'Msg ' + str(flood_msg['id']):<10} {flood_msg['route']:<15} {flood_result:<20} {tree_result:<20} {better:<10}")
        
        print()

    def _provide_algorithm_insights(self, flooding_stats, tree_stats):
        """Provide insights and recommendations based on the comparison"""
        insights = []
        
        # Network efficiency insight
        if tree_stats['network_efficiency'] > flooding_stats['network_efficiency'] * 1.1:
            insights.append("Tree-based algorithm shows significantly better network efficiency")
            insights.append("  Knowledge trees help avoid unnecessary transmissions")
        elif flooding_stats['network_efficiency'] > tree_stats['network_efficiency'] * 1.1:
            insights.append("Flooding algorithm shows better network efficiency")
            insights.append("  Simple flooding works well for this network topology")
        
        # Path length insight
        if tree_stats['average_path_length'] < flooding_stats['average_path_length'] * 0.9:
            insights.append("Tree-based algorithm finds shorter paths on average")
            insights.append("  Knowledge trees enable more direct routing")
        elif flooding_stats['average_path_length'] < tree_stats['average_path_length'] * 0.9:
            insights.append("Flooding algorithm achieves shorter paths")
            insights.append("  Multiple parallel paths help find efficient routes")
        
        # Collision insight
        total_transmissions_diff = abs(tree_stats['total_transmissions_sent'] - flooding_stats['total_transmissions_sent'])
        if total_transmissions_diff > max(tree_stats['total_transmissions_sent'], flooding_stats['total_transmissions_sent']) * 0.2:
            if tree_stats['total_transmissions_sent'] < flooding_stats['total_transmissions_sent']:
                insights.append("Tree-based algorithm significantly reduces network traffic")
                insights.append("  Smart routing decisions minimize unnecessary transmissions")
            else:
                insights.append("Flooding algorithm uses more network resources")
                insights.append("  Higher transmission volume may indicate less efficient routing")
        
        # Success rate insight
        success_diff = abs(tree_stats['success_rate'] - flooding_stats['success_rate'])
        if success_diff > 10:  # More than 10% difference
            if tree_stats['success_rate'] > flooding_stats['success_rate']:
                insights.append("Tree-based algorithm has significantly higher success rate")
                insights.append("  Learned knowledge improves message delivery reliability")
            else:
                insights.append("Flooding algorithm achieves higher success rate")
                insights.append("  Redundant paths improve delivery reliability")
        
        # Print insights
        if insights:
            for insight in insights:
                print(insight)
        else:
            print("Both algorithms performed very similarly in this scenario")
            print("Try running with different network configurations for clearer differences")
        
        print()
        print("GENERAL RECOMMENDATIONS:")
        print("• Tree-based routing works best in stable networks with good connectivity")
        print("• Flooding is more robust in dynamic or uncertain network conditions")
        print("• Consider hybrid approaches that combine both strategies")

    def _determine_winner(self, value1, value2, higher_better=True):
        """Determine winner between two values"""
        if abs(value1 - value2) < 0.001:  # Essentially equal
            return "Tie"
        
        if higher_better:
            return "Tree-Based" if value1 > value2 else "Flooding"
        else:
            return "Tree-Based" if value1 < value2 else "Flooding"
    
    def _run_interactive_learning(self):
        """Run learning phase interactively (step by step)"""
        print("Setting up interactive learning phase...")
        
        # Initialize display
        self.display_manager.initialize_display()
        self.is_running = True
        
        print("\nLearning phase controls:")
        print("  SPACE: Advance to next learning frame")
        print("  Q: Skip to learning results")
        print("  R: Reset learning")
        print("\nClick on the simulation window and press SPACE to begin learning.")
        
        # Set display mode
        self.display_manager.set_mode("learning", 
                                    self.learning_manager.current_frame, 
                                    self.learning_manager.learning_frames)
        
        # Initial display
        self.display_manager.update_display(self.learning_manager.learning_messages, "learning")
        
        # Wait for learning to complete
        while not self.learning_manager.is_complete() and self.is_running:
            import matplotlib.pyplot as plt
            plt.pause(0.1)
            if not plt.get_fignums():
                self.is_running = False
                return
        
        # Show final results if completed
        if self.learning_manager.learning_complete:
            self.learning_manager.show_final_results()
        
        # Close display
        self.display_manager.close_display()
    
    def _run_fast_learning(self):
        """Run learning phase in fast mode (no display)"""
        print("Running learning phase in fast mode...")
        
        saved_frame = self.learning_manager.current_frame
        self.learning_manager.current_frame = 0
        
        for frame in range(self.learning_manager.learning_frames):
            # Reset nodes
            for node in self.network.nodes.values():
                node.reset_frame_status()
            
            # Mark active message nodes
            for message in self.learning_manager.learning_messages.values():
                if message.is_active and not message.is_completed:
                    self.network.nodes[message.source].set_as_source(True)
                    self.network.nodes[message.target].set_as_target(True)
            
            # Execute learning frame logic without display
            self.learning_manager._start_learning_messages_for_frame()
            transmission_queue, _, _, completed_messages = \
                self.message_processor.process_transmissions(self.learning_manager.learning_messages, "learning")
            
            # Clean up completed messages
            for message in completed_messages:
                self.learning_manager._clear_learning_message_status(message)
            
            self.learning_manager.current_frame += 1
            
            # Check completion
            if all(msg.is_completed for msg in self.learning_manager.learning_messages.values()):
                print(f"All learning messages completed at frame {frame + 1}")
                break
        
        # Restore and complete learning
        self.learning_manager.current_frame = saved_frame
        self.learning_manager.learning_complete = True
        self.learning_manager.clean_up_colors()
        self.learning_manager.show_final_results()
    
    def on_key_press(self, event):
        """Handle keyboard input from display manager"""
        if not self.is_running:
            return
            
        if event.key == ' ':  # Space bar
            if not self.learning_manager.learning_complete:
                # LEARNING MODE
                if self.learning_manager.is_complete():
                    print("Learning phase completed.")
                    self.learning_manager.learning_complete = True
                    self.learning_manager.clean_up_colors()
                    self.learning_manager.show_final_results()
                    return
                print(f"Advancing to learning frame {self.learning_manager.current_frame + 1}")
                self.advance_learning_frame()
            elif hasattr(self.comparison_manager, 'messages') and self.comparison_manager.messages:
                # COMPARISON MODE (only if comparison messages exist)
                if self.comparison_manager.is_complete():
                    print("Comparison simulation already completed.")
                    return
                print(f"Advancing to comparison frame {self.comparison_manager.current_frame + 1}")
                self.advance_comparison_frame()
            else:
                # WAITING FOR COMPARISON SETUP
                print("Comparison phase not set up yet. Complete learning phase first.")
            
        elif event.key == 'q':  # Quit or skip learning
            if not self.learning_manager.learning_complete:
                # SKIP LEARNING
                print("Skipping learning phase...")
                self._run_fast_learning()
            else:
                # QUIT SIMULATION
                print("Quitting simulation...")
                self.is_running = False
                self.display_manager.close_display()
            
        elif event.key == 'r':  # Reset (comparison phase only)
            if self.learning_manager.learning_complete and hasattr(self.comparison_manager, 'messages') and self.comparison_manager.messages:
                # RESET COMPARISON
                print("Resetting comparison simulation...")
                self.comparison_manager.reset_simulation()
                self.display_manager.set_mode("comparison", 
                                            self.comparison_manager.current_frame, 
                                            self.comparison_manager.total_frames)
                self.display_manager.update_display(self.comparison_manager.messages, "comparison")
            elif not self.learning_manager.learning_complete:
                # RESET LEARNING (if needed)
                print("Cannot reset during learning phase")
            else:
                print("No comparison phase to reset")
    
    def advance_learning_frame(self):
        """Advance learning simulation by one frame"""
        if self.learning_manager.is_complete():
            print("Learning phase completed.")
            self.learning_manager.learning_complete = True
            self.learning_manager.clean_up_colors()
            self.learning_manager.show_final_results()
            return
            
        # Execute learning frame
        transmission_queue = self.learning_manager.execute_learning_frame(self.message_processor)
        
        # Update display
        self.display_manager.set_mode("learning", 
                                    self.learning_manager.current_frame, 
                                    self.learning_manager.learning_frames)
        self.display_manager.set_transmissions(transmission_queue)
        self.display_manager.update_display(self.learning_manager.learning_messages, "learning")
        
        # Check if learning is complete
        if self.learning_manager.is_complete():
            print(f"All learning messages completed at frame {self.learning_manager.current_frame}.")
            self.learning_manager.learning_complete = True
            self.learning_manager.clean_up_colors()
            self.learning_manager.show_final_results()
    
    def advance_comparison_frame(self):
        """Advance comparison simulation by one frame"""
        if self.comparison_manager.is_complete():
            print("Comparison simulation completed.")
            return
            
        # Execute comparison frame
        transmission_queue = self.comparison_manager.execute_comparison_frame(self.message_processor)
        
        # Update display
        self.display_manager.set_mode("comparison", 
                                    self.comparison_manager.current_frame, 
                                    self.comparison_manager.total_frames)
        self.display_manager.set_transmissions(transmission_queue)
        self.display_manager.update_display(self.comparison_manager.messages, "comparison")
        
        # Check completion
        if self.comparison_manager.is_complete():
            if all(msg.is_completed for msg in self.comparison_manager.messages.values()):
                print(f"All messages completed at frame {self.comparison_manager.current_frame}.")
            else:
                print(f"Simulation completed after {self.comparison_manager.total_frames} frames.")
            self.comparison_manager.show_final_statistics()