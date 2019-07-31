from math import atan, cos, tan

def get_verts(page_thickness, page_height, cover_depth, cover_height, cover_thickness, page_depth, hinge_inset, hinge_width, spine_curl):
    
    spine_angle = atan(spine_curl/cover_thickness)
    spine_offset_center = cover_thickness*cos(spine_angle)
    spine_offset_side = tan(spine_angle/2)*cover_thickness

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
        [(page_thickness / 2 + cover_thickness),                -page_depth / 2 - hinge_width / 2 - spine_offset_side ,              cover_height / 2],
        [(page_thickness / 2 + cover_thickness),                -page_depth / 2 - hinge_width / 2 - spine_offset_side,              -cover_height / 2],
        [(page_thickness / 2),                                  -page_depth / 2 - hinge_width / 2 ,                                  -cover_height / 2],
        [(page_thickness / 2),                                  -page_depth / 2 - hinge_width / 2,                                    cover_height / 2],
        [0.0,                                                   -cover_depth / 2 - spine_curl,                                      -cover_height / 2],
        [0.0,                                                   -cover_depth / 2 - spine_curl ,                                      cover_height / 2],
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
        [-(page_thickness / 2 + cover_thickness),                -page_depth / 2 - hinge_width / 2 - spine_offset_side,              cover_height / 2],
        [-(page_thickness / 2 + cover_thickness),                -page_depth / 2 - hinge_width / 2 - spine_offset_side,             -cover_height / 2],
        [-(page_thickness / 2),                                  -page_depth / 2 - hinge_width / 2 ,                                 -cover_height / 2],
        [-(page_thickness / 2),                                  -page_depth / 2 - hinge_width / 2,                                   cover_height / 2],
        [0.0,                                                   -cover_depth / 2 - spine_curl - spine_offset_center,                cover_height / 2],
        [0.0,                                                   -cover_depth / 2 - spine_curl - spine_offset_center,               -cover_height / 2],
    ]
