from build123d import *

rect_width = 80.0
rect_height = 40.0
loft_height = 30.0
circle_diameter = 30.0
vent_diameter = 10.0
mount_hole_diameter = 5.0
mount_hole_spacing = 60.0
side_rib_width = 8.0
side_rib_height = 20.0
side_rib_offset = 5.0
chamfer_dist = 1.0
boss_thickness = 4.0
boss_extension = 5.0

with BuildPart() as p:
    with BuildSketch() as s1:
        Rectangle(rect_width, rect_height)
    with BuildSketch(Plane.XY.offset(loft_height)) as s2:
        Circle(circle_diameter / 2)
    loft()

solid = p.part

solid = solid - Pos(0, 0, loft_height / 2) * Cylinder(vent_diameter / 2, loft_height + 20)

for x in [-mount_hole_spacing / 2, mount_hole_spacing / 2]:
    solid = solid - Pos(x, 0, loft_height / 2) * Cylinder(mount_hole_diameter / 2, loft_height + 20)

rib = Pos(0, 0, side_rib_height / 2) * Box(rect_width - 2 * side_rib_offset, side_rib_width, side_rib_height)
solid = solid + rib

boss = Pos(0, 0, boss_thickness / 2) * Cylinder((vent_diameter / 2) + boss_extension, boss_thickness)
solid = solid + boss

vertical_edges = solid.edges().filter_by(Axis.Z)
solid = chamfer(vertical_edges, chamfer_dist)

part = solid
part.name = "lofted_vent_panel"
export_step(part, OUTPUT_PATH)