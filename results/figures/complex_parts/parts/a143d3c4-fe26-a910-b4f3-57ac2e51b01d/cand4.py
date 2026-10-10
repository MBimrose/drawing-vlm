from build123d import *
import math

base_radius = 15.0
top_radius = 40.0
height = 40.0
boss_radius = 10.0
boss_height = 8.0
hole_diameter = 5.0
hole_count = 6
hole_circle_radius = 30.0
tab_width = 12.0
tab_height = 6.0
slot_width = 4.0
slot_length = 20.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(height)) as s2:
        Circle(top_radius)
    loft()

solid_body = p.part
solid_body = solid_body + Pos(0, 0, height + boss_height/2) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + Pos(top_radius - tab_width/2, 0, height + boss_height/2) * Box(tab_width, tab_height, boss_height)
solid_body = solid_body - Pos(0, 0, height + boss_height/2) * Box(slot_width, slot_length, boss_height)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, height + boss_height/2) * Cylinder(hole_diameter/2, height + boss_height + 10)

part = solid_body
part.name = "lofted_cone_with_boss_tab_slot_holes"
export_step(part, "output.step")