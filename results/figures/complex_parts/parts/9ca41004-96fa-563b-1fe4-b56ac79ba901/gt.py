from build123d import *

base_width = 70.0
base_length = 80.0
base_thickness = 10.0
rib_thickness = 3.0
rib_height = 5.0
large_diameter = 30.0
small_diameter = 15.0
large_radius = large_diameter/2
small_radius = small_diameter/2
large_height = 20.0
arm_length = 60.0
total_height = large_height + arm_length
mount_hole_dia = 5.0
mount_hole_spacing = 30.0
pocket_width = 20.0
pocket_depth = 12.0
fillet_radius = 3.0
chamfer_distance = 1.0

base = Box(base_width, base_length, base_thickness)
rib = Pos(0, 0, base_thickness/2 + rib_height/2) * Box(base_width - 20.0, rib_thickness, rib_height)

with BuildPart() as p:
    with BuildSketch(Plane.XZ) as sk:
        with BuildLine():
            Polyline((0, 0), (large_radius, 0), (large_radius, large_height),
                     (small_radius, large_height), (small_radius, total_height),
                     (0, total_height), close=True)
        make_face()
    revolve(axis=Axis.Z)
arm = Pos(0, 0, base_thickness/2) * p.part

result = base + rib + arm

half_spacing = mount_hole_spacing / 2
for i in range(2):
    for j in range(2):
        x = -half_spacing + i * mount_hole_spacing
        y = -half_spacing + j * mount_hole_spacing
        result = result - Pos(x, y, 0) * Cylinder(mount_hole_dia/2, 100)

pocket_center_z = base_thickness/2 + large_height + arm_length/2
pocket_box = Pos(small_radius - pocket_depth/2, 0, pocket_center_z) * Box(pocket_width, pocket_depth, pocket_width)
result = result - pocket_box

vertical_edges = result.edges().filter_by(Axis.Z)
positive_x_edges = [e for e in vertical_edges if e.center().X > 0]
result = fillet(positive_x_edges, fillet_radius)

bottom_face = result.faces().sort_by(Axis.Z)[0]
result = chamfer(bottom_face.edges(), chamfer_distance)

part = result
part.name = "base_with_arm_and_pocket"
export_step(part, OUTPUT_PATH)