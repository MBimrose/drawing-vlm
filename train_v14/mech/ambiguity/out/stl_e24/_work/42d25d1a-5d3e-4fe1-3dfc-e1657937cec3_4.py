from build123d import *

block_length = 80.0
block_width = 50.0
block_height = 20.0
boss_diameter = 20.0
boss_height = 12.0
slot_width = 8.0
slot_depth = 12.0
slot_spacing = 15.0
num_slots = 3
hole_diameter = 4.0
hole_depth = 8.0
hole_spacing = 20.0
chamfer_size = 1.2
fillet_radius = 0.8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(block_length, block_width)
    extrude(amount=block_height)
    with BuildSketch() as s2:
        Circle(boss_diameter / 2)
    extrude(amount=boss_height)

solid_body = p.part

slot_start = -((num_slots - 1) * slot_spacing) / 2
for i in range(num_slots):
    x = slot_start + i * slot_spacing
    slot = Pos(x, 0, block_height - slot_depth / 2) * Box(slot_width, block_width, slot_depth)
    solid_body = solid_body - slot

hole_start = -hole_spacing / 2
for i in range(2):
    for j in range(2):
        x = hole_start + i * hole_spacing
        y = hole_start + j * hole_spacing
        hole = Pos(x, y, block_height - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)
        solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = fillet(vertical_edges, fillet_radius)

part = solid_body
part.name = "block_with_boss_slots_holes"
export_step(part, "output.step")