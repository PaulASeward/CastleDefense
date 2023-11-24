import numpy as np
import matplotlib.markers as mmarkers
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.transforms import Affine2D


class CustomMarker(mmarkers.MarkerStyle):
    def __init__(self, text='X', color='black', markername='customD', **kwargs):
        super().__init__(marker=markername, **kwargs)
        self.text = text
        self.color = color

    def _set_custom_marker(self, text, color):
        # Define the path for the custom marker
        path_data = [
            (Path.MOVETO, (0.0, 0.5)),
            (Path.CURVE4, (0.0, 0.25)),
            (Path.CURVE4, (0.25, 0.0)),
            (Path.CURVE4, (0.75, 0.0)),
            (Path.CURVE4, (1.0, 0.25)),
            (Path.CURVE4, (1.0, 0.5)),
            (Path.CURVE4, (1.0, 0.75)),
            (Path.CURVE4, (0.75, 1.0)),
            (Path.CURVE4, (0.25, 1.0)),
            (Path.CURVE4, (0.0, 0.75)),
            (Path.CLOSEPOLY, (0.0, 0.5)),
        ]

        # Create the custom marker path
        path = Path(*zip(*path_data))

        # Set the custom marker path and color
        self.set_marker(path, color=color, transform=Affine2D().scale(10))

    def set_text(self, text):
        self.text = text
        self._set_custom_marker(self.text, self.color)

    def set_color(self, color):
        self.color = color
        self._set_custom_marker(self.text, self.color)


# Example usage:
# fig, ax = plt.subplots()
# custom_marker = CustomMarker(text='D', color='red')
# ax.scatter([1, 2, 3, 4], [1, 2, 3, 4], marker=custom_marker, s=100)
# plt.show()
