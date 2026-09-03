from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 8.0
frame_wall_thickness = 5.0
rib_width = 10.0
rib_height = 2.0
hole_diameter = 4.0
hole_offset = 12.0
chamfer_size = 0.5

inner_length = base_length - 2 * frame_wall_thickness
inner_width = base_width - 2 * frame_wall_thickness

base = Pos(0, 0, base_thickness / 2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height / 2) * Box(base_length, base_width, frame_height)
result = base + frame

cutout = Pos(0, 0, base_thickness + frame_height / 2) * Box(inner_length, inner_width, frame_height)
result = result - cutout

rib = Pos(0, 0, -rib_height / 2) * Box(base_length - 2 * frame_wall_thickness, rib_width, rib_height)
result = result + rib

hole1 = Pos(hole_offset, hole_offset, (base_thickness + frame_height) / 2) * Cylinder(hole_diameter / 2, base_thickness + frame_height + 10)
hole2 = Pos(base_length - hole_offset, base_width - hole_offset, (base_thickness + frame_height) / 2) * Cylinder(hole_diameter / 2, base_thickness + frame_height + 10)
result = result - hole1 - hole2

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "base_plate_with_frame"
export_step(part, "output.step")