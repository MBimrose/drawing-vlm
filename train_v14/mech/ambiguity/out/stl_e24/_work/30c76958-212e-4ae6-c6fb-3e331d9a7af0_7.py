from build123d import *

outer_length = 80.0
outer_width = 60.0
outer_height = 12.0
wall_thickness = 4.0
tab_width = 20.0
tab_height = 6.0
tab_thickness = 2.0
rib_thickness = 2.0
rib_height = 3.0
rib_spacing = 10.0
mount_hole_diameter = 4.0
mount_hole_offset = 10.0
chamfer_size = 0.5

base = Box(outer_length, outer_width, outer_height)
tab = Pos(0, outer_width/2 + tab_thickness/2, 0) * Box(tab_width, tab_thickness, tab_height)
combined = base + tab

inner_length = outer_length - 2 * wall_thickness
inner_width = outer_width - 2 * wall_thickness
inner_height = outer_height - wall_thickness
cavity = Pos(0, 0, -wall_thickness/2) * Box(inner_length, inner_width, inner_height)
shelled = combined - cavity

num_ribs = int((inner_width - rib_thickness) // (rib_spacing + rib_thickness)) + 1
rib_positions = [(-inner_width/2 + rib_thickness/2 + i * (rib_spacing + rib_thickness)) for i in range(num_ribs)]
ribs = Compound([Pos(0, y, -wall_thickness/2) * Box(inner_length, rib_thickness, rib_height) for y in rib_positions])
with_ribs = shelled + ribs

hole_positions = [
    (-outer_length/2 + mount_hole_offset, -outer_width/2 + mount_hole_offset),
    ( outer_length/2 - mount_hole_offset, -outer_width/2 + mount_hole_offset),
    (-outer_length/2 + mount_hole_offset,  outer_width/2 - mount_hole_offset),
    ( outer_length/2 - mount_hole_offset,  outer_width/2 - mount_hole_offset)
]
with_holes = with_ribs
for x, y in hole_positions:
    with_holes = with_holes - Pos(x, y, 0) * Cylinder(mount_hole_diameter/2, outer_height * 2)

top_face = with_holes.faces().sort_by(Axis.Z)[-1]
top_edges = top_face.edges()
result = chamfer(top_edges, chamfer_size)

part = result
part.name = "box_with_tabs_ribs_and_holes"
export_step(part, "output.step")