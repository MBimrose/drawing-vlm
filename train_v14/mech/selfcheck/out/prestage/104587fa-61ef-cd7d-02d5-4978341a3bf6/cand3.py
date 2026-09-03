from build123d import *
import math

outer_diameter = 80.0
plate_thickness = 5.0
boss_diameter = 20.0
boss_height = 2.0
slot_width = 10.0
slot_depth = 2.0
hole_diameter = 4.0
hole_depth = 2.0
hole_count = 12
hole_pitch_radius = 30.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_diameter / 2)
    extrude(amount=plate_thickness)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

solid_body = solid_body + Pos(0, 0, plate_thickness - boss_height / 2) * Cylinder(boss_diameter / 2, boss_height)

solid_body = solid_body - Pos(0, 0, plate_thickness - slot_depth / 2) * Box(slot_width, slot_depth, slot_depth)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pitch_radius * math.cos(angle)
    py = hole_pitch_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, plate_thickness - hole_depth / 2) * Cylinder(hole_diameter / 2, hole_depth)

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")