def _get_screen_x_y(df, width=None, height=None, drop_nans=True):
    if drop_nans:
        df = df[~df.left_gaze_point_on_display_area_x.isnull()]
    x = df.left_gaze_point_on_display_area_x
    y = 1 - df.left_gaze_point_on_display_area_y

    if width and height:
        x = (x * width).astype(int)
        y = (y * width).astype(int)

    return (x.reset_index(drop=True), y.reset_index(drop=True))
