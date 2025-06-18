#!/usr/bin/env python3
"""
Flooding Network Simulation - Entry Point

This script runs the simulation using FloodingSimulator (no routing logic).
"""

from flooding_simulator import FloodingSimulator

def main():
    print("=" * 60)
    print("FLOODING-ONLY NETWORK SIMULATION")
    print("=" * 60)
    print("This simulation demonstrates a pure flooding algorithm")
    print("with duplicate message avoidance and hop limits.")
    print()

    simulator = FloodingSimulator()

    try:
        num_nodes, num_messages, total_frames = simulator.get_user_input()
        simulator.setup_simulation(num_nodes, num_messages, total_frames)
        # use_predefined = input("Use predefined layout? (y/n): ").lower().strip() == 'y'
        # simulator.setup_simulation(num_nodes, num_messages, total_frames, use_predefined_layout=use_predefined)
        simulator.run_simulation()

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user.")
    except Exception as e:
        print(f"\nError occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("\nFlooding simulation ended.")

def run_example_simulation():
    """Run a predefined example flooding simulation"""
    print("Running predefined flooding simulation...")

    simulator = FloodingSimulator()
    simulator.setup_simulation(num_nodes=15, num_messages=5, total_frames=60)
    simulator.run_simulation()

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] in ["-h", "--help", "help"]:
            print("Usage: python main_flooding.py")
            print("       (or add -e / --example to run a sample)")
            sys.exit(0)
        elif sys.argv[1] in ["-e", "--example", "example"]:
            run_example_simulation()
            sys.exit(0)

    main()
