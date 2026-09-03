from build123d import *
import math

plate_length = 80.0
plate_width = 80.0
plate_thickness = 8.0
boss_radius = 20.0
boss_height = 12.0
groove_radius = 8.0
groove_depth = 4.0
through_hole_diameter = 4.0
corner_hole_diameter = 6.0
corner_hole_offset = 10.0
slot_width = 10.0
slot_length = 30.0
chamfer_size = 1.0
fillet_radius = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part

slot_positions = [
    (-plate_length/2 + slot_width/2, -plate_width/2 + slot_length/2),
    (plate_length/2 - slot_width/2, -plate_width/2 + slot_length/2),
    (-plate_length/2 + slot_width/2, plate_width/2 - slot_length/2),
    (plate_length/2 - slot_width/2, plate_width/2 - slot_length/2),
]
for x, y in slot_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness)

corner_positions = [
    (-plate_length/2 + corner_hole_offset, -plate_width/2 + corner_hole_offset),
    (plate_length/2 - corner_hole_offset, -plate_width/2 + corner_hole_offset),
    (-plate_length/2 + corner_hole_offset, plate_width/2 - corner_hole_offset),
    (plate_length/2 - corner_hole_offset, plate_width/2 - corner_hole_offset),
]
for x, y in corner_positions:
    solid_body = solid_body - Pos(x, y, plate_thickness/2) * Cylinder(corner_hole_diameter/2, plate_thickness)

solid_body = solid_body + Pos(0, 0, plate_thickness) * Cylinder(boss_radius, boss_height)

solid_body = solid_body - Pos(0, 0, plate_thickness + boss_height - groove_depth/2) * Cylinder(groove_radius, groove_depth)

solid_body = solid_body - Pos(0, 0, (plate_thickness + boss_height)/2) * Cylinder(through_hole_diameter/2, plate_thickness + boss_height)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "plate_with_boss_and_slots"
export_step(part, "output.step")