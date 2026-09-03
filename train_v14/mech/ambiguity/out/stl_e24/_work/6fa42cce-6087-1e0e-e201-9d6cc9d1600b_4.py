from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
corner_fillet_radius = 4.0
edge_chamfer = 1.0
central_pocket_width = 30.0
central_pocket_height = 20.0
central_pocket_depth = 4.0
slot_width = 12.0
slot_height = 3.0
mount_hole_diameter = 6.0
mount_hole_spacing_x = 40.0
mount_hole_spacing_y = 20.0
rib_thickness = 2.0
rib_width = 10.0
rib_length = 60.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = chamfer(solid_body.edges(), edge_chamfer)

pocket = Pos(0, 0, plate_thickness/2 - central_pocket_depth/2) * Box(central_pocket_width, central_pocket_height, central_pocket_depth)
solid_body = solid_body - pocket

slot = Box(slot_width, slot_height, plate_thickness + 1)
solid_body = solid_body - slot

hole_positions = [
    (-mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
    ( mount_hole_spacing_x/2, -mount_hole_spacing_y/2),
    (-mount_hole_spacing_x/2,  mount_hole_spacing_y/2),
    ( mount_hole_spacing_x/2,  mount_hole_spacing_y/2),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness + 1)

rib = Pos(0, 0, -plate_thickness/2 + rib_thickness/2) * Box(rib_length, rib_width, rib_thickness)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_slot_holes_rib"
export_step(part, "output.step")