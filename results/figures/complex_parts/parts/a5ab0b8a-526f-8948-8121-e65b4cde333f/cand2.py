from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 5.0
boss_size = 20.0
boss_height = 30.0
hole_diameter = 12.0
hole_offset = 15.0
rib_width = 10.0
rib_height = 10.0
chamfer_size = 0.8

base = Box(plate_length, plate_width, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

boss = Box(boss_size, boss_size, boss_height)

rib1 = Pos(0, plate_width/2 - rib_width/2, rib_height/2) * Box(plate_length, rib_width, rib_height)
rib2 = Pos(0, -plate_width/2 + rib_width/2, rib_height/2) * Box(plate_length, rib_width, rib_height)

result = base + boss + rib1 + rib2

hole_positions = [
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
]

for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(hole_diameter/2, 100)

part = result
part.name = "plate_with_boss_ribs_and_holes"
export_step(part, "output.step")