from build123d import *

knob_body_radius = 12.0
knob_body_height = 30.0
flange_radius = 20.0
flange_height = 8.0
inner_cavity_radius = 5.0
inner_cavity_depth = knob_body_height + flange_height - 3.0
shaft_hole_radius = 4.0
counterbore_radius = 6.0
counterbore_depth = 5.0
fillet_radius = 1.5

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((knob_body_radius, 0), (knob_body_radius, knob_body_height))
            l2 = ThreePointArc(l1 @ 1, (flange_radius, knob_body_height + flange_height/2), (flange_radius, knob_body_height + flange_height))
            l3 = Line(l2 @ 1, (0, knob_body_height + flange_height))
            l4 = Line(l3 @ 1, (knob_body_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

cavity = Pos(0, 0, inner_cavity_depth/2) * Cone(knob_body_radius, inner_cavity_radius, inner_cavity_depth)
solid_body = solid_body - cavity

cbore = Pos(0, 0, knob_body_height + flange_height - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)
shaft = Pos(0, 0, (knob_body_height + flange_height)/2) * Cylinder(shaft_hole_radius, knob_body_height + flange_height + 10)
solid_body = solid_body - cbore - shaft

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = fillet(top_edges, fillet_radius)

part = solid_body
part.name = "knob"
export_step(part, "output.step")