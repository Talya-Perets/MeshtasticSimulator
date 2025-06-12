import matplotlib.pyplot as plt
import math
import random
from collections import defaultdict

# Import our custom classes
from message import Message
from node import Node
from network import Network

class Simulator:
    """
    Main simulator class that manages the simulation flow, display, and user interaction
    """
    
    def __init__(self):
        # Network instance
        self.network = Network()
        
        # Messages
        self.messages = {}  # Dictionary: message_id -> Message object
        
        # Simulation parameters
        self.total_frames = 60  # Default frame count
        self.current_frame = 0
        
        # Statistics tracking
        self.stats = {
            'messages_completed': 0,
            'messages_reached_target': 0,
            'messages_hop_limit_exceeded': 0,
            'total_collisions': 0,
            'collisions_per_frame': [],
            'active_messages_per_frame': []
        }
        
        # Display settings
        self.fig = None
        self.ax = None
        
        # Simulation control
        self.is_running = False
        self.simulation_paused = True
        
        # Messages completed this frame (cleared after display)
        self.completed_this_frame = []
        
    def setup_simulation(self, num_nodes, num_messages, total_frames=60):
        """Initialize simulation with user parameters"""
        self.total_frames = total_frames
        self.current_frame = 0
        
        print(f"Setting up simulation: {num_nodes} nodes, {num_messages} messages, {total_frames} frames")
        
        # Create nodes and position them
        self.network.create_nodes(num_nodes)
        
        # Create network connections
        self.network.create_network_connections()
        
        # Generate random messages
        self._generate_messages(num_messages)
        
        # Initialize statistics
        self._initialize_statistics()
        
        print("Simulation setup complete!")
        self._print_setup_summary()
 
    def _generate_messages(self, num_messages):
        """Generate random messages for the simulation"""
        self.messages.clear()
        node_ids = list(self.network.nodes.keys())
        
        for msg_id in range(num_messages):
            # Choose random source and target (different nodes)
            source = random.choice(node_ids)
            target = random.choice([n for n in node_ids if n != source])
            
            # Create message
            message = Message(msg_id, source, target, self.total_frames)
            self.messages[msg_id] = message
        
    def _initialize_statistics(self):
        """Initialize statistics tracking"""
        self.stats = {
            'messages_completed': 0,
            'messages_reached_target': 0,
            'messages_hop_limit_exceeded': 0,
            'total_collisions': 0,
            'collisions_per_frame': [0] * self.total_frames,
            'active_messages_per_frame': [0] * self.total_frames
        }
        
    def _print_setup_summary(self):
        """Print summary of simulation setup"""
        print("\n" + "="*50)
        print("SIMULATION SETUP SUMMARY")
        print("="*50)
        
        self.network.print_network_summary()
        print(f"Simulation: {self.total_frames} frames")
        print(f"Messages: {len(self.messages)}")
        
        print("\nMessages Details:")
        for msg_id, message in self.messages.items():
            print(f"  {message}")
            
        print("="*50)
        
    def get_user_input(self):
        """Get simulation parameters from user"""
        print("Network Flooding Simulator Setup")
        print("-" * 30)
        
        try:
            num_nodes = int(input("Enter number of nodes (10-100): "))
            if not 10 <= num_nodes <= 100:
                print("Using default: 15 nodes")
                num_nodes = 15
                
            num_messages = int(input("Enter number of messages: "))
            if num_messages < 1:
                print("Using default: 5 messages")
                num_messages = 5
                
            total_frames = int(input("Enter total simulation frames (default 60): ") or "60")
            if total_frames < 10:
                print("Using minimum: 60 frames")
                total_frames = 60
                
        except ValueError:
            print("Invalid input, using defaults: 15 nodes, 5 messages, 60 frames")
            num_nodes, num_messages, total_frames = 15, 5, 60
            
        return num_nodes, num_messages, total_frames
        
    def initialize_display(self):
        """Initialize matplotlib display with keyboard controls"""
        plt.ion()  # Turn on interactive mode
        self.fig, (self.ax, self.info_ax) = plt.subplots(1, 2, figsize=(16, 8))
        
        # Main network display
        self.ax.set_title("Network Flooding Simulation")
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # Information panel
        self.info_ax.set_title("Messages & Statistics")
        self.info_ax.axis('off')
        
        # Connect keyboard events
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Try to focus the window (different methods for different backends)
        try:
            # For Qt backend
            if hasattr(self.fig.canvas, 'setFocus'):
                self.fig.canvas.setFocus()
            # For Tkinter backend
            elif hasattr(self.fig.canvas, 'get_tk_widget'):
                self.fig.canvas.get_tk_widget().focus_set()
            # For other backends
            elif hasattr(self.fig.canvas, 'manager'):
                if hasattr(self.fig.canvas.manager, 'window'):
                    self.fig.canvas.manager.window.wm_attributes('-topmost', True)
                    self.fig.canvas.manager.window.wm_attributes('-topmost', False)
        except:
            # If focus setting fails, that's okay - user can click on window
            pass
        
        plt.tight_layout()
        
        # Show control instructions
        self._show_controls()
        
    def _show_controls(self):
        """Show control instructions"""
        controls_text = "CONTROLS: SPACE=Next Frame | Q=Quit | R=Reset | (Click window first!)"
        self.fig.suptitle(controls_text, fontsize=11, y=0.96)
        
    def on_key_press(self, event):
        """Handle keyboard input"""
        if not self.is_running:
            return
            
        if event.key == ' ':  # Space bar
            if self.current_frame >= self.total_frames:
                print("Simulation already completed!")
                return
            print(f"SPACE pressed - Advancing to frame {self.current_frame + 1}")
            self.advance_frame()
            
        elif event.key == 'q':  # Quit
            print("Q pressed - Quitting simulation...")
            self.is_running = False
            plt.close()
            
        elif event.key == 'r':  # Reset (bonus feature)
            print("R pressed - Resetting simulation...")
            self.current_frame = 0
            self._reset_simulation()
            
        else:
            # Give feedback for other keys
            print(f"Key '{event.key}' pressed. Use SPACE=Next, Q=Quit, R=Reset")
            
    def advance_frame(self):
            """Advance simulation by one frame"""
            if self.current_frame >= self.total_frames:
                print("Simulation completed!")
                return
                
            # Execute frame
            self.execute_frame()
            
            # Update display AFTER frame execution
            self.update_display()
            
            # Clear completed messages after display
            if hasattr(self, 'completed_this_frame'):
                self.completed_this_frame.clear()
            
            # Check completion
            if all(msg.is_completed for msg in self.messages.values()):
                print(f"\nAll messages completed at frame {self.current_frame}!")
                self._show_final_statistics()
                
            elif self.current_frame >= self.total_frames:
                print(f"\nSimulation completed after {self.total_frames} frames!")
                self._show_final_statistics()

    def _reset_simulation(self):
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
            
        # Reset all nodes
        self.network.reset_all_nodes()
                
        # Reset statistics
        self._initialize_statistics()
        
        # Update display
        self.update_display()
        print("Simulation reset to frame 0")

    def draw_network(self):
        """Draw the current state of the network"""
        # Clear axes completely 
        self.ax.clear()
        self.ax.cla()  # Extra clear
        self.ax.set_title(f"Network Flooding Simulation - Frame {self.current_frame}/{self.total_frames}")
        self.ax.set_aspect('equal')
        self.ax.grid(True, alpha=0.3)
        
        # Draw edges (connections) - GRAY BACKGROUND FIRST
        for edge in self.network.graph.edges():
            node1, node2 = edge
            pos1 = self.network.node_positions[node1]
            pos2 = self.network.node_positions[node2]
            
            self.ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], 
                        'gray', linewidth=1, alpha=0.6, zorder=1)
        
        # Draw nodes with current colors
        print(f"🎨 Drawing nodes with colors:")
        for node_id, node in self.network.nodes.items():
            pos = self.network.node_positions[node_id]
            color = node.get_display_color()
            
            # Draw node circle
            circle = plt.Circle(pos, 0.15, color=color, zorder=3)
            self.ax.add_patch(circle)
            
            # Add node label
            self.ax.text(pos[0], pos[1], str(node_id), 
                        ha='center', va='center', fontsize=10, 
                        fontweight='bold', zorder=4)
        
        # Draw active message transmissions - LAST, ON TOP
        self._draw_active_transmissions()
        
        # Set axis limits
        positions = list(self.network.node_positions.values())
        x_coords = [pos[0] for pos in positions]
        y_coords = [pos[1] for pos in positions]
        
        margin = 0.5
        self.ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
        self.ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)
        
    def _draw_active_transmissions(self):
        """Draw lines for ALL neighbors that senders are transmitting to - with different colors per message"""
        transmission_count = 0
        
        # Define colors for different messages (cycle through if more messages than colors)
        message_colors = ['orange', 'purple', 'brown', 'blue', 'cyan', 'green', 'magenta', 'red']
        
        # We need to track what messages each SENDING node is transmitting
        # Since pending_messages is cleared, we need to get this info from the transmission queue
        
        # Draw lines from all SENDING nodes to ALL their neighbors
        for node_id, node in self.network.nodes.items():
            if node.status_flags[node.STATUS_SENDING] == True:
                sender_pos = self.network.node_positions[node_id]
                
                # Get messages this node is sending from the stored transmission info
                messages_from_node = {}
                if hasattr(self, '_current_transmissions'):
                    for sender_id, receiver_id, message, sender_path, hop_limit in self._current_transmissions:
                        if sender_id == node_id:
                            if message.id not in messages_from_node:
                                messages_from_node[message.id] = message
                
                # If no stored transmissions, use all active messages (fallback)
                if not messages_from_node:
                    for message in self.messages.values():
                        if message.is_active and not message.is_completed:
                            messages_from_node[message.id] = message
                
                # Draw lines to ALL neighbors for each message with its color
                for neighbor_id in node.neighbors:
                    neighbor_pos = self.network.node_positions[neighbor_id]
                    
                    # Draw a line for each message this node is sending
                    for message_id, message in messages_from_node.items():
                        # Get color for this message (cycle through colors)
                        color = message_colors[message_id % len(message_colors)]
                        
                        # Offset lines slightly so multiple messages are visible
                        offset = (message_id - len(messages_from_node)/2) * 0.02
                        
                        # Calculate offset perpendicular to the line
                        dx = neighbor_pos[0] - sender_pos[0]
                        dy = neighbor_pos[1] - sender_pos[1]
                        length = math.sqrt(dx*dx + dy*dy)
                        
                        if length > 0:
                            # Perpendicular offset
                            perp_x = -dy / length * offset
                            perp_y = dx / length * offset
                            
                            start_x = sender_pos[0] + perp_x
                            start_y = sender_pos[1] + perp_y
                            end_x = neighbor_pos[0] + perp_x
                            end_y = neighbor_pos[1] + perp_y
                            
                            # Draw transmission line with message-specific color and THICKER line
                            self.ax.plot([start_x, end_x], [start_y, end_y], 
                                    color=color, linewidth=2.5, alpha=0.9, zorder=2)
                            
                            # Add BIGGER and THICKER arrow to show direction
                            dx_norm = dx / length * 0.25  # Bigger arrow
                            dy_norm = dy / length * 0.25
                            
                            arrow_x = end_x - dx_norm
                            arrow_y = end_y - dy_norm
                            
                            self.ax.annotate('', xy=(end_x, end_y), xytext=(arrow_x, arrow_y),
                                        arrowprops=dict(arrowstyle='->', color=color, 
                                                        lw=3, alpha=0.9, shrinkA=0, shrinkB=0), zorder=2)
                            
                            transmission_count += 1
        
        # Add legend if there are transmissions
        if transmission_count > 0:
            # Get unique messages being transmitted
            active_messages = set()
            if hasattr(self, '_current_transmissions'):
                for sender_id, receiver_id, message, sender_path, hop_limit in self._current_transmissions:
                    active_messages.add(message.id)
            
            # Create legend entries with message IDs
            legend_elements = []
            for msg_id in sorted(active_messages):
                color = message_colors[msg_id % len(message_colors)]
                line = plt.Line2D([0], [0], color=color, linewidth=2.5, 
                                label=f'Msg {msg_id}')
                legend_elements.append(line)
            
            if legend_elements:
                self.ax.legend(handles=legend_elements, loc='upper right', fontsize=9, 
                             frameon=True, fancybox=True, shadow=True)
        
        if transmission_count == 0:
            print(f"   ✨ No SENDING nodes - screen should have NO colored lines!")
        else:
            print(f"   📡 Drawing {transmission_count} transmissions with message-specific colors")

    def draw_info_panel(self):
        """Draw simple, clean information panel"""
        self.info_ax.clear()
        self.info_ax.set_title(f"Messages & Statistics - Frame {self.current_frame}/{self.total_frames}", fontsize=12, fontweight='bold')
        self.info_ax.axis('off')
        
        y_pos = 0.95
        line_height = 0.035
        
        def add_text(text, y, fontsize=10, color='black', weight='normal'):
            self.info_ax.text(0.02, y, text, transform=self.info_ax.transAxes,
                            fontsize=fontsize, verticalalignment='top', 
                            fontfamily='monospace', color=color, fontweight=weight)
            return y - line_height
        
        def add_header(title, y):
            y = add_text(title, y, fontsize=11, weight='bold')
            y = add_text("-" * len(title), y-0.015, fontsize=10)
            return y - 0.01
        
        # ALL MESSAGES
        y_pos = add_header("ALL MESSAGES", y_pos)
        
        # Sort messages by start frame, then by message ID
        sorted_messages = sorted(self.messages.items(), key=lambda x: (x[1].start_frame, x[0]))
        
        for msg_id, message in sorted_messages:
            if not message.is_completed:
                # Show basic message info
                y_pos = add_text(f"Message {msg_id}: {message.source} -> {message.target} (Start: Frame {message.start_frame})", 
                            y_pos)
                
                # Show hop limit if message is active
                if message.is_active:
                    # Calculate current hop limit
                    current_min_hops = "?"
                    min_hops_found = []
                    
                    for node_id, node in self.network.nodes.items():
                        for pending_item in node.pending_messages:
                            if len(pending_item) >= 3:
                                pending_msg, path, local_hop_limit = pending_item
                                if pending_msg.id == message.id:
                                    min_hops_found.append(local_hop_limit)
                    
                    if min_hops_found:
                        current_min_hops = min(min_hops_found)
                    else:
                        current_min_hops = 0
                    
                    y_pos = add_text(f"  Hop Limit: {current_min_hops}/{message.hop_limit}", y_pos, fontsize=9)
                
                y_pos -= 0.01
        
        y_pos -= 0.02
        
        # COMPLETED MESSAGES
        y_pos = add_header("COMPLETED MESSAGES", y_pos)
        
        completed_found = False
        # Sort completed messages by message ID
        sorted_completed = sorted([(msg_id, msg) for msg_id, msg in self.messages.items() if msg.is_completed])
        
        for msg_id, message in sorted_completed:
                completed_found = True
                
                # Use the message's own status
                status = message.get_status()
                
                if status == "SUCCESS":
                    y_pos = add_text(f"Message {msg_id}: {message.source} -> {message.target} - SUCCESS", 
                                y_pos, color='green', weight='bold')
                else:
                    y_pos = add_text(f"Message {msg_id}: {message.source} -> {message.target} - FAILED", 
                                y_pos, color='red', weight='bold')
                
                y_pos -= 0.01
        
        if not completed_found:
            y_pos = add_text("None", y_pos)
        
        y_pos -= 0.02
        
        # Simple collision info
        current_collisions = sum(1 for node in self.network.nodes.values() 
                            if node.status_flags[node.STATUS_COLLISION])
        
        if current_collisions > 0:
            y_pos = add_header("COLLISIONS", y_pos)
            y_pos = add_text(f"Collisions this frame: {current_collisions}", y_pos)   


    def update_display(self):
        """Update the complete display"""
        self.draw_network()
        self.draw_info_panel()
        plt.draw()
        plt.pause(0.01)  # Small pause to allow display update
        
    def run_simulation(self):
        """Run the complete simulation with keyboard controls"""
        print("\nStarting simulation...")
        print("Setting up display window...")
        
        self.initialize_display()
        self.current_frame = 0  # Start from frame 0, first execution will be frame 1
        self.is_running = True
        
        # Initial display (frame 0 - setup)
        self.update_display()
        
        print("\n" + "="*50)
        print("🎮 SIMULATION READY!")
        print("="*50)
        print("Controls:")
        print("  SPACE: Advance to next frame")
        print("  Q: Quit simulation") 
        print("  R: Reset simulation")
        print("\n👆 Click on the simulation window and press SPACE to begin!")
        print("="*50)
        
        # Keep the simulation running until user quits
        try:
            while self.is_running:
                plt.pause(0.1)  # Small pause to keep GUI responsive
                
                # Check if window is still open
                if not plt.get_fignums():
                    self.is_running = False
                    break
                    
        except KeyboardInterrupt:
            print("\nSimulation interrupted")
            
        print("Simulation ended.")
        
    def execute_frame(self):
            """Execute one simulation frame"""
            print(f"\n{'='*50}")
            print(f"EXECUTING FRAME {self.current_frame + 1}")  # Show next frame number
            print(f"{'='*50}")
            
            # Reset all nodes FIRST (clear old SENDING status)
            for node_id, node in self.network.nodes.items():
                node.reset_frame_status()
            
            # Re-mark source and target nodes for ACTIVE messages only
            for message in self.messages.values():
                if message.is_active and not message.is_completed:
                    self.network.nodes[message.source].set_as_source(True)
                    self.network.nodes[message.target].set_as_target(True)
            
                
            # Start messages that begin this frame
            self._start_messages_for_frame()
            
            # Process message transmissions
            self._process_transmissions()
            
            # Update statistics
            self._update_frame_statistics()
            
            # Advance to next frame
            self.current_frame += 1
            
                
    def _start_messages_for_frame(self):
        """Start messages that should begin this frame"""
        for message in self.messages.values():
            if message.start_frame == (self.current_frame + 1) and not message.is_active:
                message.start_transmission()
                
                # Mark source and target nodes
                self.network.nodes[message.source].set_as_source(True)
                self.network.nodes[message.target].set_as_target(True)
                
                # Add message to source node's pending list (source starts with the message)
                initial_path = [message.source]
                self.network.nodes[message.source].pending_messages.append((message, initial_path))
                
                print(f"🚀 Started message {message.id}: {message.source}→{message.target}")
                print(f"    Hop limit: {message.hop_limit} | Current hops: {message.current_hops}")

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
        newly_completed = 0
        for message in self.messages.values():
            if message.is_completed and not hasattr(message, '_stats_counted'):
                message._stats_counted = True  # Mark as counted
                newly_completed += 1
                
                # Use the message's own status
                if message.get_status() == "SUCCESS":
                    self.stats['messages_reached_target'] += 1  # Success: target received
                    print(f"      ✅ Message {message.id} SUCCESS: Target reached")
                else:
                    self.stats['messages_hop_limit_exceeded'] += 1  # Failed: never reached target
                    print(f"      ❌ Message {message.id} FAILED: Target never reached")
                    
        print(f"📊 Frame {self.current_frame} stats: Active={active_count}, Collisions={collision_count}, Completed={newly_completed}")
        
        # Show current message status with hop limits
        for msg_id, message in self.messages.items():
            if message.is_active:
                # Find current hop limits for this message
                hop_limits = []
                for node_id, node in self.network.nodes.items():
                    for pending_item in node.pending_messages:
                        if len(pending_item) >= 3:
                            pending_msg, path, local_hop_limit = pending_item
                            if pending_msg.id == message.id:
                                hop_limits.append(local_hop_limit)
                
                status_info = f"(State: {message.get_state()})"
                if hop_limits:
                    min_hops = min(hop_limits)
                    max_hops = max(hop_limits)
                    if min_hops == max_hops:
                        print(f"    Message {msg_id}: {min_hops}/{message.hop_limit} hops remaining {status_info}")
                    else:
                        print(f"    Message {msg_id}: {min_hops}-{max_hops}/{message.hop_limit} hops remaining {status_info}")
                else:
                    print(f"    Message {msg_id}: finishing up... {status_info}")
            elif message.is_completed:
                status = message.get_status()
                print(f"    Message {msg_id}: COMPLETED (State: {message.get_state()}, Status: {status})")

    def _check_stalled_messages(self):
        """Check for messages that have no pending copies and should be completed"""
        print("🔍 Checking for stalled messages with no pending copies...")
        
        for message in self.messages.values():
            if message.is_active and not message.is_completed:
                # Check if this message has any pending copies anywhere
                has_pending = False
                
                for node_id, node in self.network.nodes.items():
                    for pending_item in node.pending_messages:
                        if len(pending_item) >= 2:
                            pending_msg = pending_item[0]
                            if pending_msg.id == message.id:
                                has_pending = True
                                break
                    if has_pending:
                        break
                
                if not has_pending:
                    print(f"    🚫 Message {message.id} has no pending copies - COMPLETING as expired")
                    message.complete_message("hop_limit_exceeded")
                    self._clear_message_status(message)

    def _process_transmissions(self):
        """Process all message transmissions for this frame"""
        print("Processing transmissions...")
        
        # CRITICAL FIX: Check for expired messages FIRST before any processing
        print("🔍 Checking for expired messages with hop limit 0...")
        expired_count = 0
        
        for node_id, node in self.network.nodes.items():
            expired_indices = []
            for i, pending_item in enumerate(node.pending_messages):
                if len(pending_item) >= 3:
                    message, path, local_hop_limit = pending_item
                    if local_hop_limit <= 0 and not message.is_completed:
                        print(f"    🚫 Found expired message {message.id} at node {node_id} (hop_limit: {local_hop_limit})")
                        message.complete_message("hop_limit_exceeded")
                        self._clear_message_status(message)
                        expired_indices.append(i)
                        expired_count += 1
                elif len(pending_item) == 2:
                    # Handle old format
                    message, path = pending_item
                    hops_used = len(path) - 1
                    local_hop_limit = message.hop_limit - hops_used
                    if local_hop_limit <= 0 and not message.is_completed:
                        print(f"    🚫 Found expired message {message.id} at node {node_id} (calculated hop_limit: {local_hop_limit})")
                        message.complete_message("hop_limit_exceeded")
                        self._clear_message_status(message)
                        expired_indices.append(i)
                        expired_count += 1
            
            # Remove expired messages from pending (in reverse order to maintain indices)
            for i in reversed(expired_indices):
                node.pending_messages.pop(i)
        
        if expired_count > 0:
            print(f"    ✅ Completed {expired_count} expired messages")
        
        # NEW: Check for stalled messages with no pending copies
        self._check_stalled_messages()
        
        # Phase 1: All nodes send their pending messages
        transmission_queue = []  # List of (sender_id, receiver_id, message, path, hop_limit)
        
        for sender_id, sender_node in self.network.nodes.items():
            if sender_node.pending_messages:
                
                # Filter out completed messages BEFORE sending
                active_pending = []
                for pending_item in sender_node.pending_messages:
                    if len(pending_item) == 2:
                        # Old format - calculate hop limit
                        message, current_path = pending_item
                        hops_used = len(current_path) - 1
                        local_hop_limit = message.hop_limit - hops_used
                    else:
                        # New format - hop limit already calculated
                        message, current_path, local_hop_limit = pending_item
                    
                    if message.is_completed:
                        print(f"    🚫 Removing completed msg {message.id} from node {sender_id}")
                        continue
                    elif not message.is_active:
                        print(f"    🚫 Removing inactive msg {message.id} from node {sender_id}")
                        continue
                    elif local_hop_limit <= 0:
                        print(f"    🚫 Message {message.id} hop limit reached (hop_limit: {local_hop_limit}) - COMPLETING")
                        # CRITICAL FIX: Complete the message when hop limit is exhausted
                        if not message.is_completed:
                            message.complete_message("hop_limit_exceeded")
                            self._clear_message_status(message)
                        continue
                    else:
                        active_pending.append((message, current_path, local_hop_limit))
                
                sender_node.pending_messages = active_pending
                
                # Process each message separately  
                has_transmissions = False
                
                for message, current_path, local_hop_limit in sender_node.pending_messages:
                    print(f"    📤 Processing msg {message.id} from node {sender_id}")
                    print(f"       Current path: {' → '.join(map(str, current_path))}")
                    print(f"       Local hop limit: {local_hop_limit}")
                    
                    valid_neighbors = []
                    
                    for neighbor_id in sender_node.neighbors:
                        # Only skip immediate ping-pong
                        if len(current_path) > 1 and neighbor_id == current_path[-2]:
                            continue
                        
                        # Send to all other neighbors
                        valid_neighbors.append(neighbor_id)
                    
                    if valid_neighbors:
                        has_transmissions = True
                        
                        for neighbor_id in valid_neighbors:
                            transmission_queue.append((sender_id, neighbor_id, message, current_path, local_hop_limit))
                    
                # Mark as SENDING if node has any transmissions (for drawing lines)
                if has_transmissions:
                    sender_node.set_sending()
                
                sender_node.pending_messages.clear()
        
        # STORE transmission queue for drawing
        self._current_transmissions = transmission_queue
        
        
        # CRITICAL: Detect collisions BEFORE processing
        # Group transmissions by receiver to detect collisions
        transmissions_by_receiver = {}
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
                print(f"   💥 COLLISION detected at node {receiver_id}!")
                print(f"      Senders: {sender_list}")
                print(f"      Messages: {message_list}")
                
                # Mark receiver as having collision
                self.network.nodes[receiver_id].set_collision()
        
        # Phase 2: All nodes receive messages simultaneously (but only if no collision)
        successful_receives = []
        
        for sender_id, receiver_id, message, sender_path, hop_limit in transmission_queue:
            receiver_node = self.network.nodes[receiver_id]
            
            if receiver_id in collision_nodes:
                # This receiver has collision - reject ALL messages
                print(f"   💥 COLLISION: {sender_id} → {receiver_id} (msg {message.id}) - BLOCKED by collision")
            else:
                # No collision - try to receive normally
                accepted = receiver_node.receive_message_copy(message, sender_id, sender_path)
                
                if accepted:
                    successful_receives.append((sender_id, receiver_id, message.id))
                    print(f"   ✅ ACCEPTED: {sender_id} → {receiver_id} (msg {message.id})")
                else:
                    print(f"   ❌ REJECTED: {sender_id} → {receiver_id} (msg {message.id}) - already seen")
        
        # Phase 3: Process received messages and mark receiving nodes
        completed_messages_this_frame = []
        
        for node_id, node in self.network.nodes.items():
            if node_id in collision_nodes:
                # Clear any received messages due to collision
                node.received_messages.clear()
                continue
                
            if node.received_messages:
                
                # Mark as RECEIVING (orange) if not source/target
                if not node.status_flags[node.STATUS_SOURCE] and not node.status_flags[node.STATUS_TARGET]:
                    node.set_receiving()
                else:
                    print(f"    📝 Node {node_id} received message but stays {node.get_display_color()} (source/target priority)")
                
                # Process the received messages
                processed = node.process_received_messages()
                
                for message, path in processed:
                    if message.is_completed:
                        completed_messages_this_frame.append(message)
                        # IMMEDIATE CLEANUP when message completes
                        self._clear_message_status(message)
                    else:
                        remaining_hops = message.hop_limit - len(path) + 1
        
        self.completed_this_frame = completed_messages_this_frame                 
   
    def _clear_message_status(self, completed_message):
        """Clear source/target status when message completes AND remove from all pending"""
        source_id = completed_message.source
        target_id = completed_message.target
        message_id = completed_message.id
        
        print(f"   🧹 Clearing status for completed message {message_id} ({source_id}→{target_id})")
        
        # Remove this message from ALL nodes' pending_messages
        for node_id, node in self.network.nodes.items():
            original_count = len(node.pending_messages)
            
            # CRITICAL FIX: Handle both old format (msg, path) and new format (msg, path, hop_limit)
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
            removed_count = original_count - len(node.pending_messages)
            if removed_count > 0:
                print(f"     ↳ Removed {removed_count} copies of msg {message_id} from node {node_id}")
        
        # CRITICAL: Check if source has OTHER active messages
        source_has_other_active = any(
            msg.is_active and not msg.is_completed and msg.source == source_id 
            for msg in self.messages.values() 
            if msg != completed_message
        )
        if not source_has_other_active:
            self.network.nodes[source_id].set_as_source(False)
            print(f"     ↳ Node {source_id} no longer GREEN (no other active messages as source)")
        else:
            print(f"     ↳ Node {source_id} stays GREEN (has other active messages as source)")
            
        # CRITICAL: Check if target has OTHER active messages
        target_has_other_active = any(
            msg.is_active and not msg.is_completed and msg.target == target_id 
            for msg in self.messages.values() 
            if msg != completed_message
        )
        if not target_has_other_active:
            self.network.nodes[target_id].set_as_target(False)
            print(f"     ↳ Node {target_id} no longer RED (no other active messages as target)")
        else:
            print(f"     ↳ Node {target_id} stays RED (has other active messages as target)")

    def _show_final_statistics(self):
        """Display final simulation statistics"""
        print("\n" + "="*60)
        print("FINAL SIMULATION STATISTICS")
        print("="*60)
        
        total_messages = len(self.messages)
        successful = self.stats['messages_reached_target']
        expired = self.stats['messages_hop_limit_exceeded']
        
        print(f"Total Messages: {total_messages}")
        print(f"Successful: {successful} ({successful/total_messages*100:.1f}%)")
        print(f"Expired: {expired} ({expired/total_messages*100:.1f}%)")
        print(f"Total Collisions: {self.stats['total_collisions']}")
        
        # Collision statistics
        max_collisions = max(self.stats['collisions_per_frame'])
        avg_collisions = sum(self.stats['collisions_per_frame']) / len(self.stats['collisions_per_frame'])
        
        print(f"Max Collisions per Frame: {max_collisions}")
        print(f"Average Collisions per Frame: {avg_collisions:.1f}")
        
        # Message path analysis
        print(f"\nMessage Path Analysis:")
        for msg_id, message in self.messages.items():
            print(f"Message {msg_id} ({message.source}→{message.target}):")
            print(f"  Total paths discovered: {len(message.paths)}")
            if message.paths:
                shortest_path = min(message.paths, key=len)
                longest_path = max(message.paths, key=len)
                print(f"  Shortest path: {shortest_path} (length: {len(shortest_path)})")
                print(f"  Longest path: {longest_path} (length: {len(longest_path)})")
                
        print("="*60)