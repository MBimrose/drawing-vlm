from build123d import *

base_length = 80.0
base_width = 60.0
base_thickness = 5.0
frame_height = 8.0
frame_wall_thickness = 5.0
inner_length = base_length - 2 * frame_wall_thickness
inner_width = base_width - 2 * frame_wall_thickness
rib_length = 60.0
rib_width = 10.0
rib_height = 2.0
hole_diameter = 4.0
hole_offset = 12.0
chamfer_size = 0.5

base = Pos(0, 0, base_thickness/2) * Box(base_length, base_width, base_thickness)
frame = Pos(0, 0, base_thickness + frame_height/2) * Box(base_length, base_width, frame_height)
inner_cut = Pos(0, 0, base_thickness + frame_height/2) * Box(inner_length, inner_width, frame_height)
rib = Pos(0, 0, -rib_height/2) * Box(rib_length, rib_width, rib_height)

solid_body = base + frame - inner_cut + rib

hole_r = hole_diameter / 2
hole_h = base_thickness + frame_height + rib_height + 10
hole_z = base_thickness + frame_height/2
for x, y in [(hole_offset, hole_offset), (base_length - hole_offset, hole_offset),
             (hole_offset, base_width - hole_offset), (base_length - hole_offset, base_width - hole_offset)]:
    solid_body = solid_body - Pos(x, y, hole_z) * Cylinder(hole_r, hole_h)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "base_plate_with_frame"
export_step(part, "output.step")