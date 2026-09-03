from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 8.0
frame_height = 6.0
frame_thickness = 4.0
fillet_radius = 2.0
hole_diameter = 4.0
hole_spacing_x = 20.0
hole_spacing_y = 20.0
num_holes_x = 3
num_holes_y = 2

base = Pos(0, 0, base_thickness / 2) * Box(base_length, base_width, base_thickness)
base = fillet(base.edges().filter_by(Axis.Z), fillet_radius * 0.75)

frame_outer = Pos(0, 0, base_thickness + frame_height / 2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height / 2) * Box(base_length - 2 * frame_thickness, base_width - 2 * frame_thickness, frame_height)
frame = frame_outer - frame_inner
frame = fillet(frame.edges().filter_by(Axis.Z), fillet_radius)

combined = base + frame

hole_positions = []
for i in range(num_holes_x):
    for j in range(num_holes_y):
        x = (i - (num_holes_x - 1) / 2) * hole_spacing_x
        y = (j - (num_holes_y - 1) / 2) * hole_spacing_y
        hole_positions.append((x, y))

for x, y in hole_positions:
    combined = combined - Pos(x, y, base_thickness + frame_height / 2) * Cylinder(hole_diameter / 2, 20)

part = combined
part.name = "base_with_frame_and_holes"
export_step(part, "output.step")