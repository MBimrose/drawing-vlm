from build123d import *

bracket_length = 80.0
bracket_width = 40.0
bracket_thickness = 10.0
rib_height = 8.0
rib_width = 6.0
rib_spacing = 12.0
rib_draft_angle = 5.0
hole_diameter = 5.0
hole_offset = 8.0
counterbore_diameter = 10.0
counterbore_depth = 3.0
chamfer_size = 0.5

base = Box(bracket_length, bracket_width, bracket_thickness)

num_ribs = int((bracket_length - 2 * hole_offset) // rib_spacing) + 1
rib_positions = [(-bracket_length/2 + hole_offset + i * rib_spacing) for i in range(num_ribs)]

with BuildPart() as rib_bp:
    with BuildSketch() as rib_sk:
        Rectangle(rib_width, rib_height)
    extrude(amount=rib_height, taper=rib_draft_angle)
rib_solid = rib_bp.part

for x in rib_positions:
    base = base + Pos(x, 0, bracket_thickness/2) * rib_solid

hole_positions = [(-bracket_length/2 + hole_offset), (bracket_length/2 - hole_offset)]
for x in hole_positions:
    base = base - Pos(x, 0, 0) * Cylinder(hole_diameter/2, bracket_thickness * 2)

base = base - Pos(0, 0, bracket_thickness/2 - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
base = base - Cylinder(hole_diameter/2, bracket_thickness * 2)

vertical_edges = base.edges().filter_by(Axis.Z)
base = chamfer(vertical_edges, chamfer_size)

part = base
part.name = "bracket_with_ribs"
export_step(part, "output.step")