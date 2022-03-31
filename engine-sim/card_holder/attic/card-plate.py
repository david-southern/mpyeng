# jupyter_cadquery source location:
# C:\Users\david\miniconda3\envs\jcq3\Lib\site-packages\jupyter_cadquery

import cadquery as cq
from jupyter_cadquery import ( set_defaults, Part )

from jupyter_cadquery.viewer.client import show

from jupyter_cadquery.export import exportSTL

exportObject = False

difference_fudge = 0.1
extrusion_fudge = 0.1

acrylic_thickness = 3.25

mag_diam = 8 + extrusion_fudge * 2
mag_thickness = 3 - extrusion_fudge

frame_xside_width = 12
frame_yside_width = 14
frame_extra_thickness = 3
mag_frame_offset = 4
acrylic_depth = 2

frame_overlap = 2

card_width = 54
card_height = 81
card_thickness = acrylic_thickness

frame_width = card_width + (frame_xside_width - frame_overlap) * 2
frame_height = card_height+ (frame_yside_width - frame_overlap) * 2
frame_depth = frame_extra_thickness + acrylic_thickness
corner_fillet = 2

exportResult = None

def initialize():
    set_defaults(
        axes=True,axes0=True,grid=[True, False, False],ortho=False,
        control="orbit",default_color=(176, 36, 176),default_edge_color="#0000ff",
        tree_width=250,timeit=False,ticks=5,
    )

def card_frame():
    spread_height = frame_height - mag_diam - mag_frame_offset
    spread_width = frame_width - mag_diam - mag_frame_offset

    result = cq.Workplane().box(frame_width, frame_height, frame_depth)

    view_cutout_width = card_width - frame_overlap * 2
    view_cutout_height = card_height - frame_overlap * 2
    view_cutout_depth = frame_depth * 2

    view_cutout = cq.Workplane().box(view_cutout_width, view_cutout_height, view_cutout_depth)
    result = result.cut(view_cutout)

    acrylic_center_amount = (frame_depth - acrylic_depth) / 2

    result = (
        result.edges("|Z").fillet(corner_fillet)
        .faces("<Z").workplane(invert=True).tag("baseplane")
        .rect(card_width, card_height).cutBlind(acrylic_depth + acrylic_center_amount)
        .workplaneFromTagged("baseplane")
    )


        # color("silver")
        # translate([0, 0, -(frame_depth - mag_thickness + difference_fudge) / 2])
        # {
        #     translate([0, spread_height / 2, 0])
        #     xspread(spacing=spread_width, l=spread_width) {
        #         cyl(l=mag_thickness +  + difference_fudge, d=mag_diam);
        #     }
            
        #     translate([0, -spread_height / 2, 0])
        #     xspread(spacing=spread_width / 6, l=spread_width) {
        #         cyl(l=mag_thickness + difference_fudge, d=mag_diam);
        #     }
           

    # result = (cq.Workplane("XY")
    #     .box(length, height, thickness)
    #     .faces(">Z").workplane().center(length / 3, 0).hole(height / 3)
    #     .edges("|Z").fillet(thickness / 5)
    # )

    cv = show(
        result,
        position=(0.2, -3.4, 7.6),
        zoom=1
    )

initialize()
card_frame()

if(exportObject and exportResult is not None):
    exportSTL(Part(exportResult), "result.stl", tolerance=0.1, angular_tolerance=0.1)
