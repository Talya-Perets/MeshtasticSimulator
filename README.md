# Network Flooding Simulator

A Python-based network simulation implementing and comparing flooding algorithms with knowledge tree-based intelligent routing for Meshtastic network message propagation.

## Project Objective

This project simulates Meshtastic-style mesh network communication, implementing and comparing two network routing algorithms: 
- **Pure flooding** - every node forwards to all neighbors.
- **Tree-Based Routing** – nodes use learned paths for efficient routing. The simulation demonstrates how nodes can learn network topology through message observation and make smart routing decisions using knowledge trees to optimize message propagation in mesh networks.

## Installation and Setup

### Requirements
- Python 3.7+
- matplotlib
- networkx
- numpy

### Installation
```bash
git clone https://github.com/Talya-Perets/MeshtasticSimulator.git
cd MeshtasticSimulator
pip install -r requirements.txt
```

### Running the Program
```bash
python main.py
```

## How to Use

### Simulation Setup
1. Run `python main.py`
2. Enter simulation parameters:
   - Network size (10, 50, or 100 nodes - optimized layouts)
   - Number of test messages for algorithm comparison
   - Total simulation frames
3. Choose from the main menu:
   - **Learning Phase**: Build knowledge trees through message passing
   - **Flooding Algorithm**: Pure flooding approach
   - **Tree-Based Algorithm**: Smart routing using learned knowledge
   - **Compare Both Algorithms**: Run both algorithms and compare results
   - **Exit**

### Controls
- **SPACE**: Advance to next frame
- **Q**: Skip learning phase or quit simulation
- **R**: Reset comparison phase

## Algorithms Implemented

### 1. Pure Flooding Algorithm
A straightforward flooding approach where:
- Every node forwards messages to ALL neighbors
- Nodes stop forwarding if they are the target node or have already seen the message
- Messages continue propagating until hop limit is exhausted
- Simple but generates high network traffic
- Guaranteed delivery if path exists within hop limit

### 2. Tree-Based Intelligent Routing
An advanced routing system using knowledge trees with smart forwarding decisions:
- **Knowledge Tree Analysis**: Before forwarding, nodes check their learned knowledge trees
- **Subtree Optimization**: If the source and target nodes are both located in the same subtree, the node does not forward the message
- **Smart Path Detection**: This indicates a shorter direct path exists between source and target that doesn't require routing through the current node
- **Efficient Forwarding**: Only forwards when the node can provide a useful path, reducing unnecessary network traffic
- **Adaptive Fallback**: When subtree analysis is inconclusive or knowledge is insufficient, falls back to flooding behavior

## Two-Phase Simulation Design

### Phase 1: Learning Phase
- Predetermined message pairs sent systematically
- Each node builds knowledge trees from observed message paths
- Messages spaced based on network size (every 4/8/12 frames for 10/50/100 nodes)
- Dynamic hop limits: 4/8/12 hops for 10/50/100 node networks

### Phase 2: Algorithm Testing
- Random test messages with random source/destination pairs
- Compare flooding vs tree-based algorithm performance
- Comprehensive statistics and analysis
- Visual representation of algorithm differences

## Network Features

### Optimized Graph Layouts
- **10-node network**: Compact cluster layout
- **50-node network**: Medium complexity with balanced connectivity
- **100-node network**: Well-distributed layout with normal connectivity
- Same layout every run for reproducible experiments

### Visual Representation
- **Color Coding**:
  - Green: Source nodes
  - Red: Target nodes
  - Pink: Collision occurred
  - Orange: Currently sending
  - Light Blue: Normal nodes
- **Message Flow**: Colored arrows showing active transmissions
- **Real-time Statistics**: Message status and completion tracking

### Dynamic Parameters
- **Hop Limits**: Automatically adjusted based on network size
- **Message Timing**: Intelligent spacing to prevent overlap
- **Frame Allocation**: Sufficient time for message completion

## Project Structure
```bash
   MeshtasticSimulator/
   ├── main.py                   # Entry point
   ├── requirements.txt          # Dependency list
   ├── README.md                 # Project documentation
   └── simulator/
      ├── __init__.py
      ├── simulator.py
      ├── learning_phase_manager.py
      ├── comparison_phase_manager.py
      ├── message_processor.py
      ├── display_manager.py
      ├── network.py
      ├── node.py
      └── message.py

```
### Core Classes

**Simulator (simulator.py)**
Main orchestrator managing all simulation phases, user interface, and algorithm comparison.

**LearningPhaseManager (LearningPhaseManager.py)**
Handles the learning phase where nodes build knowledge trees through systematic message passing.

**ComparisonPhaseManager (ComparisonPhaseManager.py)**
Manages algorithm testing phase with random messages and detailed statistics tracking.

**Node (node.py)**
Represents network nodes with knowledge tree building and intelligent routing capabilities.

**Message (message.py)**
Manages message lifecycle with dynamic hop limits and path tracking.

**MessageProcessor (MessageProcessor.py)**
Handles message transmission, collision detection, and reception processing for both phases.

**DisplayManager (DisplayManager.py)**
Provides real-time visual representation of network state and message flow.

**Network (network.py)**
Creates and manages network topology with optimized layouts for different sizes.

## Statistics and Analysis

The simulator provides comprehensive analysis including:
- Message success rates for each algorithm
- Network efficiency metrics
- Resource utilization comparison
- Collision statistics
- Path length analysis
- Individual message performance breakdown
- Overall algorithm winner determination

## Key Innovations

### Knowledge Tree Learning
- Nodes learn complete path information from every observed message
- Tree structure represents how to reach any known destination
- Multiple entries per destination for redundancy

### Intelligent Routing Decisions
- Subtree analysis to avoid unnecessary forwarding
- Smart fallback to flooding when knowledge is incomplete
- Dynamic adaptation based on learned network topology

### Comprehensive Comparison
- Side-by-side algorithm performance analysis
- Detailed statistics with clear winner determination
- Visual representation of algorithm differences

## Contributors

- Hagit Dahan 315158568
- Talya Perets 322353780
- Ido Avraham 208699181

## Repository

https://github.com/Talya-Perets/MeshtasticSimulator.git