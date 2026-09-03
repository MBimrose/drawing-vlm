from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 8.0
fillet_radius = 2.0
chamfer_size = 0.5
pocket_width = 30.0
pocket_depth = 20.0
pocket_cut_depth = 5.0
slot_length = 40.0
slot_width = 6.0
slot_spacing = 40.0
hole_diameter = 7.0
hole_cbore_diameter = 12.0
hole_cbore_depth = 3.0
hole_offset_x = -20.0
hole_spacing = 40.0
rib_width = 10.0
rib_depth = 5.0
rib_height = 4.0
rib_offset_x = -30.0

solid_body = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_depth, plate_thickness)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

pocket = Pos(0, 0, plate_thickness) * Box(pocket_width, pocket_depth, pocket_cut_depth)
solid_body = solid_body - pocket

for y in [-slot_spacing/2, slot_spacing/2]:
    slot = Pos(0, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
    solid_body = solid_body - slot

for y in [-hole_spacing/2, hole_spacing/2]:
    cbore = Pos(hole_offset_x, y, plate_thickness - hole_cbore_depth/2) * Cylinder(hole_cbore_diameter/2, hole_cbore_depth)
    shaft = Pos(hole_offset_x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - cbore - shaft

rib = Pos(rib_offset_x, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pockets_slots_holes_rib"
export_step(part, "output.step")