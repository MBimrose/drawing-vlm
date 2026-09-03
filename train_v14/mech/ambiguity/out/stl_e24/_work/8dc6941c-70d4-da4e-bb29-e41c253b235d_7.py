from build123d import *

plate_width = 80.0
plate_depth = 60.0
plate_thickness = 5.0
edge_chamfer = 0.8
slot_length = 40.0
slot_width = 10.0
slot_radius = slot_width / 2.0
boss_diameter = 20.0
boss_height = 2.0
hole_diameter = 5.0
hole_spacing_x = 20.0
hole_spacing_y = 25.0
hole_rows = 2
hole_cols = 3

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), edge_chamfer)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 3)
slot_solid = Pos(0, 0, -plate_thickness) * slot_bp.part
solid_body = solid_body - slot_solid

boss_solid = Pos(0, 0, plate_thickness / 2 + boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss_solid

for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        hole_solid = Pos(x, y, 0) * Cylinder(hole_diameter / 2, plate_thickness * 2)
        solid_body = solid_body - hole_solid

part = solid_body
part.name = "plate_with_slot_boss_and_holes"
export_step(part, "output.step")