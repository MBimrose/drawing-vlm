from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
notch_width = 10.0
notch_depth = 5.0
central_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0
rib_height = 6.0
rib_thickness = 2.0
rib_offset = 10.0
chamfer_size = 0.5

solid_body = Box(plate_length, plate_width, plate_thickness)

notch = Pos(0, plate_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, plate_thickness)
solid_body = solid_body - notch

solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness)

mount_points = [
    (mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, mount_hole_offset),
    (-mount_hole_offset, -mount_hole_offset),
    (mount_hole_offset, -mount_hole_offset),
]
for x, y in mount_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness)

rib_positions = [(-plate_length/2 + rib_offset, 0), (plate_length/2 - rib_offset, 0)]
for x, y in rib_positions:
    with BuildPart() as rib_bp:
        with BuildSketch() as rib_sk:
            with BuildLine() as rib_line:
                Polyline((-rib_height/2, 0), (rib_height/2, 0), (0, rib_height), close=True)
            make_face()
        extrude(amount=rib_thickness)
    rib = Pos(x, y, plate_thickness/2) * rib_bp.part
    solid_body = solid_body + rib

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "plate_with_notch_holes_and_ribs"
export_step(part, "output.step")