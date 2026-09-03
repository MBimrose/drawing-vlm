from build123d import *

leg_length = 80.0
leg_height = 70.0
thickness = 10.0
depth = 12.0
fillet_radius = 2.0
pocket_width = 30.0
pocket_depth = 6.0
pocket_offset_from_top = 5.0
hole_diameter = 4.5
hole_offset_from_top = 5.0
mount_hole_diameter = 6.0
mount_hole_offset = 40.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, 0), (leg_length, 0), (leg_length, thickness), (thickness, thickness), (thickness, leg_height), (0, leg_height), close=True)
        make_face()
    extrude(amount=depth)

solid_body = p.part
solid_body = fillet(solid_body.edges().filter_by(Axis.Z), fillet_radius)

pocket_center_y = leg_height - pocket_offset_from_top - pocket_width / 2
pocket = Pos(thickness/2, pocket_center_y, depth - pocket_depth/2) * Box(pocket_width, pocket_depth, pocket_depth)
solid_body = solid_body - pocket

hole_center_y = leg_height - hole_offset_from_top
hole = Pos(thickness/2, hole_center_y, 0) * Cylinder(hole_diameter/2, depth + 1)
solid_body = solid_body - hole

mount_hole_x = Pos(mount_hole_offset, thickness/2, 0) * Cylinder(mount_hole_diameter/2, depth + 1)
solid_body = solid_body - mount_hole_x

mount_hole_y = Pos(thickness/2, mount_hole_offset, 0) * Cylinder(mount_hole_diameter/2, depth + 1)
solid_body = solid_body - mount_hole_y

part = solid_body
part.name = "L_bracket"
export_step(part, "output.step")