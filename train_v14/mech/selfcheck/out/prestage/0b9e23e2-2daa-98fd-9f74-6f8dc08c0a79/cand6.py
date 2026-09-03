from build123d import *

block_length = 100.0
block_width = 60.0
block_height = 30.0
bearing_radius = 20.0
bearing_depth = 20.0
sensor_hole_dia = 6.0
sensor_counterbore_dia = 12.0
sensor_counterbore_depth = 4.0
sensor_offset_x = 0.0
sensor_offset_y = 20.0
mount_hole_dia = 4.0
mount_hole_offset = 8.0
rib_width = 4.0
rib_height = 10.0
rib_thickness = 2.0
rib_spacing = 15.0
chamfer_size = 1.0
slot_width = 5.0
slot_height = 10.0
slot_depth = 5.0

result = Box(block_length, block_width, block_height)

with BuildPart() as bp:
    with BuildSketch(Plane.XY.offset(block_height/2)) as sk:
        with BuildLine() as bl:
            l1 = Line((-bearing_radius, 0), (-bearing_radius, -bearing_depth))
            l2 = Line(l1@1, (bearing_radius, -bearing_depth))
            ThreePointArc(l2@1, (0, -bearing_depth/2), (-bearing_radius, 0))
        make_face()
    extrude(amount=-bearing_depth)
result = result - bp.part

result = result - Pos(sensor_offset_x, sensor_offset_y, block_height/2 - sensor_counterbore_depth/2) * Cylinder(sensor_counterbore_dia/2, sensor_counterbore_depth)
result = result - Pos(sensor_offset_x, sensor_offset_y, 0) * Cylinder(sensor_hole_dia/2, block_height + 10)

corner_x = block_length/2 - mount_hole_offset
corner_y = block_width/2 - mount_hole_offset
for x, y in [(corner_x, corner_y), (-corner_x, corner_y), (-corner_x, -corner_y), (corner_x, -corner_y)]:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height + 10)

result = result - Pos(block_length/2 - slot_depth/2, block_width/2 - slot_depth/2, -block_height/4) * Box(slot_depth, slot_width, slot_height)
result = result - Pos(-block_length/2 + slot_depth/2, -block_width/2 + slot_depth/2, block_height/4) * Box(slot_depth, slot_width, slot_height)

rib_count = int((block_length - 2*mount_hole_offset) // rib_spacing) + 1
for i in range(rib_count):
    x_pos = -block_length/2 + mount_hole_offset + i * rib_spacing
    result = result + Pos(x_pos, 0, -block_height/2 + rib_height/2) * Box(rib_width, rib_thickness, rib_height)

result = chamfer(result.edges().filter_by(Axis.Z), chamfer_size)

part = result
part.name = "bearing_block"
export_step(part, "output.step")