from build123d import *

inner_diameter = 19.6
wall_thickness = 9.2
outer_diameter = inner_diameter + 2 * wall_thickness
collar_height = 15.0
groove_width = 2.0
groove_depth = 1.0
set_screw_diameter = 3.0
set_screw_offset = 5.0
chamfer_distance = 0.4
rib_thickness = 1.0
rib_height = 2.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, collar_height))
            l3 = Line(l2 @ 1, (inner_radius, collar_height))
            l4 = Line(l3 @ 1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_distance)

groove = Pos(0, 0, collar_height / 2.0) * Cylinder(outer_radius - groove_depth, groove_width)
solid_body = solid_body - groove

set_screw = Pos(outer_radius - wall_thickness / 2.0, set_screw_offset, collar_height / 2.0) * Rot(0, 90, 0) * Cylinder(set_screw_diameter / 2.0, wall_thickness + 0.2)
solid_body = solid_body - set_screw

rib = Pos(0, 0, collar_height + rib_height / 2.0) * Box(rib_thickness, outer_diameter, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "collar_with_groove_and_rib"
export_step(part, "output.step")