from build123d import *
import math

outer_size = 80.0
wall_thickness = 5.0
height = 40.0
slot_width = 10.0
slot_height = 20.0
slot_offset = 30.0
chamfer_dist = 1.0
hole_diameter = 3.0
hole_depth = 3.0
hole_pattern_radius = 32.0
hole_count = 4

inner_size = outer_size - 2 * wall_thickness

outer_box = Box(outer_size, outer_size, height)
inner_box = Box(inner_size, inner_size, height - 2 * wall_thickness)
result = outer_box - inner_box

slot_box = Pos(-outer_size/2 + wall_thickness/2, slot_offset, 0) * Box(wall_thickness, slot_width, slot_height)
result = result - slot_box

vertical_edges = result.edges().filter_by(Axis.Z)
slot_edges = [e for e in vertical_edges if abs(e.center().X + outer_size/2 - wall_thickness/2) < 1.0]
result = chamfer(slot_edges, chamfer_dist)

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = hole_pattern_radius * math.cos(angle)
    py = hole_pattern_radius * math.sin(angle)
    hole = Pos(px, py, height/2 - hole_depth/2) * Cylinder(hole_diameter/2, hole_depth)
    result = result - hole

part = result
part.name = "hollow_box_with_slot_and_holes"
export_step(part, "output.step")