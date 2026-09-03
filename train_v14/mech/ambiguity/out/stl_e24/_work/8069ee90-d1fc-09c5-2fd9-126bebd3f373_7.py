from build123d import *
import math

plate_length = 80.0
plate_width = 80.0
plate_thickness = 5.0
octagon_radius = 12.0
slot_width = 8.0
slot_length = 30.0
slot_offset = 20.0
corner_hole_diameter = 6.0
corner_hole_offset = 10.0
boss_diameter = 20.0
boss_height = 3.0
fillet_radius = 2.0
chamfer_distance = 1.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

with BuildPart() as oct_p:
    with BuildSketch() as oct_s:
        RegularPolygon(octagon_radius, 8)
    extrude(amount=plate_thickness + 1)
solid_body = solid_body - oct_p.part

slot_points = [(slot_offset, 0), (-slot_offset, 0), (0, slot_offset), (0, -slot_offset)]
for x, y in slot_points:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness + 1)

corner_points = [
    (plate_length/2 - corner_hole_offset, plate_width/2 - corner_hole_offset),
    (-plate_length/2 + corner_hole_offset, plate_width/2 - corner_hole_offset),
    (-plate_length/2 + corner_hole_offset, -plate_width/2 + corner_hole_offset),
    (plate_length/2 - corner_hole_offset, -plate_width/2 + corner_hole_offset),
]
for x, y in corner_points:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(corner_hole_diameter/2, plate_thickness + 1)

solid_body = solid_body + Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_octagon_slots_holes_boss"
export_step(part, "output.step")