from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 8.0
slot_length = 60.0
slot_width = 8.0
boss_diameter = 12.0
boss_height = 6.0
boss_offset_from_edge = 5.0
hole_diameter = 3.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
rib_width = 6.0
rib_height = 4.0
pocket_width = 30.0
pocket_height = 20.0
pocket_depth = 4.0
fillet_radius = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

with BuildPart() as slot_p:
    with BuildSketch() as slot_s:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness + 2)
solid_body = solid_body - slot_p.part

boss_center_x = plate_length / 2 - boss_offset_from_edge - boss_diameter / 2
boss = Pos(boss_center_x, 0, plate_thickness + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole = Pos(x, y, plate_thickness / 2) * Cylinder(hole_diameter / 2, plate_thickness + 2)
        solid_body = solid_body - hole

rib = Pos(0, 0, -rib_height / 2) * Box(rib_width, plate_width - 10, rib_height)
solid_body = solid_body + rib

pocket = Pos(-plate_length / 4, 0, pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

part = solid_body
part.name = "plate_with_slot_boss_holes"
export_step(part, "output.step")