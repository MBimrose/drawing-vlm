from build123d import *

outer_radius = 30.0
housing_height = 60.0
step_height = 20.0
inner_radius_step1 = 10.0
inner_radius_step2 = 6.0
rib_width = 12.0
rib_height = 4.0
rib_position = 35.0
set_screw_hole_diameter = 5.0
set_screw_offset = outer_radius - 7.0
chamfer_size = 1.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as line:
            l1 = Line((0, 0), (outer_radius, 0))
            l2 = Line(l1 @ 1, (outer_radius, housing_height))
            l3 = Line(l2 @ 1, (0, housing_height))
            l4 = Line(l3 @ 1, (0, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

bottom_bore = Pos(0, 0, step_height/2) * Cylinder(inner_radius_step1, step_height)
top_bore = Pos(0, 0, step_height + (housing_height - step_height)/2) * Cylinder(inner_radius_step2, housing_height - step_height)
solid_body = solid_body - bottom_bore - top_bore

rib_outer_radius = outer_radius + rib_height
rib_outer = Pos(0, 0, rib_position + rib_width/2) * Cylinder(rib_outer_radius, rib_width)
rib_inner = Pos(0, 0, rib_position + rib_width/2) * Cylinder(outer_radius, rib_width)
rib_ring = rib_outer - rib_inner
solid_body = solid_body + rib_ring

hole = Pos(set_screw_offset, 0, housing_height/2) * Cylinder(set_screw_hole_diameter/2, housing_height)
solid_body = solid_body - hole

top_face = solid_body.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
solid_body = chamfer(top_edges, chamfer_size)

part = solid_body
part.name = "stepped_housing_with_rib"
export_step(part, OUTPUT_PATH)