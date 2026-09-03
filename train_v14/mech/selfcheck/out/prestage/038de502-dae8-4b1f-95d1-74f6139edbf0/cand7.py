from build123d import *
import math

plate_width = 80.0
plate_depth = 80.0
plate_thickness = 5.0
corner_fillet_radius = 4.0
edge_chamfer = 0.5
slot_width = 15.0
slot_length = 40.0
boss_diameter = 20.0
boss_height = 3.0
hole_diameter = 5.0
hole_pattern_radius = 30.0
hole_count = 8

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_width, plate_depth)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), corner_fillet_radius)
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), edge_chamfer)

slot = Pos(0, 0, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness)
solid_body = solid_body - slot

boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    hole = Pos(px, py, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness)
    solid_body = solid_body - hole

part = solid_body
part.name = "plate_with_boss_and_holes"
export_step(part, "output.step")