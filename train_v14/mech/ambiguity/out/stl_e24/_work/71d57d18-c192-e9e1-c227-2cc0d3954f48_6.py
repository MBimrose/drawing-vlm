from build123d import *

outer_radius = 30.0
inner_radius = 12.0
height = 20.0
chamfer_size = 2.0
groove_width = 4.0
groove_depth = 2.0
boss_radius = 4.0
boss_height = 10.0
boss_offset = 15.0
hole_diameter = 4.0
hole_spacing = 18.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, height))
            l3 = Line(l2@1, (inner_radius, height))
            l4 = Line(l3@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
solid_body = chamfer(top_face.edges(), chamfer_size)
bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

inner_groove = Pos(0, 0, height/2 - groove_depth/2) * Cylinder(inner_radius - groove_width, groove_depth)
solid_body = solid_body - inner_groove

outer_groove = Pos(0, 0, height/2 - groove_depth/2) * Cylinder(outer_radius - groove_width, groove_depth)
solid_body = solid_body - outer_groove

boss = Pos(boss_offset, 0, 0) * Rot(0, 90, 0) * Cylinder(boss_radius, boss_height)
solid_body = solid_body + boss

for x in [-hole_spacing, hole_spacing]:
    hole = Pos(x, 0, height/2) * Cylinder(hole_diameter/2, height)
    solid_body = solid_body - hole

part = solid_body
part.name = "revolved_ring_with_grooves_boss_and_holes"
export_step(part, "output.step")