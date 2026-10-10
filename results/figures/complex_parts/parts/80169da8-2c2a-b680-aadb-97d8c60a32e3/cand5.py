from build123d import *
import math

outer_diameter = 80.0
wall_thickness = 2.0
height = 40.0
rib_width = 10.0
rib_height = 5.0
rib_length = outer_diameter - 2 * wall_thickness
mount_hole_diameter = 3.0
mount_hole_count = 4
mount_hole_radius = (outer_diameter / 2) - wall_thickness - 5.0
chamfer_distance = 0.5

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

with BuildPart() as p:
    with BuildSketch() as s:
        Circle(outer_radius)
    extrude(amount=height)

solid_body = p.part
top_face = solid_body.faces().sort_by(Axis.Z)[-1]
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = offset(solid_body, amount=-wall_thickness, openings=[top_face, bottom_face])

rib = Pos(0, inner_radius - rib_width / 2.0, 0) * Box(rib_length, rib_width, rib_height)
solid_body = solid_body + rib

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    hole = Pos(px, py, height / 2) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2, outer_diameter)
    solid_body = solid_body - hole

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "hollow_cylinder_with_rib"
export_step(part, "output.step")