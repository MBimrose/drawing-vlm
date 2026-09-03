from build123d import *

plate_width = 80.0
plate_height = 60.0
plate_thickness = 5.0
pocket_width = 40.0
pocket_height = 30.0
hole_diameter = 6.0
countersink_diameter = 10.0
countersink_angle = 82.0
hole_offset_x = 15.0
hole_offset_y = 10.0
fillet_radius = 0.8
chamfer_distance = 0.5
slot_width = 4.0
slot_length = 20.0
slot_offset_y = 25.0
boss_diameter = 12.0
boss_height = 3.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_height)
    extrude(amount=plate_thickness)
solid_body = p.part

solid_body = chamfer(solid_body.edges(), chamfer_distance)
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * Box(pocket_width, pocket_height, plate_thickness)

hole_positions = [
    (-plate_width/2 + hole_offset_x, -plate_height/2 + hole_offset_y),
    ( plate_width/2 - hole_offset_x, -plate_height/2 + hole_offset_y),
    (-plate_width/2 + hole_offset_x,  plate_height/2 - hole_offset_y),
    ( plate_width/2 - hole_offset_x,  plate_height/2 - hole_offset_y),
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

solid_body = solid_body - Pos(0, slot_offset_y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - Pos(0, -slot_offset_y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)

part = solid_body
part.name = "plate_with_pocket_holes_slots_boss"
export_step(part, "output.step")