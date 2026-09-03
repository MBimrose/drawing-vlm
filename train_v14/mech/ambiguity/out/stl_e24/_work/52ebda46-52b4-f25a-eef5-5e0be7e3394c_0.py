from build123d import *
import math

outer_diameter = 45.0
inner_diameter = 20.0
collar_length = 30.0
counterbore_diameter = 40.0
counterbore_depth = 5.0
set_screw_hole_diameter = 4.0
set_screw_offset = 10.0
chamfer_size = 0.8
outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
counterbore_radius = counterbore_diameter / 2.0
wall_thickness = outer_radius - inner_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, collar_length))
            l2 = Line(l1@1, (counterbore_radius, collar_length))
            l3 = Line(l2@1, (counterbore_radius, collar_length - counterbore_depth))
            l4 = Line(l3@1, (inner_radius, collar_length - counterbore_depth))
            l5 = Line(l4@1, (inner_radius, 0))
            l6 = Line(l5@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
hole_r = set_screw_hole_diameter / 2.0
hole_h = wall_thickness + 2.0
hole_z = collar_length / 2.0 - set_screw_offset

for i in range(4):
    angle = math.radians(i * 90)
    px = (outer_radius - wall_thickness / 2.0) * math.cos(angle)
    py = (outer_radius - wall_thickness / 2.0) * math.sin(angle)
    hole = Pos(px, py, hole_z) * Rot(0, 0, i * 90) * Rot(0, 90, 0) * Cylinder(hole_r, hole_h)
    solid_body = solid_body - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "collar_with_set_screw_holes"
export_step(part, "output.step")