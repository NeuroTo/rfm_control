
class ImageNotAvailableException(Exception):
    def __init__(self, image_topic: str):
        super().__init__(f"Image '{image_topic}' is not available")


class JointStatesNotAvailableException(Exception):
    def __init__(self):
        super().__init__("Joint states are not available")
