from build123d import *

plate_width = 60.0
plate_depth = 45.0
plate_thickness = 5.0
corner_fillet_radius = 4.0
top_chamfer = 0.8
slot_length = 30.0
slot_width = 10.0
slot_offset_y = 5.0
hole_diameter = 4.0
hole_spacing = 20.0
hole_offset_y = -10.0
rib_width = 8.0
rib_depth = 12.0
rib_height = 2.0
rib_offset_x = 15.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), top_chamfer)

slot_cut = Pos(0, slot_offset_y, 0) * Box(slot_length, slot_width, plate_thickness * 2)
solid_body = solid_body - slot_cut

for x, y in [(-hole_spacing/2, hole_offset_y), (hole_spacing/2, hole_offset_y)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness * 2)

rib1 = Pos(-rib_offset_x, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
rib2 = Pos(rib_offset_x, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_slot_holes_and_ribs"
export_step(part, "output.step")