from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 12.0
pocket_diameter = 30.0
pocket_depth = 6.0
boss_diameter = 20.0
boss_height = 4.0
rib_width = 10.0
rib_length = 40.0
rib_height = 3.0
countersink_diameter = 10.0
countersink_angle = 82.0
countersink_depth = 3.0
hole_diameter = 5.0
hole_offset = 15.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, plate_thickness - pocket_depth/2) * Cylinder(pocket_diameter/2, pocket_depth)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)

solid_body = solid_body + Pos(0, 0, rib_height/2) * Box(rib_length, rib_width, rib_height)

hole_positions = [
    (-plate_length/2 + hole_offset, -plate_width/2 + hole_offset),
    (plate_length/2 - hole_offset, -plate_width/2 + hole_offset),
    (-plate_length/2 + hole_offset, plate_width/2 - hole_offset),
    (plate_length/2 - hole_offset, plate_width/2 - hole_offset)
]

for x, y in hole_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_pocket_boss_rib"
export_step(part, "output.step")