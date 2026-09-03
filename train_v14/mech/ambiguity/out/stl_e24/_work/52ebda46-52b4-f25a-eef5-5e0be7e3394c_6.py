from build123d import *
import math

bore_diameter = 20.0
outer_diameter = 45.0
collar_length = 30.0
shoulder_length = 5.0
shoulder_diameter = 40.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 2.5
chamfer_size = 0.8
rib_thickness = 2.0
rib_height = 8.0
rib_position = 10.0

bore_radius = bore_diameter / 2.0
outer_radius = outer_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0
wall_thickness = outer_radius - bore_radius

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((bore_radius, 0), (bore_radius, collar_length - shoulder_length))
            l2 = Line(l1@1, (shoulder_radius, collar_length - shoulder_length))
            l3 = Line(l2@1, (shoulder_radius, collar_length))
            l4 = Line(l3@1, (outer_radius, collar_length))
            l5 = Line(l4@1, (outer_radius, 0))
            l6 = Line(l5@1, (bore_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

rib = Pos(0, 0, rib_position + rib_height/2) * Cylinder(bore_radius + rib_thickness, rib_height)
solid_body = solid_body + rib

for i in range(4):
    angle = i * 90
    rad = math.radians(angle)
    cx = (outer_radius - wall_thickness/2) * math.cos(rad)
    cy = (outer_radius - wall_thickness/2) * math.sin(rad)
    cbore = Pos(cx, cy, collar_length/2 - set_screw_head_depth/2) * Rot(0, 0, angle) * Rot(0, 90, 0) * Cylinder(set_screw_head_diameter/2, set_screw_head_depth)
    solid_body = solid_body - cbore
    shaft = Pos(cx, cy, collar_length/2 - wall_thickness/2) * Rot(0, 0, angle) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, wall_thickness)
    solid_body = solid_body - shaft

part = solid_body
part.name = "collar_with_rib_and_set_screws"
export_step(part, "output.step")