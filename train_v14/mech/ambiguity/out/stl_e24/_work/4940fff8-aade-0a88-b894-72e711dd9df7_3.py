from build123d import *

plate_width = 80.0
plate_length = 80.0
plate_thickness = 5.0
frame_height = 6.0
frame_thickness = 4.0
boss_width = 12.0
boss_length = 12.0
boss_height = 4.0
hole_diameter = 5.0
hole_depth = 3.0
hole_spacing_x = 18.0
hole_spacing_y = 18.0
chamfer_size = 0.5

base = Pos(0, 0, plate_thickness/2) * Box(plate_width, plate_length, plate_thickness)
base = chamfer(base.edges().filter_by(Axis.Z), chamfer_size)

frame_outer = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_width, plate_length, frame_height)
frame_inner = Pos(0, 0, plate_thickness + frame_height/2) * Box(plate_width - 2*frame_thickness, plate_length - 2*frame_thickness, frame_height)
frame = frame_outer - frame_inner

boss = Pos(0, 0, plate_thickness + boss_height/2) * Box(boss_width, boss_length, boss_height)

combined = base + frame + boss

hole_r = hole_diameter / 2
hole_cyl = Cylinder(hole_r, hole_depth)
hole_z = plate_thickness + frame_height - hole_depth/2
for x in [-hole_spacing_x, 0, hole_spacing_x]:
    for y in [-hole_spacing_y, 0, hole_spacing_y]:
        combined = combined - Pos(x, y, hole_z) * hole_cyl

part = combined
part.name = "plate_with_frame_boss_and_holes"
export_step(part, "output.step")