from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 10.0
slot_width = 30.0
slot_length = 60.0
rib_width = 5.0
rib_height = 5.0
hole_diameter = 6.0
hole_offset = 10.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
chamfer_size = 0.5

base = Pos(0, 0, plate_thickness/2) * Box(plate_length, plate_width, plate_thickness)
slot = Pos(0, 0, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)
base = base - slot

rib = Pos(0, 0, plate_thickness/2 + rib_height/2) * Box(rib_width, plate_width, rib_height)
base = base + rib

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset)
]

for x, y in hole_positions:
    base = base - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    base = base - Pos(x, y, counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)

top_face = base.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
base = chamfer(top_edges, chamfer_size)

part = base
part.name = "plate_with_slot_rib_holes"
export_step(part, "output.step")