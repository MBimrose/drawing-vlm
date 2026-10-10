from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 12.0
shaft_radius = 8.0
shaft_height = 18.0
hole_radius = 2.0
hole_count = 12
hole_circle_radius = knob_outer_radius - 4.0
fillet_radius = 3.0
chamfer_distance = 0.8
slot_width = 6.0
slot_height = 4.0
slot_depth = 2.0

base = Pos(0, 0, knob_height/2) * Cylinder(knob_outer_radius, knob_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
base = fillet(top_face.edges(), fillet_radius)

shaft = Pos(0, 0, knob_height + shaft_height/2) * Cylinder(shaft_radius, shaft_height)
result = base + shaft

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    result = result - Pos(px, py, knob_height/2) * Cylinder(hole_radius, knob_height)

slot = Pos(knob_outer_radius - slot_depth/2, 0, knob_height/2) * Box(slot_depth, slot_width, slot_height)
result = result - slot

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

part = result
part.name = "knob"
export_step(part, "output.step")