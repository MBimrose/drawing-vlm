from build123d import *
import math

outer_radius = 45.0
inner_radius = 10.0
thickness = 8.0
split_gap = 2.0
chamfer_size = 0.5
mount_hole_dia = 4.0
mount_hole_radius = 30.0
mount_hole_count = 4
tab_width = 12.0
tab_height = 6.0
tab_thickness = 2.0

solid_body = Cylinder(outer_radius, thickness)
solid_body = solid_body - Cylinder(inner_radius, thickness)

for i in range(mount_hole_count):
    angle = math.radians(45 + i * 360.0 / mount_hole_count)
    px = mount_hole_radius * math.cos(angle)
    py = mount_hole_radius * math.sin(angle)
    solid_body = solid_body - Pos(px, py, 0) * Cylinder(mount_hole_dia / 2, thickness)

tab = Pos(outer_radius - tab_thickness / 2, 0, 0) * Box(tab_width, tab_thickness, thickness)
solid_body = solid_body + tab

split_cut = Box(outer_radius * 2, split_gap, thickness + 2)
solid_body = solid_body - split_cut

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_size)

part = solid_body
part.name = "split_ring_with_tab"
export_step(part, "output.step")