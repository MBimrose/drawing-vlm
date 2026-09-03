from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_length = 60.0
slot_width = 8.0
boss_diameter = 12.0
boss_height = 6.0
boss_offset_from_edge = 4.0
fillet_radius = 2.0
hole_diameter = 3.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
rib_width = 6.0
rib_height = 4.0
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 4.0

result = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2)
slot_solid = Pos(0, 0, -plate_thickness) * slot_bp.part
result = result - slot_solid

boss_center_x = plate_length / 2 - boss_offset_from_edge - boss_diameter / 2
boss = Pos(boss_center_x, 0, plate_thickness / 2 + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
result = result + boss

top_face = result.faces().sort_by(Axis.Z)[-1]
result = fillet(top_face.edges(), fillet_radius)

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        result = result - Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)

rib = Pos(0, 0, -plate_thickness / 2 - rib_height / 2) * Box(rib_width, plate_width, rib_height)
result = result + rib

pocket_center_x = -plate_length / 2 + pocket_length / 2 + 10
pocket = Pos(pocket_center_x, 0, 0) * Box(pocket_length, pocket_width, pocket_depth)
result = result - pocket

part = result
part.name = "plate_with_features"
export_step(part, "output.step")