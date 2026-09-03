from build123d import *

plate_width = 90.0
plate_depth = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 12.0
slot_length = 30.0
slot_width = 10.0
hole_diameter = 5.0
hole_offset = 12.0
chamfer_size = 0.8
pocket_width = 20.0
pocket_depth = 15.0
pocket_height = 4.0

solid_body = Box(plate_width, plate_depth, plate_thickness)
solid_body = solid_body + Pos(0, 0, plate_thickness/2 + boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body - Pos(0, 0, plate_thickness/2 + boss_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
solid_body = solid_body - Pos(-plate_width/2 + plate_thickness/2, 0, 0) * Box(plate_thickness, slot_width, slot_length)
solid_body = solid_body - Pos(plate_width/2 - plate_thickness/2, 0, 0) * Box(plate_thickness, slot_width, slot_length)

hole_positions = [
    (-plate_width/2 + hole_offset, -plate_depth/2 + hole_offset),
    (plate_width/2 - hole_offset, -plate_depth/2 + hole_offset),
    (-plate_width/2 + hole_offset, plate_depth/2 - hole_offset),
    (plate_width/2 - hole_offset, plate_depth/2 - hole_offset),
    (0, 0)
]
for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(hole_diameter/2, plate_thickness + boss_height + 10)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_boss_slots_and_holes"
export_step(part, "output.step")