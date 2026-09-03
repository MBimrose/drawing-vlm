from build123d import *

outer_radius = 30
inner_radius = 20
length = 80
wall_thickness = outer_radius - inner_radius
relief_groove_width = 5
relief_groove_depth = 2
relief_groove_position = 50
set_screw_diameter = 5
set_screw_depth = wall_thickness + 2
set_screw_position = 65
chamfer_size = 1

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Polyline((outer_radius, 0), (outer_radius, length), (inner_radius, length), (inner_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

groove = Pos(0, 0, relief_groove_position) * Cylinder(inner_radius + relief_groove_depth, length - relief_groove_position)
solid_body = solid_body - groove

set_screw = Pos(outer_radius - wall_thickness/2, set_screw_depth/2, set_screw_position) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - set_screw

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_groove_and_setscrew"
export_step(part, "output.step")