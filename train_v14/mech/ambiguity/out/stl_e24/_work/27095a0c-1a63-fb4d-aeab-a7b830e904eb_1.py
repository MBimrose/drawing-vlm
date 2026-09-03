from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
notch_width = 20.0
notch_depth = 6.0
central_hole_dia = 10.0
mount_hole_dia = 5.0
mount_hole_offset = 15.0
rib_width = 6.0
rib_height = 6.0
rib_spacing = 20.0
chamfer_size = 0.5

result = Box(plate_length, plate_width, plate_thickness)

notch = Pos(0, plate_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, plate_thickness)
result = result - notch

result = result - Cylinder(central_hole_dia/2, plate_thickness)

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, plate_thickness)

with BuildPart() as rib_bp:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_line:
            Polyline((-rib_width/2, 0), (rib_width/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=plate_thickness/2)
rib_solid = rib_bp.part

for x in [-plate_length/2 + rib_spacing, plate_length/2 - rib_spacing]:
    result = result + Pos(x, 0, plate_thickness/2) * rib_solid

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "plate_with_notch_holes_and_ribs"
export_step(part, "output.step")