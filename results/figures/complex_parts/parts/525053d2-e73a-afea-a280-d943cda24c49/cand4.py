from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 12.0
shaft_radius = 8.0
shaft_height = 18.0
fillet_radius = 2.0
chamfer_distance = 0.8
hole_diameter = 4.0
hole_count = 12
hole_circle_radius = knob_outer_radius - 4.0

base = Pos(0, 0, knob_height/2) * Cylinder(knob_outer_radius, knob_height)
shaft = Pos(0, 0, knob_height + shaft_height/2) * Cylinder(shaft_radius, shaft_height)
result = base + shaft

top_face = result.faces().sort_by(Axis.Z)[-1]
result = chamfer(top_face.edges(), chamfer_distance)

top_face = result.faces().sort_by(Axis.Z)[-2]
result = fillet(top_face.edges(), fillet_radius)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    result = result - Pos(px, py, knob_height/2) * Cylinder(hole_diameter/2, knob_height)

part = result
part.name = "knob"
export_step(part, "output.step")