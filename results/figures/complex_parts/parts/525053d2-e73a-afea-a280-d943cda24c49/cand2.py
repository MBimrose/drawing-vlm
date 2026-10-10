from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 12.0
shaft_radius = 8.0
shaft_height = 18.0
keyway_width = 6.0
keyway_depth = 4.0
keyway_height = 10.0
rim_hole_radius = 2.0
rim_hole_count = 12
rim_hole_offset = 4.0
fillet_radius = 2.0
chamfer_distance = 0.5

base = Pos(0, 0, knob_height/2) * Cylinder(knob_outer_radius, knob_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = fillet(top_face.edges(), fillet_radius)

shaft = Pos(0, 0, knob_height + shaft_height/2) * Cylinder(shaft_radius, shaft_height)
result = base + shaft

keyway = Pos(shaft_radius - keyway_depth/2, 0, knob_height + shaft_height/2) * Box(keyway_depth, keyway_width, keyway_height)
result = result - keyway

for i in range(rim_hole_count):
    angle = math.radians(i * 360.0 / rim_hole_count)
    px = (knob_outer_radius - rim_hole_offset) * math.cos(angle)
    py = (knob_outer_radius - rim_hole_offset) * math.sin(angle)
    hole = Pos(px, py, knob_height/2) * Cylinder(rim_hole_radius, knob_height)
    result = result - hole

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "knob_with_shaft"
export_step(part, "output.step")