from build123d import *

outer_radius = 30.0
knob_height = 20.0
inner_radius = 8.0
wall_thickness = 2.0
pocket_width = 12.0
pocket_depth = 6.0
pocket_height = 8.0
set_screw_diameter = 4.0
set_screw_offset = 5.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, knob_height))
            l3 = Line(l2@1, (inner_radius, knob_height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

pocket = Pos(outer_radius - pocket_depth/2, 0, pocket_height/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

hole1 = Pos(outer_radius - wall_thickness/2, set_screw_offset, knob_height/2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, wall_thickness + 2)
solid_body = solid_body - hole1

hole2 = Pos(outer_radius - wall_thickness/2, -set_screw_offset, knob_height/2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, wall_thickness + 2)
solid_body = solid_body - hole2

part = solid_body
part.name = "knob_with_pocket_and_set_screw_holes"
export_step(part, "output.step")