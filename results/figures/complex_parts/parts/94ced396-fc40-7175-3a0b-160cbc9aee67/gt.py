from build123d import *
base_width = 80.0
base_depth = 40.0
arm_width = 30.0
arm_length = 60.0
thickness = 5.0
boss_radius = 12.0
boss_height = 12.0
through_hole_diameter = 8.0
counterbore_diameter = 14.0
counterbore_depth = 2.5
mount_hole_clearance = 6.0
mount_hole_cbore_diameter = 10.0
mount_hole_cbore_depth = 2.0
mount_hole_offset = 10.0
fillet_radius = 1.0
rib_thickness = 3.0
points = [(-base_width/2, -base_depth/2), (base_width/2, -base_depth/2),
    (base_width/2, base_depth/2), (arm_width/2, base_depth/2),
    (arm_width/2, base_depth/2 + arm_length), (-arm_width/2, base_depth/2 + arm_length),
    (-arm_width/2, base_depth/2), (-base_width/2, base_depth/2)]
with BuildPart() as p:
    with BuildSketch() as sk:
        Polygon(*points)
    extrude(amount=thickness)
solid = p.part
boss_center_y = base_depth/2 + arm_length/2
solid = solid + Pos(0, boss_center_y, thickness + boss_height/2) * Cylinder(boss_radius, boss_height)
solid = solid - Pos(0, boss_center_y, (thickness + boss_height)/2) * Cylinder(through_hole_diameter/2, thickness + boss_height)
solid = solid - Pos(0, boss_center_y, thickness + boss_height - counterbore_depth/2) * Cylinder(counterbore_diameter/2, counterbore_depth)
hw = (base_width - 2*mount_hole_offset) / 2
hd = (base_depth - 2*mount_hole_offset) / 2
for x in [-hw, hw]:
    for y in [-hd, hd]:
        solid = solid - Pos(x, y, thickness/2) * Cylinder(mount_hole_clearance/2, thickness)
        solid = solid - Pos(x, y, thickness - mount_hole_cbore_depth/2) * Cylinder(mount_hole_cbore_diameter/2, mount_hole_cbore_depth)
solid = solid + Pos(-base_width/2 - rib_thickness/2, 0, thickness/2) * Box(rib_thickness, base_depth + arm_length, rib_thickness)
solid = fillet(solid.edges(), fillet_radius)
part = solid
part.name = "L_bracket_with_boss_and_mounting_holes"
export_step(part, OUTPUT_PATH)