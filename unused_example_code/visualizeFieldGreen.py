import matplotlib.pyplot as plt
import matplotlib.patches as patches
from CastleDefense.utils.extractPlayDataUtils import *
from CastleDefense.utils.visualizeFieldUtils import *
from CastleDefense.utils.animatePlayUtils import *
from matplotlib.markers import MarkerStyle
from matplotlib import animation
from matplotlib.animation import FFMpegWriter, FuncAnimation
import warnings
warnings.filterwarnings('ignore')

WINDOW_DISPLAY_SIZE = 6


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
                          figsize=(12, 6.33)):
    """
    Function that plots the football field for viewing plays.
    Allows for showing or hiding endzones.
    """
    # plt.close()
    rect = patches.Rectangle((0, 0), 120, 53.3, linewidth=0.1,
                             edgecolor='r', facecolor='darkgreen', zorder=0)

    # TODO: Can we make the figure size have dynamic proportions to the field in view?
    fig, ax = plt.subplots(1, figsize=figsize)

    plt.xlim(0, 120)
    plt.ylim(-5, 58.3)
    plt.axis('off')

    ax.add_patch(rect)

    ax.plot(
        [10, 10, 10, 20, 20, 30, 30, 40, 40, 50, 50, 60, 60, 70, 70, 80, 80, 90, 90, 100, 100, 110, 110, 120, 0, 0, 120,
         120],
        [0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3, 0, 0, 53.3, 53.3,
         53.3, 0, 0, 53.3],
        color='white')

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

    if linenumbers:
        for x in range(20, 110, 10):
            numb = x
            if x > 50:
                numb = 120 - x
            ax.text(x, 5, str(numb - 10),
                    horizontalalignment='center',
                    fontsize=20,  # fontname='Arial',
                    color='white')
            ax.text(x - 0.95, 53.3 - 5, str(numb - 10),
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


# DEPRECATED
def animate_play(playId, gameId, weekNumber, zoomed_view=False, plot_blockers=False,
                 display_position=False, animation_path='animation.mp4'):
    """
    Original and limited animated function. Does not allow for centering on the football or zooming out.
    Animates the movement of players and the football for a given play.
    Args:
        display_position: Default is jersey number
        playId: Play Id to identify the play
        gameId: Game Id to identify the game
        weekNumber:
        zoomed_view: Only displays the zoomed in view of the play. This window is generated dynamically based on how
        far the players move.
        plot_blockers: Whether to plot the blocking formation. This is red line between the eligible blockers.
        animation_path: Default
    Returns:
        An animation object. This is generated from Matplotlib's animation library. The helper methods generates list
        of plotting statements with specific details such as location, jersey number, orientation, and velocity vector.
    """
    # Load play dataframes
    plt.close()
    offense, defense, football = load_play(playId, gameId, weekNumber)
    play = get_play_by_id(gameId, playId)
    yardlineNumber, yardsToGo = get_los_details(play, offense)

    # Display window
    boxed_view = get_player_max_locations(offense, defense, football) if zoomed_view else None

    # Assign player display identifier
    offense, defense = assign_player_display_identifier(offense, defense, display_position=display_position)

    # Create field to animate upon
    fig, ax = create_football_field(boxed_view=boxed_view, line_of_scrimmage=yardlineNumber, yards_to_go=yardsToGo)

    # Add title from description
    playDesc = play['playDescription'].item()
    plt.title(f'Game # {gameId} Play # {playId} \n {playDesc}')

    # Animate each frame on plotted field
    ims = [[]]
    frame_ids = list(np.arange(int(offense['frameId'].unique().min()), int(offense['frameId'].unique().max()) + 1))
    for frameId in frame_ids:
        patch = animate_frameId(ax, frameId, offense=offense, defense=defense, football=football,
                                plot_blockers=plot_blockers)
        ims.append(patch)

    # Generate animation file and save
    anim = animation.ArtistAnimation(fig, ims, repeat=False)
    save_animation(anim, animation_path)

    return anim

# create_football_field()
# plt.show()
#
# animate_play(playId=playId, gameId=gameId, weekNumber=week, plot_blockers=False,
#                   animation_path='animateFuncOffense.mp4')