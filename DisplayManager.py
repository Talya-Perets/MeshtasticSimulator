import matplotlib.pyplot as plt
import math

class DisplayManager:
    """
    Manages the visual display of the simulation
    Handles network visualization, info panels, and user input
    """
    
    def __init__(self, network):
        self.network = network
        self.fig = None
        self.ax = None
        self.info_ax = None
        self.is_running = False
        
        # Current display state
        self.current_mode = "learning"  # "learning" or "comparison"
        self.current_frame = 0
        self.total_frames = 0
        self.current_transmissions = []
        
        # Callback for key events (set by main simulator)
        self.key_callback = None
        
    def set_key_callback(self, callback):
        """Set callback function for keyboard events"""
        self.key_callback = callback
        
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
        
        # Try to focus the window
        try:
            if hasattr(self.fig.canvas, 'setFocus'):
                self.fig.canvas.setFocus()
            elif hasattr(self.fig.canvas, 'get_tk_widget'):
                self.fig.canvas.get_tk_widget().focus_set()
            elif hasattr(self.fig.canvas, 'manager'):
                if hasattr(self.fig.canvas.manager, 'window'):
                    self.fig.canvas.manager.window.wm_attributes('-topmost', True)
                    self.fig.canvas.manager.window.wm_attributes('-topmost', False)
        except:
            pass
        
        plt.tight_layout()
        self._show_controls()
        
    def set_mode(self, mode, current_frame, total_frames):
        """Set display mode and frame information"""
        self.current_mode = mode
        self.current_frame = current_frame
        self.total_frames = total_frames
        self._show_controls()
        
    def set_transmissions(self, transmissions):
        """Set current transmissions for display"""
        self.current_transmissions = transmissions
        
    def _show_controls(self):
        """Show control instructions based on current mode"""
        if self.current_mode == "learning":
            controls_text = f"LEARNING MODE: SPACE=Next Frame | Q=Skip Learning | (Frame {self.current_frame}/{self.total_frames})"
        else:
            controls_text = "CONTROLS: SPACE=Next Frame | Q=Quit | R=Reset | (Click window first!)"
        self.fig.suptitle(controls_text, fontsize=11, y=0.96)
        
    def on_key_press(self, event):
        """Handle keyboard input and forward to callback"""
        if self.key_callback:
            self.key_callback(event)
            
    def draw_network(self):
        """Draw the current state of the network"""
        # Clear axes completely
        self.ax.clear()
        self.ax.cla()
        
        # Set title based on mode
        if self.current_mode == "learning":
            title = f"Learning Phase - Frame {self.current_frame}/{self.total_frames}"
        else:
            title = f"Network Flooding Simulation - Frame {self.current_frame}/{self.total_frames}"
            
        self.ax.set_title(title)
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
        for node_id, node in self.network.nodes.items():
            pos = self.network.node_positions[node_id]
            color = node.get_display_color()
            
            # Draw node circle
            circle = plt.Circle(pos, 0.15, color=color, zorder=3)
            self.ax.add_patch(circle)
            
            # Add borders for special states
            if (node.status_flags[node.STATUS_RECEIVING] and 
                (node.status_flags[node.STATUS_SOURCE] or node.status_flags[node.STATUS_TARGET])):
                border_circle = plt.Circle(pos, 0.15, fill=False, 
                                        edgecolor='orange', linewidth=3, zorder=4)
                self.ax.add_patch(border_circle)

            if (node.status_flags[node.STATUS_COLLISION] and 
                (node.status_flags[node.STATUS_SOURCE] or node.status_flags[node.STATUS_TARGET])):
                border_circle = plt.Circle(pos, 0.15, fill=False, 
                                        edgecolor='pink', linewidth=3, zorder=4)
                self.ax.add_patch(border_circle)
            
            # Add node label
            self.ax.text(pos[0], pos[1], str(node_id), 
                        ha='center', va='center', fontsize=10, 
                        fontweight='bold', zorder=5)
        
        # Draw active message transmissions - LAST, ON TOP
        self._draw_active_transmissions()
        
        # Set axis limits
        positions = list(self.network.node_positions.values())
        if positions:
            x_coords = [pos[0] for pos in positions]
            y_coords = [pos[1] for pos in positions]
            
            margin = 0.5
            self.ax.set_xlim(min(x_coords) - margin, max(x_coords) + margin)
            self.ax.set_ylim(min(y_coords) - margin, max(y_coords) + margin)

    def _draw_active_transmissions(self):
        """Draw lines for actual transmissions happening this frame"""
        transmission_count = 0
        
        # Define colors for different messages (cycle through if more messages than colors)
        message_colors = ['purple', 'brown', 'blue', 'cyan', 'green', 'magenta', 'red']
        
        # Draw lines based on ACTUAL transmissions in the queue
        if self.current_transmissions:
            for sender_id, receiver_id, message, sender_path, hop_limit in self.current_transmissions:
                sender_pos = self.network.node_positions[sender_id]
                receiver_pos = self.network.node_positions[receiver_id]
                
                # Get color for this message (cycle through colors)
                color = message_colors[message.id % len(message_colors)]
                
                # Calculate line positions (with small offset for multiple messages)
                dx = receiver_pos[0] - sender_pos[0]
                dy = receiver_pos[1] - sender_pos[1]
                length = math.sqrt(dx*dx + dy*dy)
                
                if length > 0:
                    # Small offset for multiple messages on same link
                    offset = (message.id % 3 - 1) * 0.02  # -0.02, 0, 0.02
                    
                    # Perpendicular offset
                    perp_x = -dy / length * offset
                    perp_y = dx / length * offset
                    
                    start_x = sender_pos[0] + perp_x
                    start_y = sender_pos[1] + perp_y
                    end_x = receiver_pos[0] + perp_x
                    end_y = receiver_pos[1] + perp_y
                    
                    # Draw transmission line with message-specific color and THICK line
                    self.ax.plot([start_x, end_x], [start_y, end_y], 
                            color=color, linewidth=2.5, alpha=0.9, zorder=2)
                    
                    # Add arrow to show direction
                    dx_norm = dx / length * 0.25  # Arrow size
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
            for sender_id, receiver_id, message, sender_path, hop_limit in self.current_transmissions:
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
    
    def draw_info_panel(self, messages, mode="learning"):
        """Draw clean information panel"""
        self.info_ax.clear()
        
        if mode == "learning":
            title = f"Learning Phase - Frame {self.current_frame}/{self.total_frames}"
        else:
            title = f"Messages & Statistics - Frame {self.current_frame}/{self.total_frames}"
            
        self.info_ax.set_title(title, fontsize=12, fontweight='bold')
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
        
        # Show messages based on current mode
        if mode == "learning":
            # Learning mode - show learning messages
            y_pos = add_header("LEARNING MESSAGES", y_pos)
            
            # Filter out completed learning messages from active list
            all_messages = [(msg_id, msg) for msg_id, msg in messages.items() 
                          if not msg.is_completed and (msg.is_active or msg.start_frame > self.current_frame)]
            sorted_messages = sorted(all_messages, key=lambda x: (x[1].start_frame, x[0]))
            recent_messages = sorted_messages[:7] if len(sorted_messages) > 7 else sorted_messages
            
            for msg_id, message in recent_messages:
                y_pos = add_text(f"Learning Msg {msg_id}: {message.source} -> {message.target} (Start: Frame {message.start_frame})", 
                            y_pos)
                
                if message.is_active:
                    current_min_hops = self._get_current_hop_limit(message)
                    y_pos = add_text(f"  Hop Limit: {current_min_hops}/{message.hop_limit}", y_pos, fontsize=9)
                
                y_pos -= 0.01
            
            if len(sorted_messages) > 7:
                y_pos = add_text(f"... and {len(sorted_messages) - 7} more learning messages", y_pos, fontsize=9, color='gray')
            elif len(all_messages) == 0:
                y_pos = add_text("All learning messages completed", y_pos, fontsize=9, color='green')
        
        else:
            # Normal simulation mode - show comparison messages
            y_pos = add_header("COMPARISON MESSAGES", y_pos)
            
            # Filter out completed comparison messages from active list
            all_messages = [(msg_id, msg) for msg_id, msg in messages.items() 
                          if not msg.is_completed and (msg.is_active or msg.start_frame > self.current_frame)]
            sorted_messages = sorted(all_messages, key=lambda x: (x[1].start_frame, x[0]))
            recent_messages = sorted_messages[:7] if len(sorted_messages) > 7 else sorted_messages
            
            for msg_id, message in recent_messages:
                y_pos = add_text(f"Message {msg_id}: {message.source} -> {message.target} (Start: Frame {message.start_frame})", 
                            y_pos)
                
                if message.is_active:
                    current_min_hops = self._get_current_hop_limit(message)
                    y_pos = add_text(f"  Hop Limit: {current_min_hops}/{message.hop_limit}", y_pos, fontsize=9)
                
                y_pos -= 0.01
            
            if len(sorted_messages) > 7:
                y_pos = add_text(f"... and {len(sorted_messages) - 7} more messages", y_pos, fontsize=9, color='gray')
            elif len(all_messages) == 0:
                y_pos = add_text("All comparison messages completed", y_pos, fontsize=9, color='green')
        
        y_pos -= 0.02
        
        # COMPLETED MESSAGES
        y_pos = add_header("COMPLETED MESSAGES", y_pos)
        
        completed_messages = [(msg_id, msg) for msg_id, msg in messages.items() if msg.is_completed]
        sorted_completed = sorted(completed_messages, key=lambda x: x[0])
        recent_completed = sorted_completed[-7:] if len(sorted_completed) > 7 else sorted_completed
        
        if recent_completed:
            for msg_id, message in recent_completed:
                status = message.get_status()
                
                if status == "SUCCESS":
                    y_pos = add_text(f"Message {msg_id}: {message.source} -> {message.target} - SUCCESS", 
                                y_pos, color='green', weight='bold')
                else:
                    y_pos = add_text(f"Message {msg_id}: {message.source} -> {message.target} - FAILED", 
                                y_pos, color='red', weight='bold')
                
                y_pos -= 0.01
            
            if len(sorted_completed) > 7:
                y_pos = add_text(f"... and {len(sorted_completed) - 7} more completed", y_pos, fontsize=9, color='gray')
        else:
            y_pos = add_text("None", y_pos)
    
    def _get_current_hop_limit(self, message):
        """Get current minimum hop limit for a message"""
        current_min_hops = "?"
        min_hops_found = []
        
        for node in self.network.nodes.values():
            for pending_item in node.pending_messages:
                if len(pending_item) >= 3:
                    pending_msg, path, local_hop_limit = pending_item
                    if pending_msg.id == message.id:
                        min_hops_found.append(local_hop_limit)
        
        if min_hops_found:
            current_min_hops = min(min_hops_found)
        else:
            current_min_hops = 0
        
        return current_min_hops
    
    def update_display(self, messages=None, mode="learning"):
        """Update the complete display"""
        self.draw_network()
        if messages:
            self.draw_info_panel(messages, mode)
        self._show_controls()  # Update controls text
        plt.draw()
        plt.pause(0.01)  # Small pause to allow display update
    
    def close_display(self):
        """Close the display window"""
        if self.fig:
            plt.close(self.fig)
            self.fig = None