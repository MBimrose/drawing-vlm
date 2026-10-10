from build123d import *
import math

outer_radius = 20.0
inner_radius = 15.0
body_length = 60.0
flange_thickness = 10.0
flange_radius = 30.0
chamfer_size = 2.0
mount_hole_diameter = 4.0
mount_hole_count = 4
mount_hole_radius = (inner_radius + flange_radius) / 2.0
pocket_width = 12.0
pocket_height = 8.0
pocket_depth = 5.0
side_hole_diameter = 6.0
side_hole_offset = 12.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, body_length))
            l3 = Line(l2@1, (flange_radius, body_length))
            l4 = Line(l3@1, (flange_radius, body_length + flange_thickness))
            l5 = Line(l4@1, (inner_radius, body_length + flange_thickness))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

for i in range(mount_hole_count):
    angle = math.radians(i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, (body_length + flange_thickness) / 2) * Cylinder(mount_hole_diameter / 2, body_length + flange_thickness + 20)

solid_body = solid_body - Pos(0, 0, body_length + flange_thickness - pocket_depth / 2) * Box(pocket_width, pocket_height, pocket_depth)

solid_body = solid_body - Pos(0, side_hole_offset, body_length / 2) * Rot(0, 90, 0) * Cylinder(side_hole_diameter / 2, 2 * outer_radius)

part = solid_body
part.name = "revolved_flange_with_holes"
export_step(part, "output.step")