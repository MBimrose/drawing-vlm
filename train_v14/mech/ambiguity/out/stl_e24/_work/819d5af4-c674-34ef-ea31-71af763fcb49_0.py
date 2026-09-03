from build123d import *

plate_length = 100.0
plate_width = 80.0
plate_thickness = 5.0
lip_height = 2.0
lip_extension = 2.0
slot_length = 50.0
slot_width = 5.0
hole_diameter = 6.0
hole_offset = 12.0
chamfer_size = 0.5
fillet_radius = 0.3
boss_diameter = 15.0
boss_height = 8.0
rib_width = 5.0
rib_length = 20.0
rib_height = 3.0

base = Box(plate_length, plate_width, plate_thickness)
lip = Pos(0, 0, plate_thickness/2 + lip_height/2) * Box(plate_length + 2*lip_extension, plate_width + 2*lip_extension, lip_height)
result = base + lip

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + lip_height + 10)
slot_solid = Pos(0, 0, -(plate_thickness + lip_height)/2) * slot_bp.part
result = result - slot_solid

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    ( plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset,  plate_width/2 - hole_offset),
    ( plate_length/2 - hole_offset,  plate_width/2 - hole_offset),
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + lip_height + 10)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

boss = Pos(0, 0, plate_thickness/2 + lip_height + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
result = result + boss

rib_positions = [
    (-plate_length/2 + rib_length/2 + 5, -plate_width/2 + rib_width/2 + 5),
    ( plate_length/2 - rib_length/2 - 5, -plate_width/2 + rib_width/2 + 5),
    (-plate_length/2 + rib_length/2 + 5,  plate_width/2 - rib_width/2 - 5),
    ( plate_length/2 - rib_length/2 - 5,  plate_width/2 - rib_width/2 - 5),
]
for x, y in rib_positions:
    rib = Pos(x, y, -plate_thickness/2 - rib_height/2) * Box(rib_length, rib_width, rib_height)
    result = result + rib

part = result
part.name = "plate_with_lip_and_features"
export_step(part, "output.step")