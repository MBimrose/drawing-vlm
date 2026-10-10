from build123d import *
import math

outer_radius = 30.0
inner_radius = 12.0
collar_length = 20.0
split_gap_width = 4.0
set_screw_diameter = 5.0
set_screw_head_diameter = 10.0
set_screw_head_depth = 3.0
fillet_radius = 2.0
rib_thickness = 2.0
rib_height = 6.0
rib_count = 6

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, collar_length))
            l3 = Line(l2@1, (inner_radius, collar_length))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

slot = Pos(outer_radius - split_gap_width/2, 0, collar_length/2) * Box(split_gap_width, split_gap_width, collar_length)
solid_body = solid_body - slot

boss = Pos(outer_radius, 0, set_screw_head_depth/2) * Cylinder(set_screw_head_diameter/2, set_screw_head_depth)
solid_body = solid_body + boss

hole = Pos(outer_radius, 0, collar_length/2) * Cylinder(set_screw_diameter/2, collar_length)
solid_body = solid_body - hole

for i in range(rib_count):
    angle = i * 360.0 / rib_count
    rib = Rot(0, 0, angle) * Pos(inner_radius + rib_thickness/2, 0, 0) * Box(rib_thickness, rib_height, collar_length)
    solid_body = solid_body + rib

part = solid_body
part.name = "split_collar"
export_step(part, "output.step")