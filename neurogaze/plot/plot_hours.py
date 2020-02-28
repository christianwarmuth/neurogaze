def plot_hours(grouped, column_name, **plot_kwargs):
    return (
        grouped
        .to_frame(column_name)
        .reset_index()
        .plot(x='time', y=column_name, kind='scatter', **plot_kwargs)
    )
