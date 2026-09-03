from build123d import *

body_height = 80.0
outer_radius = 15.0
wall_thickness = 2.0
chamfer_distance = 0.5
mount_tab_width = 12.0
mount_tab_thickness = 3.0
mount_tab_height = 5.0
pocket_width = 6.0
pocket_depth = 4.0
pocket_offset_from_top = 20.0
hole_diameter = 2.5
hole_offset_from_bottom = 15.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, body_height))
            l3 = Line(l2 @ 1, (0, body_height))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_distance)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_distance)

tab = Pos(outer_radius - mount_tab_width/2, 0, body_height + mount_tab_height/2) * Box(mount_tab_width, mount_tab_thickness, mount_tab_height)
solid_body = solid_body + tab

pocket = Pos(outer_radius - pocket_depth/2, 0, body_height - pocket_offset_from_top) * Box(pocket_depth, pocket_width, pocket_depth)
solid_body = solid_body - pocket

hole = Pos(outer_radius - wall_thickness/2, 0, hole_offset_from_bottom) * Rot(0, 90, 0) * Cylinder(hole_diameter/2, wall_thickness*2)
solid_body = solid_body - hole

part = solid_body
part.name = "cylindrical_body_with_features"
export_step(part, "output.step")