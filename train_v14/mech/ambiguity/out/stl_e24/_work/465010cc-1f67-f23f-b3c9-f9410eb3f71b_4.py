from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
corner_fillet_radius = 5.0
slot_length = 40.0
slot_width = 8.0
slot_spacing = 30.0
slot_chamfer = 1.0
central_hole_diameter = 8.0
boss_diameter = 20.0
boss_height = 6.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

top_edges = solid_body.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
solid_body = fillet(top_edges, corner_fillet_radius)

slot_y_offset = slot_spacing / 2.0
for y in [-slot_y_offset, slot_y_offset]:
    slot = Pos(0, y, plate_thickness / 2) * Box(slot_length, slot_width, plate_thickness)
    solid_body = solid_body - slot

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, slot_chamfer)

hole = Pos(0, 0, plate_thickness / 2) * Cylinder(central_hole_diameter / 2, plate_thickness)
solid_body = solid_body - hole

boss = Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)
solid_body = solid_body + boss

part = solid_body
part.name = "plate_with_slots_and_boss"
export_step(part, "output.step")