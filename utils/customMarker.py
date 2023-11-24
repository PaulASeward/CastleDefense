import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.patches import PathPatch
from matplotlib.path import Path
from matplotlib.transforms import Affine2D
from svgpath2mpl import parse_path
class CustomMarker:
    def __init__(self, text='D', color='black'):
        self.text = text
        self.color = color
        self._set_custom_marker(self.text, self.color)

    def _set_custom_marker(self, text, color):
        # Define the path for the custom marker
        # path_data = [
        #     (Path.MOVETO, (0.0, 0.5)),
        #     (Path.CURVE4, (0.0, 0.25)),
        #     (Path.CURVE4, (0.25, 0.0)),
        #     (Path.CURVE4, (0.75, 0.0)),
        #     (Path.CURVE4, (1.0, 0.25)),
        #     (Path.CURVE4, (1.0, 0.5)),
        #     (Path.CURVE4, (1.0, 0.75)),
        #     (Path.CURVE4, (0.75, 1.0)),
        #     (Path.CURVE4, (0.25, 1.0)),
        #     (Path.CURVE4, (0.0, 0.75)),
        #     (Path.CLOSEPOLY, (0.0, 0.5)),
        # ]
        # # Create the custom marker path
        # verts = [point[1] for point in path_data]
        # codes = [point[0] for point in path_data]

        # Hardcoded separation
        verts = [
            (0, 2),
            (0, 1),
            (1, 0),
            (3, 0),
            (4, 1),
            (4, 2),
            (4, 3),
            (3, 4),
            (4, 1),
            (0, 3),
            (0, 2),
        ]

        codes = [
            Path.MOVETO,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CURVE4,
            Path.CLOSEPOLY,
        ]


        path = Path(vertices=verts, codes=codes)

        # Set the custom marker path and color
        self.marker_path = path
        self.marker_transform = Affine2D().scale(20)  # Adjust the scale factor for better visibility
        self.facecolor = color
        self.edgecolor = color

        return path


# verts = [
#     (0, 2),
#     (0, 1),
#     (1, 0),
#     (3, 0),
#     (4, 1),
#     (4, 2),
#     (4, 3),
#     (3, 4),
#     (4, 1),
#     (0, 3),
#     (0, 2),
# ]
#
# codes = [
#     Path.MOVETO,
#     Path.CURVE4,
#     Path.CURVE4,
#     Path.CURVE4,
#     Path.CURVE4,
#     Path.CURVE4,
#     Path.CURVE4,
#     Path.CURVE4,
#     Path.CURVE4,
#     Path.CURVE4,
#     Path.CLOSEPOLY,
# ]
#
#
# path = Path(vertices=verts, codes=codes)
# # Example usage:
# fig, ax = plt.subplots()
# plt.plot(0.3, 0.6, marker=path, color='red', markersize=200)

planet_marker = parse_path("""M 61.03,41.69
           C 61.03,46.32 57.28,50.07 52.67,50.07
             48.06,50.07 44.31,46.32 44.31,41.69
             44.31,37.07 48.06,33.32 52.67,33.32
             52.67,33.32 57.28,33.32 61.03,41.69 Z
           M 83.17,25.94
           C 83.77,28.28 83.69,30.89 83.51,33.54
             92.28,39.16 93.78,42.55 93.72,43.10
             93.71,43.12 92.04,45.11 82.44,44.41
             81.20,44.32 79.91,44.18 78.56,44.01
             79.65,40.70 80.25,37.17 80.25,33.50
             80.25,15.03 65.26,0.00 46.83,0.00
             32.71,0.00 20.61,8.83 15.72,21.26
             7.66,15.96 6.23,12.76 6.29,12.22
             6.31,12.20 7.71,10.07 17.30,10.77
             18.59,8.40 20.64,6.48 22.77,4.97
             21.42,4.81 19.46,4.73 18.04,4.62
             7.71,3.87 1.94,5.66 0.37,10.10
             -1.30,14.84 2.66,20.26 12.46,26.66
             12.93,26.97 13.44,27.28 13.94,27.59
             13.59,29.51 13.40,31.48 13.40,33.50
             13.40,51.97 28.40,67.00 46.83,67.00
             59.27,67.00 70.14,60.14 75.90,50.01
             78.03,50.32 80.07,50.55 81.98,50.69
             92.30,51.45 98.08,49.66 99.64,45.22
             101.81,39.06 93.85,32.07 83.17,25.94 Z
           M 46.83,60.52
           C 31.96,60.52 19.87,48.40 19.87,33.50
             19.87,32.69 19.92,31.89 19.99,31.10
             26.02,34.35 33.03,37.53 40.58,40.39
             40.78,38.20 41.55,36.18 42.74,34.47
             34.80,31.46 27.47,28.09 21.36,24.66
             25.02,14.09 35.05,6.48 46.83,6.48
             61.69,6.48 73.78,18.60 73.78,33.50
             73.78,36.83 73.18,40.02 72.07,42.97
             69.86,42.55 67.56,42.05 65.20,41.48
             65.20,41.50 65.20,41.51 65.20,41.54
             65.20,43.73 64.62,45.79 63.61,47.58
             65.46,48.03 67.27,48.43 69.03,48.79
             64.17,55.87 56.03,60.52 46.83,60.52 Z""")

planet_marker.vertices -= planet_marker.vertices.mean(axis=0)
# planet_marker = planet_marker.transformed(mpl.transforms.Affine2D().rotate_deg(180))
# planet_marker = planet_marker.transformed(mpl.transforms.Affine2D().scale(-1,1))

plt.plot(0,0,marker=planet_marker,color='red',  markersize=200)

plt.show()  # Explicitly show the plot

