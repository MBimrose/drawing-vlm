from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
boss_diameter = 20.0
hole_diameter = 6.0
hole_depth = 4.0
hole_spacing = 10.0
hole_count = 7
slot_width = 8.0
slot_length = plate_length * 0.8
slot_offset_y = -plate_width / 2 + slot_width / 2 + 12.0
chamfer_size = 0.8
fillet_radius = 1.0

base_plate = Box(plate_length, plate_width, plate_thickness)
boss = Pos(-plate_length / 2 + boss_diameter / 2, 0, 0) * Cylinder(boss_diameter / 2, plate_thickness)
solid_body = base_plate + boss

top_y_face = solid_body.faces().sort_by(Axis.Y)[-1]
solid_body = chamfer(top_y_face.edges(), chamfer_size)

for i in range(hole_count):
    x = (i - (hole_count - 1) / 2) * hole_spacing
    solid_body = solid_body - Pos(x, 0, plate_thickness / 2 - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

with BuildPart() as slot_bp:
    with BuildSketch() as slot_sk:
        SlotOverall(slot_length, slot_width)
    extrude(amount=plate_thickness * 2)
slot_solid = slot_bp.part
solid_body = solid_body - Pos(0, slot_offset_y, -plate_thickness) * slot_solid

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_boss_holes_and_slot"
export_step(part, "output.step")