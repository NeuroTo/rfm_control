import numpy as np
from scipy.spatial.transform import Rotation
from geometry_msgs.msg import Point, Quaternion, Pose


def construct_geometry_msg_point(coords: np.ndarray) -> Point:
    point = Point()
    point.x, point.y, point.z = float(coords[0]), float(coords[1]), float(coords[2])
    return point


def construct_geometry_msg_quaternion(coords: np.ndarray) -> Quaternion:
    quaternion = Quaternion()
    quaternion.x, quaternion.y, quaternion.z, quaternion.w = float(
        coords[0]), float(
        coords[1]), float(
        coords[2]), float(
        coords[3])
    return quaternion


def to_quaternion_from_euler(rpy_angles: np.ndarray) -> Quaternion:
    quaternion: np.ndarray = Rotation.from_euler('xyz', rpy_angles).as_quat()
    return construct_geometry_msg_quaternion(quaternion)


def action_to_pose(position: np.ndarray, orientation: np.ndarray) -> Pose:
    return Pose(
        position=construct_geometry_msg_point(position),
        orientation=to_quaternion_from_euler(orientation)
    )
