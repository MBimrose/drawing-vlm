from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 10.0
rib_height = 8.0
rib_width = 4.0
rib_depth = 6.0
rib_spacing = 12.0
rib_count = int((bracket_length - 2 * rib_spacing) // rib_spacing) + 1
hole_diameter = 5.0
hole_offset = 8.0
counterbore_diameter = 10.0
counterbore_depth = 4.0
chamfer_distance = 0.5

with BuildPart() as p:
    with BuildSketch() as s:
        Rectangle(bracket_length, bracket_width)
    extrude(amount=bracket_thickness)

solid_body = p.part

for i in range(rib_count):
    x = (i - (rib_count - 1) / 2) * rib_spacing
    with BuildPart() as rib_p:
        with BuildSketch(Plane.XY.offset(bracket_thickness)) as rs:
            Rectangle(rib_width, rib_depth)
        extrude(amount=rib_height, taper=-10)
    solid_body = solid_body + Pos(x, 0, 0) * rib_p.part

for x, y in [(-bracket_length/2 + hole_offset, 0), (bracket_length/2 - hole_offset, 0)]:
    solid_body = solid_body - Pos(x, y, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 1)

solid_body = solid_body - Pos(0, 0, bracket_thickness - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
solid_body = solid_body - Pos(0, 0, bracket_thickness/2) * Cylinder(hole_diameter/2, bracket_thickness + 1)

vertical_edges = solid_body.edges().filter_by(Axis.Z)
solid_body = chamfer(vertical_edges, chamfer_distance)

part = solid_body
part.name = "bracket_with_ribs"
export_step(part, "output.step")