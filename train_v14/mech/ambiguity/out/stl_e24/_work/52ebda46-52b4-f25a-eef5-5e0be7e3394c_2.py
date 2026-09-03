from build123d import *

outer_diameter = 40.0
inner_diameter = 20.0
collar_length = 30.0
rib_height = 5.0
rib_width = 10.0
set_screw_diameter = 4.0
set_screw_head_diameter = 7.0
set_screw_head_depth = 2.0
set_screw_offset = 12.0
chamfer_size = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
rib_outer_radius = outer_radius + rib_height

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (inner_radius, collar_length - rib_width))
            l2 = Line(l1@1, (outer_radius, collar_length - rib_width))
            l3 = Line(l2@1, (outer_radius, collar_length))
            l4 = Line(l3@1, (rib_outer_radius, collar_length))
            l5 = Line(l4@1, (rib_outer_radius, 0))
            l6 = Line(l5@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

hole_cyl = Cylinder(set_screw_diameter/2, 2*rib_outer_radius)
csk_cone = Cone(set_screw_head_diameter/2, set_screw_diameter/2, set_screw_head_depth)

for sign in [1, -1]:
    x_pos = sign * (rib_outer_radius - set_screw_head_depth/2)
    csk = Pos(x_pos, 0, set_screw_offset) * Rot(0, -90, 0) * csk_cone
    hole = Pos(x_pos, 0, set_screw_offset) * Rot(0, -90, 0) * hole_cyl
    solid_body = solid_body - csk - hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "collar_with_rib_and_set_screws"
export_step(part, "output.step")