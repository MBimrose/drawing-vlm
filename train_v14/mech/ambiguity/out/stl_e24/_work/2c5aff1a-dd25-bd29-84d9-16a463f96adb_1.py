from build123d import *

outer_radius = 45.0
inner_radius = 30.0
housing_length = 70.0
wall_thickness = outer_radius - inner_radius
pocket_width = 20.0
pocket_height = 30.0
pocket_depth = 12.0
fillet_radius = 3.0
mount_hole_diameter = 6.0
mount_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            Line((inner_radius, 0), (outer_radius, 0))
            Line((outer_radius, 0), (outer_radius, housing_length))
            Line((outer_radius, housing_length), (inner_radius, housing_length))
            Line((inner_radius, housing_length), (inner_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part
solid_body = fillet(solid_body.edges(), fillet_radius)

pocket = Pos(-outer_radius + pocket_depth/2, 0, housing_length/2) * Box(pocket_depth, pocket_width, pocket_height)
solid_body = solid_body - pocket

hole1 = Pos(outer_radius - wall_thickness/2, 0, mount_hole_offset) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, housing_length)
hole2 = Pos(-(outer_radius - wall_thickness/2), 0, mount_hole_offset) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter/2, housing_length)
solid_body = solid_body - hole1 - hole2

part = solid_body
part.name = "housing_with_pocket_and_holes"
export_step(part, "output.step")