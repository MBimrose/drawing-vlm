from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 10.0
rib_height = 6.0
rib_width = 4.0
rib_spacing = 12.0
rib_margin = 8.0
rib_count = int((bracket_length - 2 * rib_margin) / rib_spacing) + 1
hole_diameter = 5.0
mount_hole_diameter = 5.0
mount_hole_offset = 8.0
counterbore_diameter = 10.0
counterbore_depth = 3.0
chamfer_size = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part

for i in range(rib_count):
    x_pos = -bracket_length / 2 + rib_margin + i * rib_spacing
    with BuildPart() as rib_p:
        with BuildSketch(Plane.XY.offset(bracket_thickness)) as rs:
            Rectangle(rib_width, rib_height)
        extrude(amount=bracket_thickness, taper=10)
    solid_body = solid_body + Pos(x_pos, 0, 0) * rib_p.part

solid_body = solid_body - Cylinder(hole_diameter / 2, bracket_thickness * 2)

for x in [-bracket_length / 2 + mount_hole_offset, bracket_length / 2 - mount_hole_offset]:
    solid_body = solid_body - Pos(x, 0, 0) * Cylinder(mount_hole_diameter / 2, bracket_thickness * 2)

solid_body = solid_body - Pos(0, 0, bracket_thickness - counterbore_depth / 2) * Cylinder(counterbore_diameter / 2, counterbore_depth)

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_size)

part = solid_body
part.name = "bracket_with_ribs"
export_step(part, "output.step")