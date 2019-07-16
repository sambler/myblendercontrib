from math import atan, cos, tan

def get_verts(page_thickness, page_height, cover_depth, cover_height, cover_thickness, page_depth, hinge_inset, hinge_width, spline_curl):
    
    spline_angle = atan(spline_curl/cover_thickness)
    spline_offset_center = cover_thickness/cos(spline_angle)
    spline_offset_side = tan(spline_angle/2)*cover_thickness

    return [
        # textblock
        [- page_thickness / 2, page_depth / 2, -page_height / 2],
        [- page_thickness / 2, page_depth / 2, page_height / 2],
        [ page_thickness / 2, page_depth / 2, -page_height / 2],
        [ page_thickness / 2, page_depth / 2, page_height / 2],
        [- page_thickness / 2, -page_depth / 2, -page_height / 2],
        [- page_thickness / 2, -page_depth / 2, page_height / 2],
        [ page_thickness / 2, -page_depth / 2, -page_height / 2],
        [ page_thickness / 2, -page_depth / 2, page_height / 2],

        #left cover
        [page_thickness / 2 ,                                    cover_depth / 2,                                                    -cover_height / 2],
        [page_thickness / 2,                                     cover_depth / 2,                                                     cover_height / 2],
        [(page_thickness / 2 + cover_thickness),                 cover_depth / 2,                                                    -cover_height / 2],
        [(page_thickness / 2 + cover_thickness),                 cover_depth / 2,                                                     cover_height / 2],

        [(page_thickness / 2 ),                                 -page_depth / 2 + hinge_width / 2,                                   -cover_height / 2],
        [(page_thickness / 2 ),                                 -page_depth / 2 + hinge_width / 2,                                    cover_height / 2],
        [(page_thickness / 2 + cover_thickness),                -page_depth / 2 + hinge_width / 2,                                   -cover_height / 2],
        [(page_thickness / 2 + cover_thickness),                -page_depth / 2 + hinge_width / 2,                                    cover_height / 2],
        [(page_thickness / 2 + cover_thickness- hinge_inset),   -page_depth / 2 ,                                                     cover_height / 2],
        [(page_thickness / 2 + cover_thickness- hinge_inset),   -page_depth / 2 ,                                                    -cover_height / 2],
        [(page_thickness / 2 ),                                 -page_depth / 2 ,                                                    -cover_height / 2],
        [(page_thickness / 2 ),                                 -page_depth / 2 ,                                                     cover_height / 2],
        [(page_thickness / 2 + cover_thickness),                -page_depth / 2 - hinge_width / 2 - spline_offset_side ,              cover_height / 2],
        [(page_thickness / 2 + cover_thickness),                -page_depth / 2 - hinge_width / 2 - spline_offset_side,              -cover_height / 2],
        [(page_thickness / 2),                                  -page_depth / 2 - hinge_width / 2 ,                                  -cover_height / 2],
        [(page_thickness / 2),                                  -page_depth / 2 - hinge_width / 2,                                    cover_height / 2],
        [0.0,                                                   -cover_depth / 2 - spline_curl,                                      -cover_height / 2],
        [0.0,                                                   -cover_depth / 2 - spline_curl ,                                      cover_height / 2],
        #right cover
        [-page_thickness / 2 ,                                    cover_depth / 2,                                                   -cover_height / 2],
        [-page_thickness / 2,                                     cover_depth / 2,                                                    cover_height / 2],
        [-(page_thickness / 2 + cover_thickness),                 cover_depth / 2,                                                   -cover_height / 2],
        [-(page_thickness / 2 + cover_thickness),                 cover_depth / 2,                                                    cover_height / 2],

        [-(page_thickness / 2 ),                                 -page_depth / 2 + hinge_width / 2,                                  -cover_height / 2],
        [-(page_thickness / 2 ),                                 -page_depth / 2 + hinge_width / 2,                                   cover_height / 2],
        [-(page_thickness / 2 + cover_thickness),                -page_depth / 2 + hinge_width / 2,                                  -cover_height / 2],
        [-(page_thickness / 2 + cover_thickness),                -page_depth / 2 + hinge_width / 2,                                   cover_height / 2],
        [-(page_thickness / 2 + cover_thickness- hinge_inset),   -page_depth / 2 ,                                                    cover_height / 2],
        [-(page_thickness / 2 + cover_thickness- hinge_inset),   -page_depth / 2 ,                                                   -cover_height / 2],
        [-(page_thickness / 2 ),                                 -page_depth / 2 ,                                                   -cover_height / 2],
        [-(page_thickness / 2 ),                                 -page_depth / 2 ,                                                    cover_height / 2],
        [-(page_thickness / 2 + cover_thickness),                -page_depth / 2 - hinge_width / 2 - spline_offset_side,              cover_height / 2],
        [-(page_thickness / 2 + cover_thickness),                -page_depth / 2 - hinge_width / 2 - spline_offset_side,             -cover_height / 2],
        [-(page_thickness / 2),                                  -page_depth / 2 - hinge_width / 2 ,                                 -cover_height / 2],
        [-(page_thickness / 2),                                  -page_depth / 2 - hinge_width / 2,                                   cover_height / 2],
        [0.0,                                                   -cover_depth / 2 - spline_curl - spline_offset_center,                cover_height / 2],
        [0.0,                                                   -cover_depth / 2 - spline_curl - spline_offset_center,               -cover_height / 2],
    ]
