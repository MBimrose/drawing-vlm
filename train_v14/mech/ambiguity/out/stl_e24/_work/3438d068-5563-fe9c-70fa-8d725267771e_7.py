from build123d import *
import math

outer_diameter = 30.0
inner_diameter = 12.0
collar_length = 15.0
tab_width = 6.0
tab_height = 3.0
tab_thickness = 2.0
chamfer_distance = 1.0
mount_hole_diameter = 5.0
mount_hole_offset = 3.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, collar_length))
            l2 = Line(l1 @ 1, (inner_radius, collar_length))
            l3 = Line(l2 @ 1, (inner_radius, 0))
            l4 = Line(l3 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

tab = Pos(outer_radius, 0, collar_length / 2.0) * Box(tab_width, tab_thickness, tab_height)
solid_body = solid_body + tab

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

hole_cyl = Rot(0, 90, 0) * Cylinder(mount_hole_diameter / 2.0, outer_diameter + 2.0)
for y_off in [mount_hole_offset, -mount_hole_offset]:
    solid_body = solid_body - Pos(outer_radius, y_off, collar_length / 2.0) * hole_cyl
    solid_body = solid_body - Pos(-outer_radius, y_off, collar_length / 2.0) * hole_cyl

part = solid_body
part.name = "collar_with_tabs_and_holes"
export_step(part, "output.step")