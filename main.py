#!/usr/bin/env python3
"""
Network Flooding Simulator - Main Program

This program simulates a network flooding algorithm with intelligent message forwarding.
Features:
- Smart flooding (nodes don't re-forward messages they've already seen)
- Collision detection (multiple simultaneous transmissions to same node)
- Visual representation using NetworkX and Matplotlib
- Step-by-step simulation with user control
- Statistics tracking and path analysis

Usage:
    python main.py

Controls:
    - SPACE/Enter: Advance to next frame
    - 'q': Quit simulation

Author: Network Simulation Project
"""

# Import the simulator class
from simulator import Simulator

def main():
    """Main program entry point"""
    print("="*60)
    print("NETWORK FLOODING SIMULATION")
    print("="*60)
    print("This simulation demonstrates intelligent flooding algorithm")
    print("with collision detection and path discovery.")
    print()
    
    # Create simulator instance
    simulator = Simulator()
    
    try:
        # Get user input for simulation parameters
        num_nodes, num_messages, total_frames = simulator.get_user_input()
        
        # Setup the simulation
        simulator.setup_simulation(num_nodes, num_messages, total_frames)
        
        # Run the simulation
        simulator.run_simulation()
        
    except KeyboardInterrupt:
        print("\nSimulation interrupted by user (Ctrl+C)")
    except Exception as e:
        print(f"\nError occurred during simulation: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nSimulation ended.")

def run_example_simulation():
    """Run a predefined example simulation for testing"""
    print("Running example simulation...")
    
    simulator = Simulator()
    
    # Setup with predefined parameters
    simulator.setup_simulation(num_nodes=12, num_messages=3, total_frames=40)
    
    # Run simulation
    simulator.run_simulation()

def print_usage_instructions():
    """Print detailed usage instructions"""
    print("\nUSAGE INSTRUCTIONS:")
    print("-" * 40)
    print("1. Run the program: python main.py")
    print("2. Enter simulation parameters:")
    print("   - Number of nodes (10-100)")
    print("   - Number of messages")
    print("   - Total simulation frames")
    print("3. Use controls during simulation:")
    print("   - SPACE or Enter: Next frame")
    print("   - 'q': Quit simulation")
    print("\nCOLOR CODING:")
    print("- Green: Source node")
    print("- Red: Target node") 
    print("- Pink: Collision occurred")
    print("- Orange: Currently sending")
    print("- Light Blue: Normal node")
    print("\nORANGE LINES: Active transmissions this frame")
    print("ARROWS: Direction of message flow")

if __name__ == "__main__":
    # Check if user wants to see instructions
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            print_usage_instructions()
            sys.exit(0)
        elif sys.argv[1] in ["-e", "--example", "example"]:
            run_example_simulation()
            sys.exit(0)
    
    # Run main simulation
    main()