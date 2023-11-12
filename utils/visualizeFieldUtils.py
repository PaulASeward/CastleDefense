import os.path

from CastleDefense.utils.extractPlayDataUtils import *
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
import dateutil
from matplotlib.animation import FFMpegWriter
import warnings
warnings.filterwarnings('ignore')


###################
# Create the field By:https://www.kaggle.com/code/ar2017/nfl-big-data-bowl-2021-animating-players-movement
###################
def create_football_field(linenumbers=True,
                          endzones=True,
                          highlight_line=False,
                          highlight_line_number=55,
                          highlight_first_down_line=False,
                          yards_to_go=10,
                          highlighted_name='Line of Scrimmage',
                          fifty_is_los=False,
                          figsize=(12, 6.33)):
    """
    Function that plots the football field for viewing plays.
    Allows for showing or hiding endzones.
    """
    rect = patches.Rectangle((0, 0), 120, 53.3, linewidth=0.1,
                             edgecolor='r', facecolor='darkgreen', zorder=0)

    fig, ax = plt.subplots(1, figsize=figsize)
    ax.add_patch(rect)

    plt.plot([10, 10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80,
              80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120, 120],
             [0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3,
              53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 53.3, 0, 0, 53.3],
             color='white')
    if fifty_is_los:
        plt.plot([60, 60], [0, 53.3], color='gold')
        plt.text(62, 50, '<- Player Yardline at Snap', color='gold')
    # Endzones
    if endzones:
        ez1 = patches.Rectangle((0, 0), 10, 53.3,
                                linewidth=0.1,
                                edgecolor='r',
                                facecolor='blue',
                                alpha=0.2,
                                zorder=0)
        ez2 = patches.Rectangle((110, 0), 120, 53.3,
                                linewidth=0.1,
                                edgecolor='r',
                                facecolor='blue',
                                alpha=0.2,
                                zorder=0)
        ax.add_patch(ez1)
        ax.add_patch(ez2)
    plt.xlim(0, 120)
    plt.ylim(-5, 58.3)
    plt.axis('off')
    if linenumbers:
        for x in range(20, 110, 10):
            numb = x
            if x > 50:
                numb = 120 - x
            plt.text(x, 5, str(numb - 10),
                     horizontalalignment='center',
                     fontsize=20,  # fontname='Arial',
                     color='white')
            plt.text(x - 0.95, 53.3 - 5, str(numb - 10),
                     horizontalalignment='center',
                     fontsize=20,  # fontname='Arial',
                     color='white', rotation=180)
    if endzones:
        hash_range = range(11, 110)
    else:
        hash_range = range(1, 120)

    for x in hash_range:
        ax.plot([x, x], [0.4, 0.7], color='white')
        ax.plot([x, x], [53.0, 52.5], color='white')
        ax.plot([x, x], [22.91, 23.57], color='white')
        ax.plot([x, x], [29.73, 30.39], color='white')

    if highlight_line:
        hl = highlight_line_number + 10
        plt.plot([hl, hl], [0, 53.3], color='yellow')
        plt.text(hl + 2, 50, '<- {}'.format(highlighted_name),
                 color='yellow')

    if highlight_first_down_line:
        fl = hl + yards_to_go
        plt.plot([fl, fl], [0, 53.3], color='yellow')
        # plt.text(fl + 2, 50, '<- {}'.format(highlighted_name),
        #         color='yellow')
    return fig, ax


def plot_tracked_movements(ht_df, at_df, ft_df, description=None):
    """
    Plots the tracked movements from available play data.
    :param description: Description of the play
    :param ht_df:
    :param at_df:
    :param ft_df:
    :return:
    """
    plt.close()
    play = get_play_by_id(ht_df['gameId'].iloc[0], ht_df['playId'].iloc[0])
    line_of_scrimmage, yards_to_go = get_los_details(play)
    fig, ax = create_football_field(highlight_line_number=line_of_scrimmage,
                                    highlight_line=True,
                                    highlight_first_down_line=True,
                                    yards_to_go=yards_to_go)

    ht_name = ht_df['club'].iloc[0]
    at_name = at_df['club'].iloc[0]

    ht_df.plot(x='x', y='y', kind='scatter', ax=ax, color='orange', s=30, label=ht_name)
    at_df.plot(x='x', y='y', kind='scatter', ax=ax, color='blue', s=30, label=at_name)
    ft_df.plot(x='x', y='y', kind='scatter', ax=ax, color='brown', s=30, label='football')

    gameId = ht_df['gameId'].iloc[0]
    playId = ht_df['playId'].iloc[0]

    title = f'{ht_name} vs. {at_name}: Game #{gameId} Play #{playId}'

    if description is not None:
        title += f' ({description})'

    plt.title(title)
    plt.legend()
    plt.show()


def plot_play_events(playId, gameId, week):
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

        plot_tracked_movements(ht, at, ft, event)


def plot_play_tracked_movements(playId, gameId, week):
    """
    Plots the tracked movements for a single play.
    :param playId:
    :param gameId:
    :param week:
    :return:
    """
    play_df = load_play_data(playId, gameId, week)
    team_1, team_2, football = load_teams_from_play(play_df)

    plot_tracked_movements(team_1, team_2, football)


###################
# Animating PLayers Movement: https://www.kaggle.com/code/ar2017/nfl-big-data-bowl-2021-animating-players-movement
###################
def animate_player_movement(playId, gameId, weekNumber):
    """
    Animates player movement for a specific play.
    :param weekNumber:
    :param playId:
    :param gameId:
    :return:
    """
    play_df = load_play_data(playId, gameId, weekNumber)
    playHome, playAway, playFootball = load_teams_from_play(play_df)
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

    fig, ax = create_football_field(highlight_line=True, highlight_line_number=yardlineNumber,
                                    highlight_first_down_line=True, yards_to_go=yardsToGo)
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
    Saves the animation to a file.
    :param anim:
    :param animation_path:
    :return:
    """
    # Install 'ffmpeg':
    #     If you don't already have 'ffmpeg' installed on your system, you can download it from the official website: https://www.ffmpeg.org/download.html
    #     Download and install 'ffmpeg' based on your operating system.
    #
    # Ensure 'ffmpeg' is in your system's PATH:
    #     After installing 'ffmpeg,' make sure it's added to your system's PATH so that Python can locate it. If it's not in your PATH, you may encounter the "No such file or directory" error.
    #
    # Restart your Python environment:
    #     If you installed 'ffmpeg' or modified your PATH settings, restart your Python environment (e.g., Jupyter Notebook, Python script, or IDE) to apply the changes.

    # video = anim.to_html5_video()
    # html = IPython.display.HTML(video)
    # display(html)
    # plt.close()

    # display(IPython_display.display_animation(anim))

    # Writer = animation.writers['ffmpeg']
    # writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
    # anim.save(animation_path, writer=writer)

    anim.save(animation_path, writer=FFMpegWriter(fps=10))
    return


gameId, playId, week = 2022090800, 343, 1

# plot_play_events(playId, gameId, week)
# # plot_play_tracked_movements(playId, gameId, week)

# anim = animate_player_movement(gameId=gameId, playId=playId, weekNumber=week)
# save_animation(anim, 'animate.mp4')
