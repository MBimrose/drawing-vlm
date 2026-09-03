from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 3.0
slot_length = 25.0
slot_width = 6.0
slot_spacing = 25.0
hole_diameter = 5.0
hole_edge_margin = 8.0
rib_height = 2.0
rib_thickness = 4.0
rib_spacing = 15.0

result = Box(plate_length, plate_width, plate_thickness)

pocket = Pos(0, 0, plate_thickness/2 - pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

slot1 = Pos(0, slot_spacing/2, 0) * Box(slot_length, slot_width, plate_thickness)
slot2 = Pos(0, -slot_spacing/2, 0) * Box(slot_length, slot_width, plate_thickness)
result = result - slot1 - slot2

hole_positions = [
    (-plate_length/2 + hole_edge_margin, -plate_width/2 + hole_edge_margin),
    ( plate_length/2 - hole_edge_margin, -plate_width/2 + hole_edge_margin),
    (-plate_length/2 + hole_edge_margin,  plate_width/2 - hole_edge_margin),
    ( plate_length/2 - hole_edge_margin,  plate_width/2 - hole_edge_margin),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness)

rib_count = int((plate_length - 2*hole_edge_margin) // rib_spacing) + 1
rib_positions = [-plate_length/2 + hole_edge_margin + i*rib_spacing for i in range(rib_count)]
for x in rib_positions:
    rib = Pos(x, 0, -plate_thickness/2 + rib_height/2) * Box(rib_thickness, plate_width - 2*hole_edge_margin, rib_height)
    result = result + rib

part = result
part.name = "plate_with_pocket_slots_holes_ribs"
export_step(part, "output.step")