from CastleDefense.utils.extractPlayDataUtils import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
import dateutil
from matplotlib.animation import FFMpegWriter
import warnings
warnings.filterwarnings('ignore')

# Constants for NFL field dimensions
NFL_FIELD_HEIGHT = 53.3
NFL_FIELD_WIDTH = 120


def plot_field_lines(ax, line_color='white'):
    """
    Generates the x and y coordinates for the field lines. Projects to the field width using next 10-yard line.
    Args:
        line_color: Color of the field lines, default white
        ax: Subplot to plot on

    Returns:
    """
    field_width = NFL_FIELD_WIDTH
    x_coord_lines = [10]
    y_coord_lines = [0]

    for i in range(10, int(field_width), 10):
        x_coord_lines.extend([i, i])
        i_base_10 = i // 10

        if i_base_10 % 2 != 0:  # Check if i_base_10 is odd
            y_coord_lines.extend([0, NFL_FIELD_HEIGHT])
        else:
            y_coord_lines.extend([NFL_FIELD_HEIGHT, 0])

    x_coord_lines.extend([field_width, 0, 0, field_width, field_width])
    y_coord_lines.extend(
        [y_coord_lines[-1], y_coord_lines[-1], y_coord_lines[-2], y_coord_lines[-2], y_coord_lines[-1]])

    return ax.plot(x_coord_lines, y_coord_lines, color=line_color)


def plot_endzones(ax):
    """
    Generates and plots the x and y coordinates for the field endzones. Projects to the field width using next 10-yard line.
    Args:
        ax: subplot to plot on
    """
    field_width = NFL_FIELD_WIDTH

    endzone_left = patches.Rectangle((0, 0), 10, NFL_FIELD_HEIGHT,
                                     linewidth=0.1,
                                     edgecolor='r',
                                     facecolor='blue',
                                     alpha=0.2,
                                     zorder=0)
    ax.add_patch(endzone_left)

    if field_width == 120:
        endzone_right = patches.Rectangle((110, 0), 10, NFL_FIELD_HEIGHT,
                                          linewidth=0.1,
                                          edgecolor='r',
                                          facecolor='blue',
                                          alpha=0.2,
                                          zorder=0)
        ax.add_patch(endzone_right)
    return ax


def plot_hashmarks(ax, line_color='white'):
    """
    Generates and plots the x and y coordinates for the field hashmarks. Projects to the field width using next 10-yard line.
    Args:
        line_color: default white
        ax: subplot to plot on
    """
    field_width = NFL_FIELD_WIDTH
    hash_range = range(11, int(field_width) - 10) if field_width == 120 else range(11, int(field_width))

    for x in hash_range:
        # At each eligible yard line, plot hash marks going vertically up the field.
        ax.plot([x, x], [0.4, 0.7], color=line_color)
        ax.plot([x, x], [53.0, 52.5], color=line_color)
        ax.plot([x, x], [22.91, 23.57], color=line_color)
        ax.plot([x, x], [29.73, 30.39], color=line_color)
    return ax


def plot_linenumbers(ax, line_color='white'):
    """
    Generates and plots the x and y coordinates for the field line numbers. Projects to the field width using next 10-yard line.
    Args:
        line_color: default white
        ax: subplot to plot on
    """
    field_width = NFL_FIELD_WIDTH
    right_end_of_field = 110 if field_width == 120 else int(field_width)

    for x in range(20, right_end_of_field, 10):
        line_numb = x - 10
        if line_numb > 50:  # Past midfield (50 yd line: x=60), numbers are offset from 100
            line_numb = 100 - line_numb
        ax.text(x, 5, str(line_numb),
                horizontalalignment='center',
                fontsize=20,  # fontname='Arial',
                color=line_color)
        ax.text(x - 0.95, NFL_FIELD_HEIGHT - 5, str(line_numb),
                horizontalalignment='center',
                fontsize=20,  # fontname='Arial',
                color=line_color, rotation=180)
    return ax


def create_football_field(boxed_view=None,
                          line_of_scrimmage=None,
                          yards_to_go=None,
                          v_padding=0,
                          h_padding=0,
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
    x_min = min(x_max-10.0, max(0, boxed_view[0]))
    y_min = min(y_max-10.0, max(0, boxed_view[1]))
    field_height = y_max - y_min
    field_width = x_max - x_min

    figsize = (field_width / 10, (field_height + 10) / 10)  # Allow larger vertical spacing for titles in figure
    fig, ax = plt.subplots(1, figsize=figsize)

    padded_field_boundary = patches.Rectangle((x_min-h_padding, y_min-v_padding),
                                              field_width + (2*h_padding), field_height + (2*v_padding), linewidth=0.1,
                                              edgecolor='r', facecolor='lightgreen', alpha=0.2, zorder=0)

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
        ax.plot([hl, hl], [0, NFL_FIELD_HEIGHT], color='yellow')
        ax.text(hl - 8, NFL_FIELD_HEIGHT - 3, 'L.O.S. ->', fontsize=10, color='yellow')

    if yards_to_go and line_of_scrimmage:
        fl = line_of_scrimmage + 10 + yards_to_go
        ax.plot([fl, fl], [0, NFL_FIELD_HEIGHT], color='yellow')

    return fig, ax


def plot_tracked_movements(ht_df, at_df, ft_df, description=None, zoomed_view=True, plot_blockers=False):
    """
    Plots the tracked movements from available play data.

    :return:

    Args:
        description: Description of the play
        ht_df: Home team data frame
        at_df: Away team data frame
        ft_df: Football data frame
        zoomed_view: Zooms in on the play
    """
    plt.close()
    play = get_play_by_id(ht_df['gameId'].iloc[0], ht_df['playId'].iloc[0])

    line_of_scrimmage, yards_to_go = get_los_details(play)
    boxed_view = get_player_max_locations(ht_df, at_df, ft_df) if zoomed_view else None

    fig, ax = create_football_field(boxed_view=boxed_view, line_of_scrimmage=line_of_scrimmage, yards_to_go=yards_to_go, field_color='white', line_color='black')

    ht_name = ht_df['club'].iloc[0]
    at_name = at_df['club'].iloc[0]

    ht_df.plot(x='x', y='y', kind='scatter', ax=ax, color='orange', s=30, label=ht_name)
    at_df.plot(x='x', y='y', kind='scatter', ax=ax, color='blue', s=30, label=at_name)
    ft_df.plot(x='x', y='y', kind='scatter', ax=ax, color='brown', s=30, label='football')

    if plot_blockers:
        plot_blocking_formation(ax, ht_df, 'red')

    gameId = ht_df['gameId'].iloc[0]
    playId = ht_df['playId'].iloc[0]

    title = f'{ht_name} vs. {at_name}: Game #{gameId} Play #{playId}'

    if description is not None:
        title += f' ({description})'

    plt.title(title)
    plt.legend()
    plt.show()


def plot_play_events(playId, gameId, week, zoomed_view=False, plot_blockers=False):
    """
    Plots all events for a single play.
    :param playId:
    :param gameId:
    :param week:
    :return:
    """
    play_df = load_play_data(playId, gameId, week)
    team_1, team_2, football = load_teams_from_play(play_df)

    events = play_df['event'].unique()
    events = [event for event in events if not pd.isna(event)]

    for event in events:
        ht = team_1[team_1['event'] == event]
        at = team_2[team_2['event'] == event]
        ft = football[football['event'] == event]

        plot_tracked_movements(ht, at, ft, description=event, zoomed_view=zoomed_view, plot_blockers=plot_blockers)


def plot_play_tracked_movements(playId, gameId, week, zoomed_view=False):
    """
    Plots the tracked movements for a single play.
    :param playId:
    :param gameId:
    :param week:
    :return:
    """
    play_df = load_play_data(playId, gameId, week)
    team_1, team_2, football = load_teams_from_play(play_df)

    plot_tracked_movements(team_1, team_2, football, zoomed_view=zoomed_view)


def plot_blocking_formation(ax, ht_df, line_color):
    blocker_df = get_blocking_players(ht_df)
    blocker_df = blocker_df.sort_values(by=['y'], ascending=[True])

    for i in range(len(blocker_df) - 1):
        blocker = blocker_df.iloc[i]
        next_blocker = blocker_df.iloc[i + 1]

        if next_blocker is not None:
            ax.plot([blocker['x'], next_blocker['x']], [blocker['y'], next_blocker['y']], color=line_color)

    return ax

###################
# Animating PLayers Movement: https://www.kaggle.com/code/ar2017/nfl-big-data-bowl-2021-animating-players-movement
###################
def animate_player_movement(playId, gameId, weekNumber, zoomed_view=False):
    """
    Animates player movement for a specific play.
    :param weekNumber:
    :param playId:
    :param gameId:
    :return:
    """
    play_df = load_play_data(playId, gameId, weekNumber)
    playHome, playAway, playFootball = load_teams_from_play(play_df)
    boxed_view = get_player_max_locations(playHome, playAway, playFootball) if zoomed_view else None

    play = get_play_by_id(gameId, playId)

    playHome['time'] = playHome['time'].apply(lambda x: dateutil.parser.parse(x).timestamp()).rank(method='dense')
    playAway['time'] = playAway['time'].apply(lambda x: dateutil.parser.parse(x).timestamp()).rank(method='dense')
    playFootball['time'] = playFootball['time'].apply(lambda x: dateutil.parser.parse(x).timestamp()).rank(
        method='dense')

    maxTime = int(playAway['time'].unique().max())
    minTime = int(playAway['time'].unique().min())
    playDir = playHome.sample(1)['playDirection'].item()

    yardlineNumber, yardsToGo = get_los_details(play)
    absoluteYardlineNumber = play['absoluteYardlineNumber'].item() - 10

    if (absoluteYardlineNumber > 50):
        yardlineNumber = 100 - yardlineNumber
    if (absoluteYardlineNumber <= 50):
        yardlineNumber = yardlineNumber

    if (playDir == 'left'):
        yardsToGo = -yardsToGo
    else:
        yardsToGo = yardsToGo

    fig, ax = create_football_field(boxed_view=boxed_view, line_of_scrimmage=yardlineNumber, yards_to_go=yardsToGo)

    playDesc = play['playDescription'].item()
    plt.title(f'Game # {gameId} Play # {playId} \n {playDesc}')

    def update_animation(time):
        patch = []

        # Home players' location
        homeX = playHome.query('time == ' + str(time))['x']
        homeY = playHome.query('time == ' + str(time))['y']
        homeNum = playHome.query('time == ' + str(time))['jerseyNumber']
        homeOrient = playHome.query('time == ' + str(time))['o']
        homeDir = playHome.query('time == ' + str(time))['dir']
        homeSpeed = playHome.query('time == ' + str(time))['s']
        patch.extend(plt.plot(homeX, homeY, 'o', c='gold', ms=20, mec='white'))

        # Home players' jersey number
        for x, y, num in zip(homeX, homeY, homeNum):
            patch.append(plt.text(x, y, int(num), va='center', ha='center', color='black', size='medium'))

        # Home players' orientation
        for x, y, orient in zip(homeX, homeY, homeOrient):
            dx, dy = calculate_dx_dy(x, y, orient, 1, 1)
            patch.append(plt.arrow(x, y, dx, dy, color='gold', width=0.5, shape='full'))

        # Home players' direction
        for x, y, direction, speed in zip(homeX, homeY, homeDir, homeSpeed):
            dx, dy = calculate_dx_dy(x, y, direction, speed, 1)
            patch.append(plt.arrow(x, y, dx, dy, color='black', width=0.25, shape='full'))

        # Away players' location
        awayX = playAway.query('time == ' + str(time))['x']
        awayY = playAway.query('time == ' + str(time))['y']
        awayNum = playAway.query('time == ' + str(time))['jerseyNumber']
        awayOrient = playAway.query('time == ' + str(time))['o']
        awayDir = playAway.query('time == ' + str(time))['dir']
        awaySpeed = playAway.query('time == ' + str(time))['s']
        patch.extend(plt.plot(awayX, awayY, 'o', c='orangered', ms=20, mec='white'))

        # Away players' jersey number
        for x, y, num in zip(awayX, awayY, awayNum):
            patch.append(plt.text(x, y, int(num), va='center', ha='center', color='white', size='medium'))

        # Away players' orientation
        for x, y, orient in zip(awayX, awayY, awayOrient):
            dx, dy = calculate_dx_dy(x, y, orient, 1, 1)
            patch.append(plt.arrow(x, y, dx, dy, color='orangered', width=0.5, shape='full'))

        # Away players' direction
        for x, y, direction, speed in zip(awayX, awayY, awayDir, awaySpeed):
            dx, dy = calculate_dx_dy(x, y, direction, speed, 1)
            patch.append(plt.arrow(x, y, dx, dy, color='black', width=0.25, shape='full'))

        # Footballs' location
        football_data = playFootball.query('time == ' + str(time))['club']
        footballX = playFootball.query('time == ' + str(time))['x']
        footballY = playFootball.query('time == ' + str(time))['y']
        patch.extend(plt.plot(footballX, footballY, 'o', c='black', ms=10, mec='white',
                              data=football_data))

        return patch

    ims = [[]]
    for time in np.arange(minTime, maxTime + 1):
        patch = update_animation(time)
        ims.append(patch)

    anim = animation.ArtistAnimation(fig, ims, repeat=False)

    return anim


def save_animation(anim, animation_path):
    """
    May need ffmpeg installed and added to system PATH

    Saves the animation to a file.
    :param anim:
    :param animation_path:
    :return:
    """
    anim.save(animation_path, writer=FFMpegWriter(fps=10))
    return


gameId, playId, week = 2022090800, 343, 1

# create_football_field(boxed_view=(0,0,80,NFL_FIELD_HEIGHT), line_of_scrimmage=10, yards_to_go=10)
# plt.show()

plot_play_events(playId, gameId, week, plot_blockers=True)
# plot_play_tracked_movements(playId, gameId, week)

# anim = animate_player_movement(gameId=gameId, playId=playId, weekNumber=week)
# save_animation(anim, 'animate.mp4')
