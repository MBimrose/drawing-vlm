from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
rib_height = 5.0
rib_width = 20.0
rib_position = 40.0
set_screw_diameter = 6.0
set_screw_counterbore_diameter = 12.0
set_screw_counterbore_depth = 5.0
chamfer_size = 2.0
counterbore_diameter = 60.0
counterbore_depth = 10.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
wall_thickness = outer_radius - inner_radius
set_screw_radius = set_screw_diameter / 2.0
set_screw_counterbore_radius = set_screw_counterbore_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, rib_position))
            l3 = Line(l2@1, (outer_radius + rib_height, rib_position))
            l4 = Line(l3@1, (outer_radius + rib_height, rib_position + rib_width))
            l5 = Line(l4@1, (outer_radius, rib_position + rib_width))
            l6 = Line(l5@1, (outer_radius, length))
            l7 = Line(l6@1, (inner_radius, length))
            l8 = Line(l7@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

cbore = Pos(0, 0, length - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - cbore

radial_offset = outer_radius - wall_thickness / 2.0
set_screw_hole = Pos(radial_offset, length/2, 0) * Rot(90, 0, 0) * Cylinder(set_screw_radius, length)
solid_body = solid_body - set_screw_hole

counterbore = Pos(radial_offset, length/2, 0) * Rot(90, 0, 0) * Cylinder(set_screw_counterbore_radius, set_screw_counterbore_depth)
solid_body = solid_body - counterbore

part = solid_body
part.name = "ribbed_cylinder_with_set_screw"
export_step(part, "output.step")