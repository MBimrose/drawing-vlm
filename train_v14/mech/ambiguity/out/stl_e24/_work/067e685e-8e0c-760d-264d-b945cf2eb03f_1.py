from build123d import *

plate_length = 80.0
plate_width = 30.0
plate_thickness = 5.0
corner_fillet_radius = 2.5
chamfer_distance = 0.3
rib_height = 3.0
rib_width = 4.0
rib_spacing = 10.0
hole_diameter = 4.0
hole_offset_x = 15.0
hole_offset_y = 10.0

solid_body = Box(plate_length, plate_width, plate_thickness)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), corner_fillet_radius)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

rib1 = Pos(-rib_spacing/2, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
rib2 = Pos(rib_spacing/2, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_height, rib_height)
solid_body = solid_body + rib1 + rib2

hole_r = hole_diameter / 2
hole_h = plate_thickness + rib_height + 5
for x, y in [(-hole_offset_x, -hole_offset_y), (hole_offset_x, -hole_offset_y),
             (-hole_offset_x, hole_offset_y), (hole_offset_x, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_r, hole_h)

part = solid_body
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")