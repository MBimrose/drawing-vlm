from build123d import *
import math

knob_outer_radius = 30.0
knob_height = 12.0
shaft_radius = 8.0
shaft_height = 18.0
hole_diameter = 4.0
hole_count = 12
hole_circle_radius = knob_outer_radius - 4.0
fillet_radius = 3.0
chamfer_distance = 0.8
pocket_width = 12.0
pocket_depth = 6.0
pocket_height = 4.0
grip_pad_radius = 5.0
grip_pad_height = 2.0
grip_pad_offset = 15.0

result = Pos(0, 0, knob_height/2) * Cylinder(knob_outer_radius, knob_height)
top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = fillet(top_edges, fillet_radius)

shaft = Pos(0, 0, knob_height + shaft_height/2) * Cylinder(shaft_radius, shaft_height)
result = result + shaft

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_circle_radius * math.cos(angle)
    py = hole_circle_radius * math.sin(angle)
    hole = Pos(px, py, knob_height/2) * Cylinder(hole_diameter/2, knob_height)
    result = result - hole

pocket = Pos(0, 0, knob_height + shaft_height - pocket_height/2) * Box(pocket_width, pocket_depth, pocket_height)
result = result - pocket

grip_pad = Pos(grip_pad_offset, 0, knob_height + grip_pad_height/2) * Cylinder(grip_pad_radius, grip_pad_height)
result = result + grip_pad

top_edges = result.edges().sort_by(Axis.Z)[-1:]
result = chamfer(top_edges, chamfer_distance)

part = result
part.name = "knob"
export_step(part, "output.step")