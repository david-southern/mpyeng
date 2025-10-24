// $fn = Number of line segments used to generate a circle/arc/sphere
// - do not exceed 128
// - values divisible by 4 will produce an axis-aligned integer bounding box
// - $preview is set when previewing in OpenSCAD, but not when rendering or exporting
$fn = $preview ? 32 : 96;

$align_msg = false; // Suppress the BOSL2 alignment warning

epsilon = 0.01; // Small value to ensure proper subtraction
printer_fudge = 0.15;

prusa_core_one_max_bed_width = 250;
prusa_core_one_max_bed_depth = 220;
prusa_core_one_max_bed_height = 270;

// In practice, printing too close to the edges of the bed is not a good idea
printer_bed_edge_margin = 20;

max_print_width = prusa_core_one_max_bed_width - printer_bed_edge_margin;
max_print_depth = prusa_core_one_max_bed_depth - printer_bed_edge_margin;
max_print_height = prusa_core_one_max_bed_height - printer_bed_edge_margin;

landscape_paper_width =  279.4; // mm
landscape_paper_height = 215.9; // mm

wire_22ga_outer_diameter = 1.65;
wire_26ga_outer_diameter = 1.4;

function toPct(thingy) = thingy < 1 ? thingy : thingy / 100;