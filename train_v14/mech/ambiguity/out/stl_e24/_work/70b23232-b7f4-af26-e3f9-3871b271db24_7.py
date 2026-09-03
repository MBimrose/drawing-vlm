from build123d import *
import math

outer_radius = 30.0
wall_thickness = 3.0
inner_radius = outer_radius - wall_thickness
channel_length = 80.0
groove_width = 12.0
groove_depth = 2.0
groove_position = 40.0
hole_diameter = 4.0
hole_count = 6
hole_z = channel_length / 2.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=channel_length)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face])

groove_box = Pos(0, 0, groove_position + groove_depth / 2) * Box(groove_width, groove_depth, groove_depth)
solid_body = solid_body - groove_box

for i in range(hole_count):
    angle_deg = i * 360.0 / hole_count
    angle_rad = math.radians(angle_deg)
    px = (outer_radius - wall_thickness / 2) * math.cos(angle_rad)
    py = (outer_radius - wall_thickness / 2) * math.sin(angle_rad)
    hole = Pos(px, py, hole_z) * Rot(0, 0, angle_deg) * Rot(0, 90, 0) * Cylinder(hole_diameter / 2, wall_thickness + 1)
    solid_body = solid_body - hole

top_edges = solid_body.edges().sort_by(Axis.Z)[-1:]
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_holes"
export_step(part, "output.step")