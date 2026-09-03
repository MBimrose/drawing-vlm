from build123d import *

outer_width = 80.0
outer_length = 60.0
outer_height = 12.0
wall_thickness = 5.0
top_radius = outer_width / 2.0
hole_diameter = 5.0
hole_spacing_x = 30.0
hole_spacing_y = 30.0
hole_rows = 2
hole_cols = 2
chamfer_size = 1.0
rib_width = 6.0
rib_length = 30.0
rib_height = 3.0

base = Box(outer_width, outer_length, outer_height)
rounded_top = Pos(0, outer_length / 2.0, 0) * Cylinder(top_radius, outer_height)
outer_body = base + rounded_top

inner_width = outer_width - 2 * wall_thickness
inner_length = outer_length - 2 * wall_thickness
inner_height = outer_height - wall_thickness
inner_cut = Pos(0, 0, wall_thickness / 2.0) * Box(inner_width, inner_length, inner_height)
shelled = outer_body - inner_cut

rib = Pos(0, 0, -outer_height / 2 + rib_height / 2) * Box(rib_width, rib_length, rib_height)
with_ribs = shelled + rib

hole_depth = outer_height - wall_thickness
hole_cyl = Cylinder(hole_diameter / 2, hole_depth)
for i in range(hole_cols):
    for j in range(hole_rows):
        x = (i - (hole_cols - 1) / 2) * hole_spacing_x
        y = (j - (hole_rows - 1) / 2) * hole_spacing_y
        with_ribs = with_ribs - Pos(x, y, outer_height / 2 - hole_depth / 2) * hole_cyl

vertical_edges = with_ribs.edges().filter_by(Axis.Z)
result = chamfer(vertical_edges, chamfer_size)

part = result
part.name = "rounded_box_with_ribs_and_holes"
export_step(part, "output.step")