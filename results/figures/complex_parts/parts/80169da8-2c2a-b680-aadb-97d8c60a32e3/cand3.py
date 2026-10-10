from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
height = 40.0
flange_thickness = 3.0
flange_height = 45.0
hole_diameter = 3.0
hole_count = 6
hole_z = 20.0
chamfer_size = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

flange = Pos(0, outer_radius + flange_thickness / 2.0, 0) * Box(outer_diameter, flange_thickness, flange_height)
solid_body = solid_body + flange

for i in range(hole_count):
    angle = math.radians(i * 360.0 / hole_count)
    px = (outer_radius - wall_thickness / 2.0) * math.cos(angle)
    py = (outer_radius - wall_thickness / 2.0) * math.sin(angle)
    hole = Pos(px, py, hole_z) * Rot(0, 0, angle) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2.0, wall_thickness * 2.0)
    solid_body = solid_body - hole

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_flange"
export_step(part, "output.step")