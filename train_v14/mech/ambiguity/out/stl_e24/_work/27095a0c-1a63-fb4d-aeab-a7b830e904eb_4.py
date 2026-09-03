from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
central_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 30.0
mount_hole_offset = 15.0
rib_height = 6.0
rib_base = 8.0
rib_thickness = 2.0
rib_offset = 20.0
chamfer_distance = 0.5
notch_width = 20.0
notch_depth = 6.0

solid_body = Box(plate_length, plate_width, plate_thickness)
solid_body = solid_body - Cylinder(central_hole_diameter/2, plate_thickness * 2)

for x, y in [(-mount_hole_spacing/2, -mount_hole_offset),
             (mount_hole_spacing/2, -mount_hole_offset),
             (-mount_hole_spacing/2, mount_hole_offset),
             (mount_hole_spacing/2, mount_hole_offset)]:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

notch = Pos(0, plate_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, plate_thickness)
solid_body = solid_body - notch

with BuildPart() as rib_bp:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_line:
            l1 = Line((-rib_base/2, 0), (rib_base/2, 0))
            l2 = Line(l1@1, (0, rib_height))
            l3 = Line(l2@1, (-rib_base/2, 0))
        make_face()
    extrude(amount=rib_thickness)
rib_solid = rib_bp.part

for x_off in [-rib_offset, rib_offset]:
    solid_body = solid_body + Pos(x_off, 0, plate_thickness/2) * rib_solid

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_distance)

part = solid_body
part.name = "plate_with_ribs"
export_step(part, "output.step")