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
    
    auto_messages = sim.generate_random_message_pairs(num_messages)
    
    # Setup simulation variables
    step_count = 0
    max_steps = 50
    running = True
    waiting_for_input = False
    
    def handle_key(key):
        """Handle keyboard input from graph window"""
        nonlocal running, step_count, waiting_for_input
        
        print(f"\n🔧 DEBUG: Key pressed: '{key}' (waiting_for_input: {waiting_for_input})")
        
        # IMPORTANT: Prevent double execution
        if waiting_for_input:
            print("🔧 DEBUG: Already processing input, ignoring...")
            return
        
        if key == ' ':  # Space bar
            if step_count < max_steps:
                waiting_for_input = True  # Block further inputs
                step_count += 1
                
                print(f"\n--- Step {step_count} ---")
                print("🔧 DEBUG: About to call step_simulation()")
                
                # Execute simulation step
                has_more = sim.step_simulation()
                
                print("🔧 DEBUG: step_simulation() returned:", has_more)
                
                # Update visualization - NO KEY CALLBACK to prevent double execution
                try:
                    print("🔧 DEBUG: About to update visualization")
                    sim.visualize_current_state(key_callback=None)  # REMOVED CALLBACK!
                    print("🔧 DEBUG: Visualization updated successfully")
                except Exception as e:
                    print(f"🔧 DEBUG: Visualization update failed: {e}")
                    import traceback
                    traceback.print_exc()
                
                # Check if simulation is complete
                if not has_more and len(sim.all_messages) == len(sim.completed_messages):
                    print("All messages completed!")
                    print("\n=== Final Results ===")
                    sim.print_simulation_results()
                    running = False
                elif step_count >= max_steps:
                    print("Simulation reached maximum steps!")
                    running = False
                
                waiting_for_input = False  # Ready for next input
                print("🔧 DEBUG: Ready for next SPACE press")
                
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
        print("🔧 DEBUG: Setting up matplotlib")
        plt.figure(figsize=(16, 10))
        plt.ion()  # Interactive mode
        
        print("🔧 DEBUG: Showing initial visualization")
        # Show initial state with key callback
        sim.visualize_current_state(key_callback=handle_key)
        print("\nGraph window opened! Click on it and press SPACE to advance simulation.")
        
        print("🔧 DEBUG: Entering main loop")
        # Keep the program running and responsive - FIXED VERSION
        while running:
            try:
                plt.pause(1.0)  # Even slower pause - 1 second intervals
                
                # Check if window was closed
                if not plt.get_fignums():  # No figures open
                    print("Graph window closed")
                    break
                    
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                break
            except Exception as e:
                print(f"🔧 DEBUG: Error in main loop: {e}")
                break
                
        print("🔧 DEBUG: Exited main loop")
            
    except Exception as e:
        print(f"Visualization setup error: {e}")
        import traceback
        traceback.print_exc()
        print("\nRunning in text-only mode...")
        
        # Fallback to terminal input - IMPROVED VERSION
        print("🔧 DEBUG: Entering text-only mode")
        while step_count < max_steps and running:
            try:
                user_input = input(f"\nStep {step_count + 1} - Press ENTER to advance, 'q' to quit: ").strip().lower()
                
                if user_input == 'q':
                    break
                
                step_count += 1
                print(f"\n--- Step {step_count} ---")
                
                has_more = sim.step_simulation()
                
                if not has_more and len(sim.all_messages) == len(sim.completed_messages):
                    print("All messages completed!")
                    break
                    
            except KeyboardInterrupt:
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
        import traceback
        traceback.print_exc()
        print("Please check your input and try again.")