from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 8.0
frame_wall_thickness = 5.0
rib_height = 2.0
rib_width = 8.0
rib_length = base_length - 20.0
hole_diameter = 4.0
hole_offset = 12.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length - 2*frame_wall_thickness, base_width - 2*frame_wall_thickness, frame_height)
rib = Pos(0, 0, -rib_height/2) * Box(rib_length, rib_width, rib_height)

solid_body = base + frame - inner_cut + rib

hole_positions = [
    (hole_offset, hole_offset),
    (base_length - hole_offset, hole_offset),
    (hole_offset, base_width - hole_offset),
    (base_length - hole_offset, base_width - hole_offset)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "base_plate_with_frame"
export_step(part, "output.step")