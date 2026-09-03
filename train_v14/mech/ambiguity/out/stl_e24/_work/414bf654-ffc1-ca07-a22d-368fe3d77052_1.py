from build123d import *
import math

outer_radius = 20.0
wall_thickness = 2.0
inner_radius = outer_radius - wall_thickness
tube_length = 70.0
groove_width = 5.0
groove_depth = 2.0
groove_position = 30.0
central_hole_diameter = 10.0
chamfer_size = 0.5
mount_hole_diameter = 4.0
mount_hole_count = 4

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, tube_length))
            l3 = Line(l2@1, (inner_radius, tube_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove_cut = Pos(0, 0, groove_position - groove_width / 2) * Cylinder(outer_radius - groove_depth, groove_width)
solid_body = solid_body - groove_cut

solid_body = solid_body - Rot(90, 0, 0) * Cylinder(central_hole_diameter / 2, tube_length)

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

for i in range(mount_hole_count):
    angle = i * 360.0 / mount_hole_count
    rad = math.radians(angle)
    x = (outer_radius - wall_thickness / 2) * math.cos(rad)
    y = (outer_radius - wall_thickness / 2) * math.sin(rad)
    hole = Pos(x, y, 0) * Rot(0, 0, angle) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2, wall_thickness * 2)
    solid_body = solid_body - hole

part = solid_body
part.name = "tube_with_groove_and_holes"
export_step(part, "output.step")