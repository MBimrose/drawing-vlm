from build123d import *
import math

outer_size = 80.0
wall_thickness = 5.0
height = 40.0
base_fillet = 2.0
hole_diameter = 3.0
hole_offset = 2.0

outer = Box(outer_size, outer_size, height)
inner = Box(outer_size - 2*wall_thickness, outer_size - 2*wall_thickness, height - 2*wall_thickness)
result = outer - inner

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = fillet(bottom_face.edges(), base_fillet)

hole_r = hole_diameter / 2
hole_h = wall_thickness + 1
hole_pos_r = outer_size/2 - wall_thickness/2 - hole_offset
for i in range(4):
    angle = math.radians(i * 90)
    px = hole_pos_r * math.cos(angle)
    py = hole_pos_r * math.sin(angle)
    result = result - Pos(px, py, height/2) * Cylinder(hole_r, hole_h)

part = result
part.name = "hollow_square_with_holes"
export_step(part, "output.step")