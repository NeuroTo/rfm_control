import numpy as np
import time

from tng_control.config.model_client_config_base import Gr00tConfigBase
from tng_control.model_adapter.model_clients.gr00t.gr00t_model_client import Gr00tModelClient, Gr00tAction


class Gr00tDualClientMock(Gr00tModelClient):
    """Mock policy client implementation for dual-arm GR00T robot models."""

    def __init__(self, config: Gr00tConfigBase):
        """
        Initialize with configuration dictionary.

        Args:
            config: Configuration object for the policy client.
        """
        # Store the creation time
        self.start_time = time.time()
        self.started = False
        # Define 10 different constant positions
        self.positions = [
            [0, 0, 0, 0, 0],
            [-50, 0, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, -50, 0, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, -50, 0, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, -50, 0],
            [0, 0, 0, 0, 0],
            [0, 0, 0, 0, -50],
            [0, 0, 0, 0, 0],
            # [-25.56305356, -25.36886633, 15.26926564, 82.23740393, 15.43266476],  # Position 1
        ]
        self.duration = 7

    def get_action(self, observation: dict[str, np.ndarray], prompt: str) -> Gr00tAction:
        """Get action from GR00T model."""
        # Calculate elapsed time since creation
        if not self.started:
            self.start_time = time.time()
            self.started = True
        elapsed_time = time.time() - self.start_time

        # Determine which position to return based on 5-second intervals
        # Use modulo to cycle through positions repeatedly
        position_index = int(elapsed_time // self.duration) % len(self.positions)

        return {
            "action.right_arm_pos": self.positions[position_index],
            "action.left_arm_pos": self.positions[position_index],
            "action.gripper": 12.2,
            "action.single_arm_velocity":
            [100, 100, 100, 100, 100],
            "action.gripper_velocity": 50}

