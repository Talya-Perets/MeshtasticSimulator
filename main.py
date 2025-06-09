#!/usr/bin/env python3
"""
Meshtastic Network Simulator - Graph Keyboard Control
"""

from simulator import MeshtasticSimulator
import matplotlib.pyplot as plt
import threading
import time

def main():
    """Main function with graph keyboard control"""
    print("=== Meshtastic Network Simulator ===")
    
    # Get number of nodes
    while True:
        try:
            num_nodes = int(input("Enter number of nodes (10-100): "))
            if 10 <= num_nodes <= 100:
                break
            else:
                print("Please enter a number between 10 and 100")
        except ValueError:
            print("Please enter a valid number")
    
    # Create simulator
    sim = MeshtasticSimulator()
    
    # Create network
    print(f"\nCreating network with {num_nodes} nodes...")
    network = sim.create_network(
        num_nodes=num_nodes, 
        space_size=100, 
        target_neighbors=4, 
        distribution="improved_random"
    )
    
    # Set routing to flooding
    sim.set_routing_algorithm("flooding")
    
    # Display network statistics
    sim.print_network_stats()
    
    # Generate random messages - start next message when previous completes
    num_messages = max(1, num_nodes // 3)
    print(f"\nGenerating {num_messages} random messages...")
    
    # Create messages that start one after another (not by time, but by completion)
    start_times = []
    for i in range(num_messages):
        start_times.append(0 if i == 0 else -1)  # First starts immediately, others wait
    
    auto_messages = sim.generate_random_message_pairs(num_messages, start_times=start_times)
    
    # Setup simulation variables
    step_count = 0
    max_steps = 50
    running = True
    
    def handle_key(key):
        """Handle keyboard input from graph window"""
        nonlocal running, step_count
        
        print(f"Key pressed: {key}")
        
        if key == ' ':  # Space bar
            if step_count < max_steps:
                print(f"\n--- Step {step_count + 1} ---")
                
                # Execute simulation step
                has_more = sim.step_simulation()
                
                # Update visualization
                try:
                    sim.visualize_current_state(key_callback=handle_key)
                except Exception as e:
                    print(f"Visualization update failed: {e}")
                
                step_count += 1
                
                # Check if simulation is complete
                if not has_more and len(sim.all_messages) == len(sim.completed_messages):
                    print("All messages completed!")
                    print("\n=== Final Results ===")
                    sim.print_simulation_results()
            else:
                print("Simulation reached maximum steps!")
                
        elif key == 'q':  # Quit
            print("Simulation stopped by user.")
            running = False
            plt.close('all')
    
    # Setup visualization
    print("\n=== Simulation ===")
    print("Controls in graph window:")
    print("  - SPACE = Next step")
    print("  - Q = Quit")
    print("  - Click graph to focus first!")
    
    # Show initial visualization
    try:
        plt.figure(figsize=(16, 10))
        plt.ion()  # Interactive mode
        sim.visualize_current_state(key_callback=handle_key)
        print("\nGraph window opened! Click on it and press SPACE to advance simulation.")
        
        # Keep the program running and responsive
        while running:
            plt.pause(0.1)  # Allow matplotlib to process events
            
    except Exception as e:
        print(f"Visualization error: {e}")
        print("Running in text-only mode...")
        
        # Fallback to terminal input
        while step_count < max_steps:
            user_input = input(f"\nStep {step_count + 1} - Press SPACE (or Enter) to advance, 'q' to quit: ").strip().lower()
            
            if user_input == 'q':
                break
            
            has_more = sim.step_simulation()
            step_count += 1
            
            if not has_more and len(sim.all_messages) == len(sim.completed_messages):
                print("All messages completed!")
                break
        
        print("\n=== Final Results ===")
        sim.print_simulation_results()
    
    print("\nSimulation complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        print("Please check your input and try again.")