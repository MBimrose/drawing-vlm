from build123d import *
import math

plate_length = 80.0
plate_width = 60.0
plate_thickness = 8.0
boss_diameter = 30.0
boss_height = 4.0
recess_diameter = 20.0
recess_depth = 2.0
hole_diameter = 5.5
hole_pattern_radius = 25.0
fillet_radius = 1.0
slot_width = 8.0
slot_length = 30.0

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(plate_length, plate_width)
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

boss = Pos(0, 0, boss_height/2) * Cylinder(boss_diameter/2, boss_height)
solid_body = solid_body + boss

recess = Pos(0, 0, boss_height - recess_depth/2) * Cylinder(recess_diameter/2, recess_depth)
solid_body = solid_body - recess

for i in range(6):
    angle = math.radians(i * 60)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    hole = Pos(px, py, plate_thickness/2) * Cylinder(hole_diameter/2, plate_thickness + 1)
    solid_body = solid_body - hole

slot1 = Pos(0, 0, plate_thickness/2) * Box(slot_width, slot_length, plate_thickness + 1)
slot2 = Pos(0, 0, plate_thickness/2) * Box(slot_length, slot_width, plate_thickness + 1)
solid_body = solid_body - slot1 - slot2

part = solid_body
part.name = "plate_with_boss_and_slots"
export_step(part, "output.step")