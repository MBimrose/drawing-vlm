from build123d import *

outer_length = 80.0
outer_width = 50.0
outer_height = 30.0
wall_thickness = 2.0
snap_tab_width = 12.0
snap_tab_height = 6.0
snap_tab_thickness = 3.0
snap_notch_width = 4.0
snap_notch_depth = 1.0
rib_thickness = 1.5
rib_height = 5.0
rib_spacing = 15.0
hole_diameter = 3.0
hole_spacing_x = 20.0
hole_spacing_y = 15.0
hole_rows = 2
hole_cols = 3
chamfer_size = 0.5

base = Pos(0, 0, outer_height/2) * Box(outer_length, outer_width, outer_height)
top_face = base.faces().sort_by(Axis.Z)[-1]
bottom_face = base.faces().sort_by(Axis.Z)[0]
base = offset(base, amount=-wall_thickness, openings=[top_face, bottom_face])

tab = Pos(0, outer_width/2 + snap_tab_thickness/2, outer_height/2 - snap_tab_height/2 - wall_thickness) * Box(snap_tab_width, snap_tab_thickness, snap_tab_height)
base = base + tab

notch = Pos(0, outer_width/2 + snap_tab_thickness - snap_notch_depth/2, outer_height/2 - snap_tab_height/2 - wall_thickness) * Box(snap_notch_width, snap_notch_depth, snap_tab_height - 2*snap_notch_depth)
base = base - notch

num_ribs = int((outer_height - 2*wall_thickness) // rib_spacing)
for i in range(num_ribs):
    z_pos = wall_thickness + rib_spacing/2 + i * rib_spacing
    rib = Pos(0, -outer_width/2 - rib_thickness/2, z_pos) * Box(rib_thickness, rib_thickness, rib_height)
    base = base + rib

for row in range(hole_rows):
    for col in range(hole_cols):
        x = (col - (hole_cols-1)/2) * hole_spacing_x
        y = (row - (hole_rows-1)/2) * hole_spacing_y
        hole = Pos(x, y, outer_height - wall_thickness/2) * Cylinder(hole_diameter/2, wall_thickness)
        base = base - hole

top_edges = base.edges().filter_by(Axis.Z).sort_by(Axis.Z)[-1:]
base = chamfer(top_edges, chamfer_size)

part = base
part.name = "snap_fit_box"
export_step(part, "output.step")