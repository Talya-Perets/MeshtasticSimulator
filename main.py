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
- FIXED graph layouts for reproducible experiments
- Modular design with separate managers for different phases
- 5-option menu system for flexible simulation control

Usage:
    python main.py                 # Interactive mode
    python main.py --preset 10     # Quick start with 10-node fixed graph
    python main.py --preset 50     # Quick start with 50-node fixed graph
    python main.py --preset 100    # Quick start with 100-node fixed graph

Controls:
    - SPACE/Enter: Advance to next frame
    - 'q': Quit simulation or skip learning

Author: Network Simulation Project
"""

# Import the refactored simulator class
from simulator.simulator import Simulator
import sys

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
        # Check for preset arguments
        if len(sys.argv) > 2 and sys.argv[1] == "--preset":
            preset_size = int(sys.argv[2])
            if preset_size in [10, 50, 100]:
                print(f"Using preset: {preset_size}-node optimized graph")
                num_nodes = preset_size
                
                # Scale messages appropriately for each graph size
                if preset_size == 10:
                    num_messages = 3
                elif preset_size == 50:
                    num_messages = 5
                else:  # 100 nodes
                    num_messages = 8  # More messages for larger graph
                    
                total_frames = 60
            else:
                print(f"Invalid preset size {preset_size}. Available: 10, 50, 100")
                return
        else:
            # Get user input for simulation parameters
            num_nodes, num_messages, total_frames = simulator.get_user_input()
        
        # Setup the simulation (without skip_learning parameter)
        simulator.setup_simulation(num_nodes, num_messages, total_frames)
        
        # Run the simulation with 5-option menu
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
    print("Running example simulation with 10-node optimized graph...")
    
    simulator = Simulator()
    
    # Setup with predefined parameters using optimized graph
    simulator.setup_simulation(num_nodes=10, num_messages=3, total_frames=40)
    
    # Run simulation
    simulator.run_simulation()

def run_comparison_demo():
    """Run demonstrations of all optimized graph sizes"""
    print("OPTIMIZED GRAPHS COMPARISON DEMO")
    print("="*50)
    
    fixed_sizes = [10, 50, 100]
    messages_for_size = {10: 3, 50: 5, 100: 8}
    
    for size in fixed_sizes:
        print(f"\nDemonstrating {size}-node optimized graph...")
        if size == 100:
            print("   (Well distributed with normal connectivity)")
        input("Press Enter to continue...")
        
        simulator = Simulator()
        messages = messages_for_size[size]
        simulator.setup_simulation(num_nodes=size, num_messages=messages, total_frames=60)
        
        print(f"Graph created! Each run will show the SAME optimized layout.")
        input("Press Enter to close and try next size...")

def print_usage_instructions():
    """Print detailed usage instructions"""
    print("\nUSAGE INSTRUCTIONS:")
    print("-" * 40)
    print("BASIC USAGE:")
    print("  python main.py                    # Interactive mode with 5-option menu")
    print("  python main.py --preset 10        # Quick 10-node fixed graph")
    print("  python main.py --preset 50        # Quick 50-node fixed graph") 
    print("  python main.py --preset 100       # Quick 100-node fixed graph")
    print("\nOPTIMIZED GRAPH LAYOUTS:")
    print("  Size 10: Compact cluster - good for basic flooding")
    print("  Size 50: Medium complexity - balanced connectivity") 
    print("  Size 100: Well distributed - normal connectivity, good spread")
    print("  Same layout every time - perfect for reproducible experiments")
    print("\n5-OPTION MENU SYSTEM:")
    print("  1. Learning Phase - Build knowledge trees")
    print("  2. Flooding Algorithm - Pure flooding approach")
    print("  3. Tree-Based Algorithm - Smart routing with learned knowledge")
    print("  4. Algorithm Comparison - Run both and compare results")
    print("  5. Exit - End simulation")
    print("\nFLEXIBLE EXECUTION:")
    print("  • Run learning phase separately when needed")
    print("  • Test algorithms with or without learning")
    print("  • Return to menu after each operation")
    print("  • No forced sequence - choose what to run")
    print("\nSIMULATION SETUP:")
    print("1. Choose graph size (10, 50, or 100)")
    print("2. Enter number of comparison messages")
    print("3. Enter simulation frames")
    print("4. Use menu to choose what to run")
    print("\nCONTROLS DURING SIMULATION:")
    print("   - SPACE: Advance to next frame")
    print("   - Q: Skip learning phase or quit simulation")
    print("   - R: Reset comparison phase")
    print("\nCOLOR CODING:")
    print("- Green: Source node")
    print("- Red: Target node") 
    print("- Pink: Collision occurred")
    print("- Orange: Currently receiving")
    print("- Light Blue: Normal node")
    print("\nCOLORED LINES: Active transmissions this frame")
    print("ARROWS: Direction of message flow")
    print("\nIMPROVED ARCHITECTURE:")
    print("- Modular design with separate phase managers")
    print("- Flexible menu system for better control")
    print("- Independent learning and comparison phases")
    print("- Enhanced user experience with clear options")

if __name__ == "__main__":
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            print_usage_instructions()
            sys.exit(0)
        elif sys.argv[1] in ["-e", "--example", "example"]:
            run_example_simulation()
            sys.exit(0)
        elif sys.argv[1] in ["-c", "--compare", "compare"]:
            run_comparison_demo()
            sys.exit(0)
        elif sys.argv[1] == "--preset":
            if len(sys.argv) < 3:
                print("Error: --preset requires a size argument (10, 50, or 100)")
                print("Example: python main.py --preset 50")
                sys.exit(1)
    
    # Run main simulation
    main()