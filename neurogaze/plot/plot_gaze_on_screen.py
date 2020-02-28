import seaborn as sns

from neurogaze.analyze import _get_screen_x_y


def plot_gaze_on_screen(df, show_progression=False, **plot_kwargs):
    cmap = sns.cubehelix_palette(as_cmap=True)

    df_without_nans = df[~df.left_gaze_point_on_display_area_x.isnull()]
    x, y = _get_screen_x_y(df_without_nans)

    if not plot_kwargs:
        plot_kwargs = {
            's': 1,
            'alpha': 0.1,
        }

    return sns.scatterplot(
        data=df_without_nans,
        x=x,
        y=y,
        # hue='utc_unix_timestamp',
        # cmap=cmap,
        edgecolor=None,
        **({
            'hue': 'utc_unix_timestamp',
            'cmap': cmap,
        } if show_progression else {}),
        **plot_kwargs,
    )
