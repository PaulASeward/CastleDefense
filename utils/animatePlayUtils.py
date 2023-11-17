from CastleDefense.utils.extractPlayDataUtils import *
from CastleDefense.utils.visualizeFieldUtils import *
import matplotlib.pyplot as plt
from matplotlib import animation
from matplotlib.animation import FFMpegWriter
import warnings

warnings.filterwarnings('ignore')


###################
# Animating PLayers Movement: https://www.kaggle.com/code/ar2017/nfl-big-data-bowl-2021-animating-players-movement
###################
def create_plot_statements_at_frameId(ax, frameId, team_df, team_color, plot_blockers=False):
    """
    Generate the plot statements for each player's location, velocity vector, jersey number, orientation for a given
    team at a specific integer timestep.
    Args:
        ax: Matplotlib axis
        frameId: Frame integer timestep of play
        team_df: DataFrame with only the players on a specific team
        team_color: Color of the circle representing the player
        plot_blockers: Whether to plot the blocking formation
    Returns:
        List of plotting statements
    """
    patch = []

    player_data = team_df.query('frameId == ' + str(frameId))
    play_direction = player_data['playDirection'].iloc[0]

    patch.extend(ax.plot(player_data['x'], player_data['y'], 'o', c=team_color, ms=13))

    if plot_blockers:
        blockers_df = get_blocking_players(team_df)
        patch.extend(create_plot_blocking_formation_statements(ax, frameId, blockers_df))

    for _, player in player_data.iterrows():
        jersey_number_text = ax.text(player['x'], player['y'], int(player['jerseyNumber']), va='center', ha='center',
                                     color='white', fontsize=10)

        # Rotate the text based on player's orientation
        player_orientation = player['o'] if play_direction == 'left' else player['o'] + 180
        jersey_number_text.set_rotation(player_orientation)
        patch.append(jersey_number_text)

        # Calculate and plot players' velocity vectors
        dx, dy = calculate_dx_dy(player['s'], player['dir'])
        patch.append(ax.arrow(player['x'], player['y'], dx, dy, color='grey', width=0.15, shape='full'))

    return patch


def animate_frameId(ax, frameId, offense, defense, football, plot_blockers=False):
    """
    Updates the animation at a specific timestep.
    Args:
        ax: Matplotlib axis
        frameId: integer timestep of play
        offense:
        defense:
        football:
        plot_blockers:
    """
    patch = []

    # Plot home players
    patch.extend(create_plot_statements_at_frameId(ax, frameId, offense, 'orangered', plot_blockers=plot_blockers))

    # Plot away players
    patch.extend(create_plot_statements_at_frameId(ax, frameId, defense, 'blue'))

    # Plot football
    football_data = football[football['frameId'] == frameId]
    patch.extend(ax.plot(football_data['x'], football_data['y'], 'D', c='brown', ms=10,
                         data=football_data['club']))

    return patch


def create_plot_blocking_formation_statements(ax, frameId, blockers_df, line_color='red'):
    """
    Creates the plot statements for the blocking formation.
    Args:
        ax: Matplotlib axis
        frameId: integer timestep of play
        blockers_df: DataFrame with only the blocking players
        line_color: Red is best for visibility
    """
    plot_statements = []
    blocker_df = blockers_df[blockers_df['frameId'] == frameId]
    blocker_df = blocker_df.sort_values(by=['y'], ascending=[True])

    for i in range(len(blocker_df) - 1):
        blocker = blocker_df.iloc[i]
        next_blocker = blocker_df.iloc[i + 1]

        if next_blocker is not None:
            plot_statements.extend(
                ax.plot([blocker['x'], next_blocker['x']], [blocker['y'], next_blocker['y']], color=line_color))

    return plot_statements


def save_animation(anim, animation_path):
    """
    May need ffmpeg installed and added to system PATH

    Saves the animation to a file.
    :param anim: An animation object from Matplot Animation Library
    :param animation_path:
    :return:
    """
    anim.save(animation_path, writer=FFMpegWriter(fps=10))
    return


def animate_play(playId, gameId, weekNumber, zoomed_view=False, plot_blockers=False, animation_path='animation.mp4'):
    """
    Animates the movement of players and the football for a given play.
    Args:
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
    offense, defense, football = load_play(playId, gameId, weekNumber)
    play = get_play_by_id(gameId, playId)

    boxed_view = get_player_max_locations(offense, defense,
                                          football) if zoomed_view else None  # Display view window size

    yardlineNumber, yardsToGo = get_los_details(play, offense)
    fig, ax = create_football_field(boxed_view=boxed_view, line_of_scrimmage=yardlineNumber, yards_to_go=yardsToGo)

    playDesc = play['playDescription'].item()
    plt.title(f'Game # {gameId} Play # {playId} \n {playDesc}')

    ims = [[]]
    frame_ids = list(np.arange(int(offense['frameId'].unique().min()), int(offense['frameId'].unique().max()) + 1))
    for frameId in frame_ids:
        patch = animate_frameId(ax, frameId, offense=offense, defense=defense, football=football, plot_blockers=plot_blockers)
        ims.append(patch)

    anim = animation.ArtistAnimation(fig, ims, repeat=False)
    save_animation(anim, animation_path)

    return anim


gameId, playId, week = 2022090800, 343, 1

# create_football_field(boxed_view=(0,0,80,NFL_FIELD_HEIGHT), line_of_scrimmage=10, yards_to_go=10)
# plt.show()

# plot_play_events(playId, gameId, week, plot_blockers=True)
# plot_play_tracked_movements(playId, gameId, week)

animate_play(playId=playId, gameId=gameId, weekNumber=week, plot_blockers=True, animation_path='animateOffense.mp4')
