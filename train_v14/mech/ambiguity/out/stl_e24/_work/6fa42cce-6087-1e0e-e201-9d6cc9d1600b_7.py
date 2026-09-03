from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
corner_fillet_radius = 4.0
edge_chamfer = 1.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0
slot_length = 70.0
slot_width = 3.0
hole_diameter = 6.0
hole_offset = 8.0
rib_height = 2.0
rib_width = 20.0
rib_length = 30.0

base = Box(plate_length, plate_width, plate_thickness)
base = fillet(base.edges().filter_by(Axis.Z), corner_fillet_radius)
base = chamfer(base.edges(), edge_chamfer)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
base = base - pocket

slot = Box(slot_length, slot_width, plate_thickness)
base = base - slot

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    base = base - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib = Pos(0, 0, -plate_thickness/2 + rib_height/2) * Box(rib_length, rib_width, rib_height)
base = base + rib

part = base
part.name = "plate_with_pocket_slot_holes_rib"
export_step(part, "output.step")