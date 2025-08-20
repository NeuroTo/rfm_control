import numpy as np
from scipy.spatial.transform import Rotation
from geometry_msgs.msg import Pose, Quaternion


def add_pose(pose1: Pose, pose2: Pose) -> Pose:
    pose1.position.x += pose2.position.x
    pose1.position.y += pose2.position.y
    pose1.position.z += pose2.position.z
    pose1.orientation.x += pose2.orientation.x
    pose1.orientation.y += pose2.orientation.y
    pose1.orientation.z += pose2.orientation.z
    pose1.orientation.w += pose2.orientation.w
    return pose1


def substract_pose(pose1: Pose, pose2: Pose) -> Pose:
    pose1.position.x -= pose2.position.x
    pose1.position.y -= pose2.position.y
    pose1.position.z -= pose2.position.z
    pose1.orientation.x -= pose2.orientation.x
    pose1.orientation.y -= pose2.orientation.y
    pose1.orientation.z -= pose2.orientation.z
    pose1.orientation.w -= pose2.orientation.w
    return pose1


def to_euler_from_quaterntion(quaternion: np.ndarray) -> np.ndarray:
    return Rotation.from_quat(quaternion).as_euler("xyz")


def orientation_to_list(orientation: Quaternion) -> np.ndarray:
    return np.array([orientation.x, orientation.y, orientation.z, orientation.w])
