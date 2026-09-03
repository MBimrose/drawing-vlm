from build123d import *

plate_length = 80.0
plate_width = 40.0
plate_thickness = 4.0
rib_height = 5.0
rib_width = 6.0
rib_spacing = 20.0
central_hole_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_offset = 15.0
notch_width = 20.0
notch_depth = 6.0
chamfer_size = 0.5

base = Box(plate_length, plate_width, plate_thickness)

notch = Pos(0, plate_width/2 - notch_depth/2, 0) * Box(notch_width, notch_depth, plate_thickness)
base = base - notch

base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

with BuildPart() as rib_bp:
    with BuildSketch() as rib_sk:
        with BuildLine() as rib_line:
            Polyline((-rib_width/2, 0), (rib_width/2, 0), (0, rib_height), close=True)
        make_face()
    extrude(amount=plate_thickness)

rib_solid = rib_bp.part
rib1 = Pos(-rib_spacing, 0, 0) * rib_solid
rib2 = Pos(rib_spacing, 0, 0) * rib_solid
base = base + rib1 + rib2

total_height = plate_thickness + rib_height
hole_z = rib_height / 2

base = base - Pos(0, 0, hole_z) * Cylinder(central_hole_diameter/2, total_height)

for x, y in [(mount_hole_offset, mount_hole_offset), (-mount_hole_offset, mount_hole_offset),
             (mount_hole_offset, -mount_hole_offset), (-mount_hole_offset, -mount_hole_offset)]:
    base = base - Pos(x, y, hole_z) * Cylinder(mount_hole_diameter/2, total_height)

part = base
part.name = "plate_with_ribs_and_holes"
export_step(part, "output.step")