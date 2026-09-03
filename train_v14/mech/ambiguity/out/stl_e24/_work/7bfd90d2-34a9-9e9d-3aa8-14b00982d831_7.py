from build123d import *

outer_radius = 30.0
inner_radius = 8.0
height = 20.0
keyway_width = 6.0
keyway_depth = 4.0
set_screw_diameter = 4.0
set_screw_depth = 8.0
set_screw_offset = 10.0
chamfer_size = 1.0
pocket_width = 12.0
pocket_height = 4.0
pocket_depth = 3.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, height))
            l2 = Line(l1@1, (inner_radius, height))
            l3 = Line(l2@1, (inner_radius, 0))
            l4 = Line(l3@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

keyway = Pos(outer_radius - keyway_depth/2, 0, 0) * Box(keyway_depth, keyway_width, height)
solid_body = solid_body - keyway

hole1 = Pos(outer_radius - set_screw_depth/2, 0, set_screw_offset) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole1

hole2 = Pos(outer_radius - set_screw_depth/2, 0, -set_screw_offset) * Rot(90, 0, 0) * Cylinder(set_screw_diameter/2, set_screw_depth)
solid_body = solid_body - hole2

pocket = Pos(outer_radius - pocket_depth/2, 0, 0) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "revolved_ring_with_keyway"
export_step(part, "output.step")