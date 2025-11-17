from dataclasses import dataclass
import xml.etree.ElementTree as ET

@dataclass
class GazeboCameraConfig:
    name: str
    """The camera name as defined in the URDF."""
    topic: str
    """The base topic of the topics to which the camera publishes. Equals <topic> element in the URDF."""

    @property 
    def rgb_image_topic(self) -> str: return f"{self.topic}/rgb/image_raw"
    
    @property
    def depth_image_topic(self) -> str: return f"{self.topic}/depth/image_raw"
    
    @property
    def point_cloud_topic(self) -> str: return f"{self.topic}/point_cloud"
    
    @property
    def camera_info_topic(self) -> str: return f"{self.topic}/camera_info"

    @property 
    def gz_rgb_image_topic(self) -> str: return f"{self.topic}/image"
    
    @property
    def gz_depth_image_topic(self) -> str: return f"{self.topic}/depth_image"
    
    @property
    def gz_point_cloud_topic(self) -> str: return f"{self.topic}/points"
    
    @property
    def gz_camera_info_topic(self) -> str: return f"{self.topic}/camera_info"

  

def parse_robot_description_to_cameras(robot_description: str) -> list[GazeboCameraConfig]:    
    root = ET.fromstring(robot_description)
    cameras = []

    # Look for <gazebo> elements of type rgbd_camera
    for gazebo_elem in root.findall(".//gazebo"):
        for sensor in gazebo_elem.findall("sensor"):
            if sensor.attrib.get("type") != "rgbd_camera":
                continue

            name = sensor.attrib.get("name")
            if name is None:
                raise ValueError("Found <sensor> of type 'rgbd_camera' without a 'name' attribute.")
            
            topic_elem = sensor.find("topic")
            if topic_elem is None or not topic_elem.text:
                raise ValueError(f"RGBD camera sensor '{name}' is missing a <topic> element or it is empty.")

            cameras.append(GazeboCameraConfig(name, topic=topic_elem.text))

    return cameras

    