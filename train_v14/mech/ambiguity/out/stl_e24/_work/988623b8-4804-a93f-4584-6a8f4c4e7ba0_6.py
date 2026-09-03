from build123d import *

plate_length = 80.0
plate_width = 60.0
plate_thickness = 6.0
gusset_height = 30.0
gusset_thickness = 4.0
hole_diameter = 5.0
countersink_diameter = 10.0
countersink_angle = 82.0
mount_hole_diameter = 4.0
mount_hole_offset = 5.0
chamfer_distance = 0.8
rib_width = 12.0
rib_height = 4.0
rib_depth = 2.0
rib_spacing = 20.0

solid_body = Box(plate_length, plate_width, plate_thickness)

with BuildPart() as gusset_bp:
    with BuildSketch(Plane.YZ.offset(plate_length/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((0, 0), (gusset_height/2, gusset_height))
            l2 = Line(l1@1, (gusset_height, 0))
            l3 = Line(l2@1, (0, 0))
        make_face()
    extrude(amount=gusset_thickness)

solid_body = solid_body + gusset_bp.part

solid_body = solid_body - Pos(0, 0, plate_thickness/2) * CounterSinkHole(hole_diameter/2, countersink_diameter/2, plate_thickness, countersink_angle)

corner_points = [
    (-plate_length/2 + mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (plate_length/2 - mount_hole_offset, -plate_width/2 + mount_hole_offset),
    (-plate_length/2 + mount_hole_offset, plate_width/2 - mount_hole_offset),
    (plate_length/2 - mount_hole_offset, plate_width/2 - mount_hole_offset),
]
for x, y in corner_points:
    solid_body = solid_body - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, plate_thickness * 2)

rib_count = int((plate_length - 2*mount_hole_offset) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -plate_length/2 + mount_hole_offset + i * rib_spacing
    solid_body = solid_body - Pos(x_pos, 0, -plate_thickness/2 + rib_depth/2) * Box(rib_width, rib_height, rib_depth)

part = solid_body
part.name = "plate_with_gusset_and_ribs"
export_step(part, "output.step")