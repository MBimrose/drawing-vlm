from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
height = 20.0
set_screw_diameter = 3.0
set_screw_head_diameter = 6.0
set_screw_head_depth = 2.0
inner_radius = outer_diameter/2 - wall_thickness
outer_radius = outer_diameter/2

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as line:
            Polyline((inner_radius, 0), (inner_radius, height), (outer_radius, height), (outer_radius, 0), close=True)
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

hole = Pos(outer_radius - wall_thickness/2, 0, height/2) * Rot(0, 90, 0) * Cylinder(set_screw_diameter/2, wall_thickness*2)
solid_body = solid_body - hole

slot = Pos(outer_radius - set_screw_head_depth/2, 0, height/2) * Box(set_screw_head_depth, set_screw_head_diameter, height*0.9)
solid_body = solid_body - slot

part = solid_body
part.name = "revolved_ring_with_set_screw"
export_step(part, "output.step")