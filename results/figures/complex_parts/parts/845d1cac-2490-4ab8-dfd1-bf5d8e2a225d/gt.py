from build123d import *

arm_length = 80
base_section_length = 30
arm_height_base = 12
arm_height_tip = 8
arm_thickness = 6
notch_width = 15
notch_height = 6
notch_depth = arm_thickness / 2
notch_x = arm_length * 0.6
threaded_section_length = 20
thread_dia = 12
hole_dia = 4
mount_spacing = 20
mount_x = base_section_length / 2
rib_count = 3
rib_spacing = (arm_length - base_section_length) / (rib_count + 1)
rib_width = 4
rib_height = 2
rib_depth = arm_thickness
chamfer_dist = 0.5
overlap_dist = 15.0

with BuildPart() as p:
    with BuildSketch() as sk:
        with BuildLine() as bl:
            Polyline((0, -arm_height_base/2), (base_section_length, -arm_height_base/2),
                     (arm_length, -arm_height_tip/2), (arm_length, arm_height_tip/2),
                     (base_section_length, arm_height_base/2), (0, arm_height_base/2), close=True)
        make_face()
    extrude(amount=arm_thickness)

solid_body = p.part

notch_y = arm_height_base/2 - (notch_x - base_section_length) / (arm_length - base_section_length) * (arm_height_base/2 - arm_height_tip/2)
notch = Pos(notch_x, notch_y - notch_depth/2, arm_thickness/2) * Box(notch_width, notch_depth, notch_height)
solid_body = solid_body - notch

for x, y in [(mount_x, -mount_spacing/2), (mount_x, mount_spacing/2)]:
    solid_body = solid_body - Pos(x, y, arm_thickness/2) * Cylinder(hole_dia/2, arm_thickness + 10)

for i in range(1, rib_count + 1):
    rib_x = base_section_length + i * rib_spacing
    rib = Pos(rib_x, 0, rib_height/2) * Box(rib_width, rib_depth, rib_height)
    solid_body = solid_body + rib

cyl_center_x = arm_length + threaded_section_length / 2 - overlap_dist
thread_cyl = Pos(cyl_center_x + threaded_section_length/2, 0, 0) * Rot(0, 90, 0) * Cylinder(thread_dia/2, threaded_section_length)
solid_body = solid_body + thread_cyl

solid_body = chamfer(solid_body.edges().filter_by(Axis.Z), chamfer_dist)

part = solid_body
part.name = "arm_with_thread"
export_step(part, OUTPUT_PATH)