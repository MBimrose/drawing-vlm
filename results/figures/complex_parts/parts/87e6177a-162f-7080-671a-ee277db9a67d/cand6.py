from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 5.0
height = 60.0
groove_width = 8.0
groove_depth = 2.0
hole_diameter = 4.0
hole_count = 6
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness
groove_radius = inner_radius - groove_depth

solid_body = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)

groove = Pos(0, 0, height/2 - groove_width/2) * Cylinder(groove_radius, groove_width)
solid_body = solid_body - groove

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = (outer_radius - wall_thickness/2) * math.cos(angle)
    py = (outer_radius - wall_thickness/2) * math.sin(angle)
    hole = Pos(px, py, -height/2 + wall_thickness) * Cylinder(hole_diameter/2, wall_thickness*2)
    solid_body = solid_body - hole

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_holes"
export_step(part, "output.step")