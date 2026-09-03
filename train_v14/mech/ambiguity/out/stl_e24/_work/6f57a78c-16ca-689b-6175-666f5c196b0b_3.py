from build123d import *

outer_diameter = 80.0
inner_diameter = 60.0
length = 80.0
wall_thickness = (outer_diameter - inner_diameter) / 2.0
pocket_width = 20.0
pocket_height = 10.0
pocket_depth = wall_thickness - 2.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
chamfer_size = 1.0

outer_radius = outer_diameter / 2.0
inner_radius = inner_diameter / 2.0

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine() as bl:
            l1 = Line((outer_radius, 0), (outer_radius, length))
            l2 = Line(l1 @ 1, (inner_radius, length))
            l3 = Line(l2 @ 1, (inner_radius, 0))
            l4 = Line(l3 @ 1, (outer_radius, 0))
        make_face()
    revolve(axis=Axis.Z)

solid_body = p.part

pocket_box = Pos(0, 0, length / 2.0) * Box(pocket_width, outer_diameter + 10, pocket_height)
solid_body = solid_body - pocket_box

for x in [-mount_hole_spacing / 2.0, mount_hole_spacing / 2.0]:
    hole = Pos(x, 0, length / 2.0) * Rot(90, 0, 0) * Cylinder(mount_hole_diameter / 2.0, outer_diameter + 10)
    solid_body = solid_body - hole

solid_body = chamfer(solid_body.edges(), chamfer_size)

part = solid_body
part.name = "hollow_cylinder_with_pocket_and_mount_holes"
export_step(part, "output.step")