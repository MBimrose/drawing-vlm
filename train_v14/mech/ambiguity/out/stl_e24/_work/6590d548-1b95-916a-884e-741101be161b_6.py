from build123d import *

base_radius = 30.0
top_width = 45.0
top_depth = 30.0
total_height = 60.0
pocket_width = 20.0
pocket_depth = 8.0
pocket_depth_cut = 10.0
fillet_radius = 2.0
mount_hole_diameter = 4.0
mount_hole_spacing = 25.0
mount_hole_offset = 15.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Circle(base_radius)
    with BuildSketch(Plane.XY.offset(total_height)) as s2:
        Rectangle(top_width, top_depth)
    loft()

solid_body = p.part

pocket = Pos(0, 0, total_height - pocket_depth_cut / 2) * Box(pocket_width, pocket_depth, pocket_depth_cut)
solid_body = solid_body - pocket

solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    hole = Pos(x, mount_hole_offset, total_height / 2) * Cylinder(mount_hole_diameter / 2, total_height + 10)
    solid_body = solid_body - hole

part = solid_body
part.name = "lofted_mount_with_pocket"
export_step(part, "output.step")