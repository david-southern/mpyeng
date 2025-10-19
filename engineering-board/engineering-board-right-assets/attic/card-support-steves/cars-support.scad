include <BOSL2/std.scad>
use <lazy.scad>

$fn = 83;

card_tray_width = 90;
card_tray_height = 120;
card_tray_thickness = 3;
card_rim_thickness = 9;
card_wall_width = 7;

card_height = card_tray_height - card_wall_width;
card_waist_height = 70;
card_width = card_tray_width - card_wall_width * 2;
card_waist_start = (card_height - card_waist_height - card_wall_width * 2) / 2;

card_tray_x_0 = 0;
card_tray_x_1 = card_wall_width;
card_tray_x_2 = card_wall_width * 2;
card_tray_x_3 = card_tray_width - card_wall_width * 2;
card_tray_x_4 = card_tray_width - card_wall_width;
card_tray_x_5 = card_tray_width;

card_tray_y_0 = 0;
card_tray_y_1 = card_wall_width;
card_tray_y_2 = card_wall_width + card_waist_start;
card_tray_y_3 = card_wall_width + card_waist_start + card_wall_width;
card_tray_y_4 = card_wall_width + card_waist_start + card_wall_width + card_waist_height;
card_tray_y_5 = card_wall_width + card_waist_start + card_wall_width + card_waist_height + card_wall_width;
card_tray_y_6 = card_tray_height;

epsilon = 0.01; // Small value to ensure proper subtraction

difference()
{
    // Outer tray
    color("lightgrey")
    card_outer_tray();

    // Inner tray
    tz(-epsilon)
    scale([1, 1, 10])
    card_inner_tray();
}
card_inner_tray();

* pixel_support();

echo(card_height = card_height);
echo(card_waist_height = card_waist_height);
echo(card_waist_start = card_waist_start);
echo(card_width = card_width);

module card_inner_tray()
{
    linear_extrude(height=card_tray_thickness)
    polygon([
        [card_tray_x_1, card_tray_y_1],
        [card_tray_x_4, card_tray_y_1],
        [card_tray_x_4, card_tray_y_2],
        [card_tray_x_3, card_tray_y_3],
        [card_tray_x_3, card_tray_y_4],
        [card_tray_x_4, card_tray_y_5],
        [card_tray_x_4, card_tray_y_6],
        [card_tray_x_1, card_tray_y_6],
        [card_tray_x_1, card_tray_y_5],
        [card_tray_x_2, card_tray_y_4],
        [card_tray_x_2, card_tray_y_3],
        [card_tray_x_1, card_tray_y_2]
    ]);
}

module card_outer_tray()
{
    linear_extrude(height=card_rim_thickness)
    polygon([
        [card_tray_x_0, card_tray_y_0],
        [card_tray_x_2, card_tray_y_0],
        [card_tray_x_2, card_tray_y_1],
        [card_tray_x_3, card_tray_y_1],
        [card_tray_x_3, card_tray_y_0],
        [card_tray_x_5, card_tray_y_0],
        [card_tray_x_5, card_tray_y_2],
        [card_tray_x_4, card_tray_y_3],
        [card_tray_x_4, card_tray_y_4],
        [card_tray_x_5, card_tray_y_5],
        [card_tray_x_5, card_tray_y_6],
        [card_tray_x_0, card_tray_y_6],
        [card_tray_x_0, card_tray_y_5],
        [card_tray_x_1, card_tray_y_4],
        [card_tray_x_1, card_tray_y_3],
        [card_tray_x_0, card_tray_y_2]
    ]);
}

pixel_grid_size = 5;
pixel_cell_size = 5;
pixel_cell_depth = 1.7;

intra_pixel_spacing = 11.5;
bend_allowance = 1;
bend_bar_height = 1;
pixel_cell_spacing = pixel_cell_size + intra_pixel_spacing - bend_bar_height * 2;
bend_bar_width = pixel_cell_spacing - pixel_cell_size - bend_allowance * 2;

strip_width = 10;
strip_separator_width = pixel_cell_spacing - strip_width - bend_allowance * 2;
strip_pin_width = 1.7;
strip_pin_spacing = 3;

echo(str("Pixel Cell Spacing: ", pixel_cell_spacing));

module pixel_grid() {
    color("pink")
    xcopies(pixel_cell_spacing, pixel_grid_size)
    {
        ycopies(pixel_cell_spacing, pixel_grid_size)
        {
            cube([pixel_cell_size, pixel_cell_size, pixel_cell_depth], center=true);
        }
    }
}

module pixel_support(){
    difference()
    {
        union()
        {
            difference()
            {
                cube([pixel_cell_spacing * pixel_grid_size, pixel_cell_spacing * pixel_grid_size, pixel_cell_depth], anchor = BOTTOM);
                scale([1, 1, 10])
                pixel_grid();
            }

            difference()
            {
                cube([
                    pixel_cell_spacing * pixel_grid_size + strip_width * 2, 
                    pixel_cell_spacing * pixel_grid_size + strip_width * 2, 
                    pixel_cell_depth * 2
                ], anchor = BOTTOM);
                tz(-epsilon)
                cube([
                    pixel_cell_spacing * pixel_grid_size, 
                    pixel_cell_spacing * pixel_grid_size, 
                    pixel_cell_depth * 10
                ], anchor = BOTTOM);
            }

            color("lightblue")
            tz(pixel_cell_depth)
            ycopies(pixel_cell_spacing, pixel_grid_size + 1)
            cube([
                pixel_cell_spacing * pixel_grid_size + strip_width, 
                bend_bar_width,
                bend_bar_height
            ], anchor = BOTTOM);

            color("pink")
            tz(pixel_cell_depth)
            xcopies(pixel_cell_spacing, pixel_grid_size + 1)
            cube([
                strip_separator_width,
                pixel_cell_spacing * pixel_grid_size + strip_width, 
                bend_bar_height
            ], anchor = BOTTOM);
        }

        tz(pixel_cell_depth + epsilon)
        ycopies(pixel_cell_spacing, pixel_grid_size)
        pixel_lock_bar();

        intersection()
        {
            strips(strip_width + 2);
            cube([
                pixel_cell_spacing * pixel_grid_size, 
                pixel_cell_spacing * pixel_grid_size, 
                pixel_cell_depth * 10
            ], anchor = BOTTOM);
        }
    }
}

module pixel_lock_bar()
{
    color("blue")
    cube([
        pixel_cell_spacing * pixel_grid_size + strip_width, 
        pixel_cell_size,
        bend_bar_height * 2
    ], anchor = BOTTOM);
}

strip_seg_length = pixel_cell_size + bend_allowance * 2 + bend_bar_width;
strip_seg_thickness = 1;

module strips(seg_width = strip_width)
{
    xcopies(pixel_cell_spacing, pixel_grid_size)
    translate([
        -seg_width / 2,
        -pixel_cell_size / 2 - bend_allowance,
        pixel_cell_depth + strip_seg_thickness / 2
    ])
    ycopies(strip_seg_length, 5)
    strip_segment(seg_width);
}

module strip_segment(seg_width = strip_width)
{
    echo(str("Seg Width: ", seg_width));
    bent_path = [
        [0, 0], 
        [0 + pixel_cell_size, 0], 
        [0 + pixel_cell_size + bend_allowance / 2, bend_bar_height], 
        [0 + pixel_cell_size + bend_allowance / 2 + bend_bar_width, bend_bar_height], 
        [0 + pixel_cell_size + bend_allowance + bend_bar_width, 0], 
    ];

    path = [
        [0, bend_bar_height],
        [bend_allowance, 0], 
        [bend_allowance + pixel_cell_size, 0],
        [bend_allowance + pixel_cell_size + bend_allowance, bend_bar_height], 
        [bend_allowance + pixel_cell_size + bend_allowance + bend_bar_width, bend_bar_height], 
    ];

    color("red")
    rx(90)
    ry(90)
    linear_extrude(height=seg_width)
    stroke(path, width=strip_seg_thickness);
}