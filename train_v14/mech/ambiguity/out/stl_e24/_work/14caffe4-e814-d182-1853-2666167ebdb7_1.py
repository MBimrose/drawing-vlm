from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
fillet_radius = 2.0
chamfer_distance = 0.5
pocket_length = 30.0
pocket_width = 20.0
pocket_depth = 5.0
slot_length = 40.0
slot_width = 6.0
slot_offset = 10.0
hole_diameter = 7.0
hole_spacing = 40.0
boss_diameter = 15.0
boss_height = 4.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = fillet(top_face.edges(), fillet_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness) * Box(pocket_length, pocket_width, pocket_depth)

solid_body = solid_body - Pos(0, slot_offset, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - Pos(0, -slot_offset, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)

for x, y in [(-hole_spacing/2, plate_width/2 - 10), (hole_spacing/2, plate_width/2 - 10)]:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_pocket_slots_holes_boss"
export_step(part, "output.step")