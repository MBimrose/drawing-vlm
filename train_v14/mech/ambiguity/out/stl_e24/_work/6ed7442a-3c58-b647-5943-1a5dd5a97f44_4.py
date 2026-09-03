from build123d import *
import math

outer_diameter = 80.0
plate_thickness = 5.0
boss_diameter = 15.0
boss_height = 2.0
slot_width = 5.0
slot_length = 30.0
slot_count = 6
slot_angle = 360.0 / slot_count
chamfer_size = 0.5
central_hole_diameter = 8.0
pocket_depth = 0.5
pocket_margin = 2.0

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=plate_thickness)

solid_body = p.part

for i in range(slot_count):
    angle = i * slot_angle
    slot = Rot(0, 0, angle) * Pos(outer_diameter / 2 - slot_length / 2, 0, plate_thickness / 2) * Box(slot_length, slot_width, plate_thickness)
    solid_body = solid_body - slot

solid_body = solid_body - Pos(0, 0, plate_thickness / 2) * Cylinder(central_hole_diameter / 2, plate_thickness)

pocket_radius = outer_diameter / 2 - pocket_margin
solid_body = solid_body - Pos(0, 0, plate_thickness - pocket_depth / 2) * Cylinder(pocket_radius, pocket_depth)

solid_body = solid_body + Pos(0, 0, boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "plate_with_slots_and_boss"
export_step(part, "output.step")