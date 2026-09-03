from build123d import *

knob_outer_radius = 20.0
knob_body_height = 30.0
shoulder_radius = 12.0
shoulder_height = 8.0
dome_radius = 22.0
dome_height = 6.0
shaft_hole_diameter = 8.0
shaft_hole_depth = 45.0
counterbore_diameter = 12.0
counterbore_depth = 3.0
inner_cone_depth = 20.0
inner_cone_radius = 10.0
boss_radius = 5.0
boss_height = 4.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((shoulder_radius, 0), (shoulder_radius, knob_body_height))
            a1 = ThreePointArc(l1 @ 1, (shoulder_radius, knob_body_height + shoulder_height/2), (shoulder_radius + shoulder_radius/2, knob_body_height + shoulder_height))
            l2 = Line(a1 @ 1, (dome_radius, knob_body_height + shoulder_height + dome_height))
            l3 = Line(l2 @ 1, (0, knob_body_height + shoulder_height + dome_height))
            l4 = Line(l3 @ 1, (shoulder_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
top_z = knob_body_height + shoulder_height + dome_height

solid_body = solid_body - Pos(0, 0, top_z - shaft_hole_depth/2) * Cylinder(shaft_hole_diameter/2, shaft_hole_depth)
solid_body = solid_body - Pos(0, 0, top_z - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(0, 0, inner_cone_depth/2) * Cone(inner_cone_radius, 0, inner_cone_depth)
solid_body = solid_body + Pos(0, 0, top_z + boss_height/2) * Cylinder(boss_radius, boss_height)

part = solid_body
part.name = "knob"
export_step(part, "output.step")