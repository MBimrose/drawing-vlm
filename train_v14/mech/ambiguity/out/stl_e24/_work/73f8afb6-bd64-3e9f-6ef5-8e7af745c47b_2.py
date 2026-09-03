from build123d import *

outer_diameter = 80.0
wall_thickness = 5.0
height = 30.0
groove_width = 4.0
groove_depth = 2.0
groove_position = 15.0
tab_width = 20.0
tab_height = 10.0
tab_thickness = wall_thickness
mount_hole_diameter = 5.0
mount_hole_spacing = 14.0
chamfer_size = 0.8

outer_radius = outer_diameter / 2.0
inner_radius = outer_radius - wall_thickness

shell = Cylinder(outer_radius, height) - Cylinder(inner_radius, height)
shell = chamfer(shell.edges(), chamfer_size)

groove = Pos(0, 0, groove_position - height/2 + groove_width/2) * Cylinder(inner_radius - groove_depth, groove_width)
shell = shell - groove

tab = Pos(outer_radius + tab_thickness/2 - 0.5, 0, 0) * Box(tab_thickness, tab_width, tab_height)
shell = shell + tab

for y in [-mount_hole_spacing/2, mount_hole_spacing/2]:
    hole = Pos(outer_radius + tab_thickness/2 - 0.5, y, 0) * Rot(0, 90, 0) * Cylinder(mount_hole_diameter/2, 200)
    shell = shell - hole

part = shell
part.name = "cylindrical_shell_with_tab"
export_step(part, "output.step")