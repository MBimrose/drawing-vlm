from build123d import *

base_width = 80.0
base_length = 80.0
base_thickness = 5.0
frame_height = 6.0
frame_thickness = 4.0
hole_diameter = 5.0
hole_depth = 3.0
hole_spacing = 18.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_width, base_length, base_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_width, base_length, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(base_width - 2*frame_thickness, base_length - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner

result = base + frame

for i in range(3):
    for j in range(3):
        x = (i - 1) * hole_spacing
        y = (j - 1) * hole_spacing
        result = result - Pos(x, y, base_thickness - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")