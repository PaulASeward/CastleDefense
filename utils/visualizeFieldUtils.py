from utils.extractPlayDataUtils import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
import dateutil
from matplotlib.animation import FFMpegWriter
import warnings
warnings.filterwarnings('ignore')

# Constants for NFL field dimensions
NFL_FIELD_HEIGHT = 120
NFL_FIELD_WIDTH = 53.3

def plot_field_lines(ax, line_color='white'):
    """
    Generates the x and y coordinates for the field lines. Projects to the field width using next 10-yard line.
    Args:
        line_color: Color of the field lines, default white
        ax: Subplot to plot on

    Returns:
    """
    field_height = NFL_FIELD_HEIGHT  # need to rename the field_width variable done
    x_coord_lines = [0]
    y_coord_lines = [10]

    for i in range(10, int(field_height), 10):
        y_coord_lines.extend([i, i])
        i_base_10 = i // 10

        if i_base_10 % 2 != 0:  # Check if i_base_10 is odd
            x_coord_lines.extend([NFL_FIELD_WIDTH, 0])
        else:
            x_coord_lines.extend([0, NFL_FIELD_WIDTH])
    y_coord_lines.extend([field_height, 0, 0, field_height, field_height])
    x_coord_lines.extend(
        [x_coord_lines[-1], x_coord_lines[-1], x_coord_lines[-2], x_coord_lines[-2], x_coord_lines[-1]])

    return ax.plot(x_coord_lines, y_coord_lines, color=line_color)


def plot_endzones(ax):
    """
    Generates and plots the x and y coordinates for the field endzones. Projects to the field width using next 10-yard line.
    Args:
        ax: subplot to plot on
    """
    field_height = NFL_FIELD_HEIGHT
    # coloring not the lines
    endzone_bottom = patches.Rectangle((0, 0), NFL_FIELD_WIDTH, 10,
                                     linewidth=0.1,
                                     edgecolor='r',
                                     facecolor='blue',
                                     alpha=0.2,
                                     zorder=0)
    ax.add_patch(endzone_bottom)

    if field_height == 120:
        endzone_top = patches.Rectangle((0, 110), NFL_FIELD_WIDTH, 10,
                                          linewidth=0.1,
                                          edgecolor='r',
                                          facecolor='blue',
                                          alpha=0.2,
                                          zorder=0)
        ax.add_patch(endzone_top)
    return ax


def plot_hashmarks(ax, line_color='white'):
    """
    Generates and plots the x and y coordinates for the field hashmarks. Projects to the field width using next 10-yard line.
    Args:
        line_color: default white
        ax: subplot to plot on
    """
    field_height = NFL_FIELD_HEIGHT
    hash_range = range(11, int(field_height) - 10) if field_height == 120 else range(11, int(field_height))

    for x in hash_range:
        # At each eligible yard line, plot hash marks going vertically up the field.
        ax.plot([0.4, 0.7], [x, x], color=line_color)
        ax.plot([53.0, 52.5], [x, x], color=line_color)
        ax.plot([22.91, 23.57], [x, x], color=line_color)
        ax.plot([29.73, 30.39], [x, x], color=line_color)
    return ax


def plot_linenumbers(ax, line_color='white'):
    """
    Generates and plots the x and y coordinates for the field line numbers. Projects to the field width using next 10-yard line.
    Args:
        line_color: default white
        ax: subplot to plot on
    """
    field_height = NFL_FIELD_HEIGHT
    top_of_field = 110 if field_height == 120 else int(field_height)
    # Following loop creates line numbering.
    for x in range(20, top_of_field, 10):
        line_numb = x - 10
        if line_numb > 50:  # Past midfield (50 yd line: x=60), numbers are offset from 100
            line_numb = 100 - line_numb
        ax.text(5, x - 1.85, str(line_numb),
                horizontalalignment='center',
                fontsize=20,  # fontname='Arial',
                color=line_color, rotation=270)
        ax.text(NFL_FIELD_WIDTH - 5, x - 0.95, str(line_numb),
                horizontalalignment='center',
                fontsize=20,  # fontname='Arial',
                color=line_color, rotation=90)
    return ax


def create_football_field(boxed_view=None,
                          line_of_scrimmage=None,
                          yards_to_go=None,
                          v_padding=10,
                          h_padding=10,
                          field_color='darkgreen',
                          line_color='white'):
    """
    Creates a football field using matplotlib patches.
    Args:
        boxed_view: 4 tuple for the coordinate bounds of the field being displayed. Default is full view
        line_of_scrimmage: Providing a line of scrimmage will display a line of scrimmage marker
        yards_to_go: Yards to next 1st down marker. Will display a line for the yards to go
        v_padding: Adds vertical padding to the view
        h_padding: Adds horizontal padding to the view
        field_color: Default darkgreen
        line_color: Default white

    Returns:

    """
    if boxed_view is None:
        boxed_view = (0, 0, NFL_FIELD_WIDTH, NFL_FIELD_HEIGHT)

    x_max = max(10.0, min(NFL_FIELD_WIDTH, boxed_view[2]))  # clipping 10 < field_width < 120
    y_max = max(10.0, min(NFL_FIELD_HEIGHT, boxed_view[3]))  # clipping 10 < field_height < 53.3
    x_min = min(x_max - 10.0, max(0, boxed_view[0]))
    y_min = min(y_max - 10.0, max(0, boxed_view[1]))
    # field_height = y_max - y_min
    # field_width = x_max - x_min
    field_height = NFL_FIELD_HEIGHT  # Default to full field view since we are using sliding viewing window
    field_width = NFL_FIELD_WIDTH

    figsize = (field_width / 10, (field_height + 10) / 10)  # Allow larger vertical spacing for titles in figure
    fig, ax = plt.subplots(1, figsize=figsize)

    padded_field_boundary = patches.Rectangle((x_min-h_padding, y_min-v_padding),
                                              field_width + (2*h_padding), field_height + (2*v_padding), linewidth=0.1,
                                              edgecolor='r', facecolor='darkblue', alpha=0.2, zorder=0)

    out_of_bounds_boundary = patches.Rectangle((x_min, y_min), field_width, field_height,
                                               linewidth=0.1, edgecolor='r', facecolor=field_color, zorder=0)
    ax.add_patch(padded_field_boundary)
    ax.add_patch(out_of_bounds_boundary)

    plt.xlim(x_min - h_padding, x_max + h_padding)
    plt.ylim(y_min - v_padding, y_max + v_padding)
    plt.axis('off')

    plot_field_lines(ax, line_color=line_color)
    plot_endzones(ax)
    plot_linenumbers(ax, line_color=line_color)
    plot_hashmarks(ax, line_color=line_color)

    if line_of_scrimmage:
        hl = line_of_scrimmage + 10
        ax.plot([NFL_FIELD_WIDTH, 0], [hl, hl], color='yellow')
        ax.text(hl - 8, NFL_FIELD_HEIGHT - 3, 'L.O.S. ->', fontsize=10, color='yellow')

    if yards_to_go and line_of_scrimmage:
        fl = line_of_scrimmage + 10 + yards_to_go
        ax.plot([0, NFL_FIELD_WIDTH], [fl, fl], color='yellow')

    return fig, ax


def plot_player_locations(offense, defense, football, description=None, zoomed_view=True, plot_blockers=False):
    """
    Plots the player locations for a single play.
    Args:
        description: Description of the play
        offense: Home team data frame
        defense: Away team data frame
        football: Football data frame
        zoomed_view: Zooms in on the play
    """
    plt.close()
    play = get_play_by_id(offense['gameId'].iloc[0], offense['playId'].iloc[0])

    line_of_scrimmage, yards_to_go = get_los_details(play, offense)
    boxed_view = get_player_max_locations(offense, defense, football) if zoomed_view else None

    fig, ax = create_football_field(boxed_view=boxed_view, line_of_scrimmage=line_of_scrimmage, yards_to_go=yards_to_go,
                                    field_color='green', line_color='white')

    ht_name = offense['club'].iloc[0]
    at_name = defense['club'].iloc[0]
    gameId = offense['gameId'].iloc[0]
    playId = offense['playId'].iloc[0]

    title = f'{ht_name} vs. {at_name}: Game #{gameId} Play #{playId}'
    if description is not None:
        title += f' ({description})'

    offense.plot(x='y', y='x', kind='scatter', ax=ax, color='orangered', s=10, label=ht_name)
    defense.plot(x='y', y='x', kind='scatter', ax=ax, color='blue', s=10, label=at_name)
    football.plot(x='y', y='x', kind='scatter', ax=ax, color='brown', s=15, label='football')

    if plot_blockers:
        blockers_df = get_blocking_players(offense)
        plot_blocking_formation(ax, blockers_df, 'red')

    plt.title(title)
    plt.legend()
    plt.show()


def plot_play_events(playId, gameId, week, zoomed_view=False, plot_blockers=False):
    """
    Plots the discrete events for a single play as seperate diagrams.
    Args:
        playId: identifies the play and game
        gameId:
        week:
        zoomed_view: Zooms in on the play
        plot_blockers: Displays red line connnecting eligible blockers
    """
    # Load play dataframes
    offense, defense, football = load_play(playId, gameId, week)

    events = offense['event'].unique()
    events = [event for event in events if not pd.isna(event)]

    for event in events:
        off = offense[offense['event'] == event]
        df = defense[defense['event'] == event]
        ft = football[football['event'] == event]

        plot_player_locations(off, df, ft, description=event, zoomed_view=zoomed_view, plot_blockers=plot_blockers)


def plot_play_tracked_movements(playId, gameId, week, zoomed_view=False):
    """
     Plots the tracked movements from one play. This visualizes the path of each player that they travelled on a certain play.
    Args:
        playId: identifier for the play and game
        gameId:
        week:
        zoomed_view: Displays zoome in window of the play
    """
    # Load play dataframes
    offense, defense, football = load_play(playId, gameId, week)

    plot_player_locations(offense, defense, football, zoomed_view=zoomed_view)


def plot_blocking_formation(ax, blocker_df, line_color='red'):
    """
    Plots a line between eligble blockers resembling the blocking formation for a play.
    Args:
        ax: Matplotlib axis
        blocker_df: DataFrame with only the blocking players
        line_color: Color of the line.
    """
    blocker_df = blocker_df.sort_values(by=['y'], ascending=[True])

    for i in range(len(blocker_df) - 1):
        blocker = blocker_df.iloc[i]
        next_blocker = blocker_df.iloc[i + 1]

        if next_blocker is not None:
            ax.plot([blocker['y'], next_blocker['y']], [blocker['x'], next_blocker['x']], color=line_color)

    return ax


gameId, playId, week = 2022090800, 343, 1

# create_football_field(boxed_view=(0,0,80,NFL_FIELD_HEIGHT), line_of_scrimmage=10, yards_to_go=10)
# plt.show()

# plot_play_events(playId, gameId, week, plot_blockers=True)
# plot_play_tracked_movements(playId, gameId, week)

# anim = animate_player_movement(gameId=gameId, playId=playId, weekNumber=week, plot_blockers=True)
# save_animation(anim, 'animateOffense.mp4')
