include <BOSL2/std.scad>
include <BOSL2/shapes3d.scad>
include <useful_stuff.scad>

seven_seg_color = "dodgerblue";
wall_thickness = 2;

/* [Print Properties] */
show_collar = false;
show_mock = false;

/* [Collar Properties] */
profile_height_above_display = 2; // 0.01

profile_base_width = 13; // [1:0.5:50]
profile_base_height = 11; // [1:0.5:50]

profile_top_pct = 80; // [10:0.5:100]

// Percentage of the profile height used for corner fillet
profile_corner_fillet_pct = 70; // [0:0.5:100]

// Percentage of the profile height used for edge fillet
profile_top_fillet_pct = 10; // [0:0.5:100]

// Height of the 'straight' portion of the collar that maintains the bottom collar size before
// narrowing to the top size, to accommodate the display's PCB, as a percentage of the PCB
// thickness
profile_shoulder_height_pct = 200; // [100:0.5:500]

punch_fudge = 0.2;

/* [Hidden] */
actual_display_width = 50.5;
actual_display_height = 22;
display_depth = 8;
// The displays are not centered on the PCB, they are 1.25mm to the left of center
display_center_offset = 1.25;

actual_board_width = 67;
actual_board_height = 29;
actual_board_depth = 1.6;

display_width = actual_display_width + punch_fudge * 2;
display_height = actual_display_height + punch_fudge * 2;
board_width = actual_board_width + punch_fudge * 2;
board_height = actual_board_height + punch_fudge * 2;
board_depth = actual_board_depth  + punch_fudge * 2;

seven_seg_collar_base_width = display_width + profile_base_width * 2;
seven_seg_collar_base_height = display_height + profile_base_height * 2;
collar_top_width = display_width + profile_base_width * toPct(profile_top_pct) * 2;
collar_top_height = display_height + profile_base_height * toPct(profile_top_pct) * 2;
seven_seg_collar_depth = display_depth + board_depth + profile_height_above_display;
collar_shoulder_depth = board_depth * toPct(profile_shoulder_height_pct);
collar_cone_depth = seven_seg_collar_depth - collar_shoulder_depth;

// The soldering vias are inset 6.5 mm from the right side of the board
wire_x_offset = 6.5;
wire_mock_length = board_depth * 3;
wire_mock_diameter = wire_26ga_outer_diameter;
// Spacing between the soldering vias, center-to-center
wire_spacing = 3;
wire_count = 4;

if(show_collar)
{
    render()
    seven_seg_collar(anchor=BOTTOM);
}

if(show_mock)
{
    seven_seg_display_mock(anchor=BOTTOM);
}

module seven_seg_collar(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[seven_seg_collar_base_width, seven_seg_collar_base_height, seven_seg_collar_depth]) 
    {
        render()
        down(seven_seg_collar_depth / 2)
        difference()
        {
            seven_seg_collar_blank(anchor=BOTTOM);
            seven_seg_display_punch(anchor=BOTTOM);
        }
        children();
    }

}

module seven_seg_collar_blank(anchor=CENTER, spin=0, orient=UP)
{
    attachable(anchor, spin, orient, size=[seven_seg_collar_base_width, seven_seg_collar_base_height, seven_seg_collar_depth]) 
    {
        render()
        color("white")
        difference()
        {
            down(seven_seg_collar_depth / 2)
            cuboid(
                [seven_seg_collar_base_width, seven_seg_collar_base_height, collar_shoulder_depth], 
                rounding = profile_base_height * toPct(profile_corner_fillet_pct),
                edges = "Z",
                anchor=BOTTOM)
            position(TOP)
                diff()
                prismoid(
                    [seven_seg_collar_base_width, seven_seg_collar_base_height],
                    [collar_top_width, collar_top_height],
                    h = collar_cone_depth,
                    rounding = profile_base_height * toPct(profile_corner_fillet_pct),
                    anchor=BOTTOM)
                {
                    edge_profile([TOP], excess=10, convexity=20)
                    {
                        mask2d_roundover(
                            h=collar_top_height * toPct(profile_top_fillet_pct), 
                            mask_angle=$edge_angle
                        );
                    }                
                };
        }
        children();
    }
}

module seven_seg_display_mock(anchor=CENTER, spin=0, orient=UP)
{
    mock_width = actual_board_width;
    mock_height = actual_board_height;
    mock_depth = display_depth + actual_board_depth;

    attachable(anchor, spin, orient, size=[mock_width, mock_height, mock_depth]) {
        recolor("silver")
        up(mock_depth / 2)
        left(display_center_offset)
        cuboid([actual_display_width, actual_display_height, display_depth], anchor=TOP)
        position(BOTTOM)
            recolor("green")
            right(display_center_offset)
            cuboid([actual_board_width, actual_board_height, actual_board_depth], anchor=TOP)
            position(BOTTOM + RIGHT)
                recolor("gray")
                left(wire_x_offset)
                up(actual_board_depth + 0.5)
                ycopies(wire_spacing, n=wire_count)
                cyl(l = actual_board_depth * 3, d = wire_mock_diameter, anchor=TOP);
        children();
    }
}


module seven_seg_display_punch(anchor=CENTER, spin=0, orient=UP)
{
    mock_width = board_width;
    mock_height = board_height;
    mock_depth = seven_seg_collar_depth + epsilon * 2;

    attachable(anchor, spin, orient, size=[mock_width, mock_height, mock_depth]) {
        color("white")
        up(mock_depth / 2)
        left(display_center_offset)
        cuboid(
            [display_width, display_height, mock_depth],
            rounding = -collar_top_height * toPct(profile_top_fillet_pct),
            edges = TOP,
            anchor=TOP
        )
        position(BOTTOM)
            right(display_center_offset)
            cuboid([board_width, board_height, board_depth], anchor=BOTTOM);
        children();
    }
}
