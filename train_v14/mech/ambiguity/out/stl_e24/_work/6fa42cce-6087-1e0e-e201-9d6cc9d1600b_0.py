from build123d import *

plate_length = 80.0
plate_width = 50.0
plate_thickness = 6.0
corner_fillet_radius = 4.0
edge_chamfer = 1.0
hole_diameter = 6.0
hole_offset = 20.0
slot_width = 3.0
slot_length = 12.0
slot_spacing = 15.0
boss_diameter = 12.0
boss_height = 4.0
pocket_depth = 2.0
pocket_width = 30.0
pocket_length = 20.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
solid_body = chamfer(solid_body.edges(), edge_chamfer)

for x, y in [(hole_offset, hole_offset), (-hole_offset, hole_offset), (-hole_offset, -hole_offset), (hole_offset, -hole_offset)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

for x, y in [(-slot_spacing, 0), (0, 0), (slot_spacing, 0)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(0, 0, -pocket_depth/2) * Box(pocket_length, pocket_width, pocket_depth)

part = solid_body
part.name = "plate_with_features"
export_step(part, "output.step")