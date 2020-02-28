import matplotlib.pyplot as plt
import seaborn as sns


def plot_activity_strip(df, group_by='app_short'):
    fig = plt.figure(figsize=(18, 10))

    ax = sns.stripplot(
        x='time', y=group_by, data=df, marker='.',
        s=5,
    )
    ax.set_xlim([df.time.min(), df.time.max()])

    return fig
