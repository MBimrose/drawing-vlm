from build123d import *

outer_diameter = 80.0
inner_diameter = 30.0
length = 100.0
rib_height = 5.0
rib_width = 20.0
counterbore_diameter = 60.0
counterbore_depth = 30.0
chamfer_size = 2.0
hole_diameter = 10.0
hole_offset = 20.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0
rib_outer_radius = outer_radius + rib_height
counterbore_radius = counterbore_diameter / 2.0
hole_radius = hole_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((inner_radius, 0), (outer_radius, 0))
            l2 = Line(l1@1, (outer_radius, length/2 - rib_width/2))
            l3 = Line(l2@1, (rib_outer_radius, length/2 - rib_width/2))
            l4 = Line(l3@1, (rib_outer_radius, length/2 + rib_width/2))
            l5 = Line(l4@1, (outer_radius, length/2 + rib_width/2))
            l6 = Line(l5@1, (outer_radius, length))
            l7 = Line(l6@1, (inner_radius, length))
            l8 = Line(l7@1, (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = chamfer(solid_body.edges(), chamfer_size)

solid_body = solid_body - Pos(0, 0, length - counterbore_depth/2) * Cylinder(counterbore_radius, counterbore_depth)

hole_cyl = Pos(outer_radius - hole_offset, length/2, length/2) * Rot(90, 0, 0) * Cylinder(hole_radius, length)
solid_body = solid_body - hole_cyl

part = solid_body
part.name = "ribbed_cylinder_with_counterbore"
export_step(part, "output.step")