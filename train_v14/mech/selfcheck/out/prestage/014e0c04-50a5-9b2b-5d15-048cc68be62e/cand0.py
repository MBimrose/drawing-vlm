from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 6.0
rib_width = 6.0
rib_height = 3.0
rib_length = plate_length - 10.0
hole_diameter = 5.0
hole_spacing = 50.0
pocket_diameter = 12.0
pocket_depth = 4.0
slot_width = 15.0
slot_length = 6.0
chamfer_size = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, rib_length, rib_height)
solid_body = solid_body + rib

for x in [-hole_spacing/2, hole_spacing/2]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(hole_diameter/2, plate_thickness + rib_height + 10)

solid_body = solid_body - Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

slot_cut = Pos(0, plate_width/2 - plate_thickness/2, 0) * Box(slot_width, plate_thickness, slot_length)
solid_body = solid_body - slot_cut

part = solid_body
part.name = "plate_with_rib_holes_pocket_slot"
export_step(part, "output.step")