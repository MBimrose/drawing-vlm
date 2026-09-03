from build123d import *
import math

block_length = 80.0
block_width = 50.0
block_height = 30.0
wall_thickness = 4.0
channel_radius = 6.0
channel_angle_deg = 120.0
channel_angle_rad = math.radians(channel_angle_deg)
channel_center_radius = 20.0
chamfer_size = 1.0
mount_hole_dia = 5.0
mount_hole_offset = 8.0
rib_width = 6.0
rib_height = 10.0
rib_thickness = 3.0

start_pt = (channel_center_radius * math.cos(-channel_angle_rad/2), 0, channel_center_radius * math.sin(-channel_angle_rad/2))
end_pt = (channel_center_radius * math.cos(channel_angle_rad/2), 0, channel_center_radius * math.sin(channel_angle_rad/2))
mid_pt = (0, 0, 0)

with BuildLine() as bl:
    ThreePointArc(Vector(start_pt), Vector(mid_pt), Vector(end_pt))
path_wire = bl.wire()

with BuildSketch() as sk:
    Circle(channel_radius)
profile_face = sk.face()

channel_solid = sweep(sections=profile_face, path=path_wire)

block = Box(block_length, block_width, block_height)
result = block - channel_solid

hole_positions = [
    (-block_length/2 + mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset, -block_width/2 + mount_hole_offset),
    ( block_length/2 - mount_hole_offset,  block_width/2 - mount_hole_offset),
    (-block_length/2 + mount_hole_offset,  block_width/2 - mount_hole_offset)
]
for x, y in hole_positions:
    result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, block_height)

rib = Pos(0, block_width/4, block_height/2 - rib_thickness/2) * Box(rib_width, rib_height, rib_thickness)
result = result + rib

vertical_edges = result.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "block_with_channel"
export_step(part, "output.step")