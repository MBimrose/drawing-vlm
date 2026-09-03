from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
corner_fillet_radius = 4.0
edge_chamfer = 1.0
pocket_width = 30.0
pocket_height = 20.0
slot_width = 12.0
slot_height = 3.0
slot_offset_x = 20.0
hole_diameter = 5.0
hole_spacing_x = 40.0
hole_spacing_y = 20.0
rib_thickness = 2.0
rib_height = 30.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = chamfer(solid_body.edges(), edge_chamfer)

solid_body = solid_body - Box(pocket_width, pocket_height, plate_thickness)

for x in [-slot_offset_x, slot_offset_x]:
    solid_body = solid_body - Pos(x, 0, 0) * Box(slot_width, slot_height, plate_thickness)

for x in [-hole_spacing_x/2, hole_spacing_x/2]:
    for y in [-hole_spacing_y/2, hole_spacing_y/2]:
        solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib1 = Pos(-plate_length/2 + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
rib2 = Pos(plate_length/2 - rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, plate_thickness)
solid_body = solid_body + rib1 + rib2

part = solid_body
part.name = "plate_with_pockets_slots_holes_ribs"
export_step(part, "output.step")