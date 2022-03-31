include <BOSL/constants.scad>
use <BOSL/shapes.scad>
use <BOSL/transforms.scad>
use <BOSL/paths.scad>
use <BOSL/metric_screws.scad>

use <lazy.scad>
use <rounded_collar.scad>

$fn = 7;

difference_fudge = 0.01;
extrusion_fudge = 0.1;
wall_thickness = 2;

display_width = 54;
display_height = 22;
display_depth = 8;
display_x_offset = 6.5;

wire_x_offset_start = 12;
wire_x_offset_end = 4.5;
wire_stubs_height = 1;
wire_height = 13;

board_width = 67;
board_height = 29;
actual_board_depth = 1.6;
board_depth = actual_board_depth + wire_stubs_height;

corner_radius = 1;

profile_height = 7;
profile_base_width = 13;
profile_top_width = 7;
profile_tight_corner = 1;
profile_wide_corner = 2;
shoulder_height = 7;

support_depth = board_depth * 2.5 + wall_thickness;
metric_screw_size = 3;
screw_spread = display_height + profile_base_width * 1.15;

// round_rect_collar(interior_size=[display_width, display_height], top_width=5, base_width=12, collar_height=6, shoulder_height=4, inner_radius=1, outer_radius=4);

printit = true;
laser_cut = false;

if(printit) {
    if(laser_cut) {
        projection() printable();
    } else {
        printable();
    }
}
else {
    sevenSegCollar();

    tz(board_depth + wall_thickness)
    display();
}
 
module printable()
{
    print_split_z = wall_thickness + board_depth;

    top_half(z = print_split_z + difference_fudge)
    sevenSegCollar();

    translate([0, 100, 0])
    bottom_half(z = print_split_z - difference_fudge)
    sevenSegCollar();
}

module sevenSegCollar() {
    //render()
    difference()
    {
        round_rect_collar(interior_size=[display_width, display_height], 
            top_width=profile_top_width, base_width=profile_base_width, 
            collar_height=profile_height, shoulder_height=shoulder_height, 
            inner_radius=profile_tight_corner, outer_radius=profile_wide_corner, shoulder_radius=profile_tight_corner,
            corner_qual=27, profile_qual=11);

        tz(board_depth + wall_thickness)
        {
            display();
            
            yspread(n=2, l=screw_spread)
            screw(screwsize=metric_screw_size, screwlen=15,
                headsize=get_metric_socket_cap_diam(metric_screw_size), 
                headlen=get_metric_socket_cap_height(metric_screw_size) * 1.15
            );
        }
    }
}

module base_plate()
{
    translate([-display_width / 2 + board_width / 2 - display_x_offset, 0, 0])
    {
        color("green")
        translate([0, 0, -board_depth / 2])
        cuboid([board_width, board_height, board_depth]);
    }
}

module display()
{
    color("silver")
    tz(display_depth / 2)
    cuboid([display_width, display_height, display_depth]);

    base_plate();
    
    tx(-display_width / 2 + board_width / 2 - display_x_offset)
    {
        wire_width = wire_x_offset_start - wire_x_offset_end;
        wire_depth = board_depth * 5;
        
        color("red")
        txz(board_width / 2 - wire_width / 2 - wire_x_offset_end, -wire_depth / 2)
        cuboid([wire_width, wire_height, wire_depth]);
    }
}
