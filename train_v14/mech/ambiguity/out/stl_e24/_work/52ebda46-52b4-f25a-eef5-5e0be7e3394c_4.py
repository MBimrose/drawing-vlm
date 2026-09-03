from build123d import *
import math

outer_diameter = 45.0
inner_diameter = 20.0
collar_height = 30.0
groove_depth = 5.0
set_screw_diameter = 4.0
set_screw_head_diameter = 8.0
set_screw_head_angle = 82.0
set_screw_count = 4
set_screw_height = collar_height * 0.4
chamfer_size = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, collar_height))
            l3 = Line(l2@1, (inner_radius + groove_depth, collar_height))
            l4 = Line(l3@1, (inner_radius + groove_depth, collar_height - groove_depth))
            l5 = Line(l4@1, (inner_radius, collar_height - groove_depth))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

shaft_r = set_screw_diameter / 2
csk_r = set_screw_head_diameter / 2
csk_h = (csk_r - shaft_r) / math.tan(math.radians(set_screw_head_angle / 2))
hole_depth = wall_thickness + 2.0

for i in range(set_screw_count):
    angle_deg = i * 360.0 / set_screw_count
    angle_rad = math.radians(angle_deg)
    px = (outer_radius - wall_thickness / 2) * math.cos(angle_rad)
    py = (outer_radius - wall_thickness / 2) * math.sin(angle_rad)
    shaft = Pos(px, py, set_screw_height) * Rot(0, 90, angle_deg) * Cylinder(shaft_r, hole_depth)
    csk = Pos(px, py, set_screw_height) * Rot(0, 90, angle_deg) * Cone(csk_r, shaft_r, csk_h)
    solid_body = solid_body - shaft - csk

bottom_edges = solid_body.edges().sort_by(Axis.Z)[:1]
solid_body = chamfer(bottom_edges, chamfer_size)

part = solid_body
part.name = "collar_with_set_screws"
export_step(part, "output.step")