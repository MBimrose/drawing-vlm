from build123d import *

plate_length = 80.0
plate_width = 80.0
plate_thickness = 10.0
wall_thickness = 4.0
pocket_depth = 8.0
fillet_radius = 2.0
hole_diameter = 6.5
hole_offset = 10.0
boss_diameter = 15.0
boss_height = 4.0
slot_width = 12.0
slot_height = 30.0
slot_depth = 5.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket_w = plate_length - 2 * wall_thickness
pocket_h = plate_width - 2 * wall_thickness
pocket = Pos(0, 0, plate_thickness - pocket_depth/2) * Box(pocket_w, pocket_h, pocket_depth)
solid_body = solid_body - pocket

boss_positions = [
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
]
for x, y in boss_positions:
    boss = Pos(x, y, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
    solid_body = solid_body + boss

hole_positions = [
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (0, plate_width/4),
    (0, -plate_width/4),
]
for x, y in hole_positions:
    hole = Pos(x, y, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)
    solid_body = solid_body - hole

slot = Pos(plate_length/2 - slot_depth/2, 0, 0) * Box(slot_depth, slot_width, slot_height)
solid_body = solid_body - slot

part = solid_body
part.name = "plate_with_pocket_bosses_and_slot"
export_step(part, "output.step")