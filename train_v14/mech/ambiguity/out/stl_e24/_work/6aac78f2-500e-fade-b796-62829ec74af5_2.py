from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 10.0
wall_thickness = 1.0
chamfer_distance = 2.0
pocket_length = 40.0
pocket_width = 30.0
pocket_depth = 6.0
mount_hole_diameter = 4.0
mount_hole_spacing = 20.0
rib_thickness = 2.0
rib_height = 4.0
rib_width = 20.0
side_hole_diameter = 4.0
side_hole_cbore_diameter = 6.0
side_hole_cbore_depth = 2.0
side_hole_spacing = 20.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline(
                (-plate_length/2, -plate_width/2),
                (plate_length/2, -plate_width/2),
                (plate_length/2, plate_width/2 - 10),
                (plate_length/2 - 10, plate_width/2 - 10),
                (plate_length/2 - 10, plate_width/2),
                (-plate_length/2, plate_width/2),
                close=True
            )
        make_face()
    extrude(amount=plate_thickness)

solid_body = p.part
solid_body = offset(solid_body, amount=-wall_thickness)
solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

pocket = Pos(0, plate_width/2 - pocket_depth/2, plate_thickness/2) * Box(pocket_length, pocket_depth, pocket_width)
solid_body = solid_body - pocket

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    solid_body = solid_body - Pos(-plate_length/2, y, plate_thickness/2) * Cylinder(mount_hole_diameter/2, plate_length)

for y in [-side_hole_spacing/2, side_hole_spacing/2]:
    solid_body = solid_body - Pos(plate_length/2 - side_hole_cbore_depth/2, y, plate_thickness/2) * Rot(0, 90, 0) * Cylinder(side_hole_cbore_diameter/2, side_hole_cbore_depth)
    solid_body = solid_body - Pos(plate_length/2 - plate_thickness/2, y, plate_thickness/2) * Rot(0, 90, 0) * Cylinder(side_hole_diameter/2, plate_thickness)

rib = Pos(-plate_length/2 + rib_width/2, 0, wall_thickness + rib_height/2) * Box(rib_width, rib_thickness, rib_height)
solid_body = solid_body + rib

part = solid_body
part.name = "plate_with_pocket_and_holes"
export_step(part, "output.step")