from build123d import *

outer_diameter = 45.0
inner_diameter = 20.0
collar_height = 30.0
shoulder_height = 5.0
shoulder_diameter = 40.0
set_screw_diameter = 4.0
set_screw_head_diameter = 8.0
set_screw_head_depth = 3.0
chamfer_size = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
shoulder_radius = shoulder_diameter / 2.0
wall_thickness = outer_radius - inner_radius
set_screw_radius = set_screw_diameter / 2.0
set_screw_head_radius = set_screw_head_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, collar_height))
            l2 = Line(l1@1, (shoulder_radius, collar_height))
            l3 = Line(l2@1, (shoulder_radius, collar_height - shoulder_height))
            l4 = Line(l3@1, (inner_radius, collar_height - shoulder_height))
            l5 = Line(l4@1, (inner_radius, 0))
            l6 = Line(l5@1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

solid_body = solid_body - Pos(0, 0, collar_height/2) * Cylinder(set_screw_radius, collar_height)

radial_cut = Pos(outer_radius - wall_thickness/2, 0, collar_height/2 - wall_thickness/2) * Rot(0, 90, 0) * Cylinder(set_screw_radius, wall_thickness)
cbore_cut = Pos(outer_radius - set_screw_head_depth/2, 0, collar_height/2 - set_screw_head_depth/2) * Rot(0, 90, 0) * Cylinder(set_screw_head_radius, set_screw_head_depth)
radial_hole = radial_cut + cbore_cut

for i in range(4):
    solid_body = solid_body - Rot(0, 0, i * 90) * radial_hole

bottom_face = solid_body.faces().sort_by(Axis.Z)[0]
solid_body = chamfer(bottom_face.edges(), chamfer_size)

part = solid_body
part.name = "collar_with_set_screw_holes"
export_step(part, "output.step")