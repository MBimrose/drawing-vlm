from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 10.0
frame_thickness = 4.0
hole_diameter = 5.5
chamfer_size = 0.8
hole_positions = [
    (-30.0, -20.0),
    (0.0, -20.0),
    (30.0, -20.0),
    (-30.0, 20.0),
    (0.0, 20.0),
    (30.0, 20.0),
]

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame_outer = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
frame_inner = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_thickness, base_width - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner
solid_body = base + frame

hole_radius = hole_diameter / 2
hole_height = base_thickness + frame_height + 2
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, (base_thickness + frame_height)/2) * Cylinder(hole_radius, hole_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "base_with_frame_and_holes"
export_step(part, "output.step")