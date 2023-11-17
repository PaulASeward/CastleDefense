from CastleDefense.utils.extractPlayDataUtils import *
from CastleDefense.utils.visualizeFieldUtils import *
import matplotlib.pyplot as plt
from matplotlib import animation
import dateutil
from matplotlib.animation import FFMpegWriter
import warnings

warnings.filterwarnings('ignore')


###################
# Animating PLayers Movement: https://www.kaggle.com/code/ar2017/nfl-big-data-bowl-2021-animating-players-movement
###################
def plot_players_at_timestep(ax, time, team_df, team_color, plot_blockers=False):
    """
    Generate the plot statements for each player's location, velocity vector, jersey number, orientation for a given team at a specific timestep.
    Args:
        ax: Matplotlib axis
        time: Timestep of play
        team_df: DataFrame with only the players on a specific team
        team_color: Color of the circle representing the player
        plot_blockers: Whether to plot the blocking formation

    Returns:
        List of plotting statements
    """
    patch = []

    player_data = team_df.query('time == ' + str(time))
    play_direction = player_data['playDirection'].iloc[0]

    patch.extend(ax.plot(player_data['x'], player_data['y'], 'o', c=team_color, ms=13))

    if plot_blockers:
        blockers_df = get_blocking_players(team_df)
        patch.extend(create_plot_blocking_formation_statements(ax, time, blockers_df))

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


def update_animation_at_timestep(ax, time, offense, defense, football, plot_blockers=False):
    """
    Updates the animation at a specific timestep.
    Args:
        ax: Matplotlib axis
        time: timestep of play
        offense:
        defense:
        football:
        plot_blockers:
    """
    patch = []

    # Plot home players
    patch.extend(plot_players_at_timestep(ax, time, offense, 'orangered', plot_blockers=plot_blockers))

    # Plot away players
    patch.extend(plot_players_at_timestep(ax, time, defense, 'blue'))

    # Plot football
    football_data = football.query('time == ' + str(time))
    patch.extend(ax.plot(football_data['x'], football_data['y'], 'D', c='brown', ms=10,
                         data=football_data['club']))

    return patch


def create_plot_blocking_formation_statements(ax, time, blockers_df, line_color='red'):
    """
    Creates the plot statements for the blocking formation.
    Args:
        ax: Matplotlib axis
        time: timestep of play
        blockers_df: DataFrame with only the blocking players
        line_color: Red is best for visibility
    """
    plot_statements = []
    blocker_df = blockers_df.query('time == ' + str(time))
    blocker_df = blocker_df.sort_values(by=['y'], ascending=[True])

    for i in range(len(blocker_df) - 1):
        blocker = blocker_df.iloc[i]
        next_blocker = blocker_df.iloc[i + 1]

        if next_blocker is not None:
            plot_statements.extend(
                ax.plot([blocker['x'], next_blocker['x']], [blocker['y'], next_blocker['y']], color=line_color))

    return plot_statements


def animate_player_movement(playId, gameId, weekNumber, zoomed_view=False, plot_blockers=False):
    """
    Animates the movement of players and the football for a given play.
    Args:
        playId: Play Id to identify the play
        gameId: Game Id to identify the game
        weekNumber:
        zoomed_view: Only displays the zoomed in view of the play. This window is generated dynamically based on how
        far the players move.
        plot_blockers: Whether to plot the blocking formation. This is red line between the eligible blockers.

    Returns:
        An animation object. This is generated from Matplotlib's animation library. The helper methods generates list
        of plotting statements with specific details such as location, jersey number, orientation, and velocity vector.
    """
    # Load play dataframes
    offense, defense, football = load_play(playId, gameId, weekNumber)
    play = get_play_by_id(gameId, playId)

    boxed_view = get_player_max_locations(offense, defense,
                                          football) if zoomed_view else None  # Display view window size

    offense['time'] = offense['time'].apply(lambda x: dateutil.parser.parse(x).timestamp()).rank(method='dense')
    defense['time'] = defense['time'].apply(lambda x: dateutil.parser.parse(x).timestamp()).rank(method='dense')
    football['time'] = football['time'].apply(lambda x: dateutil.parser.parse(x).timestamp()).rank(method='dense')

    maxTime = int(defense['time'].unique().max())
    minTime = int(defense['time'].unique().min())

    yardlineNumber, yardsToGo = get_los_details(play, offense)
    fig, ax = create_football_field(boxed_view=boxed_view, line_of_scrimmage=yardlineNumber, yards_to_go=yardsToGo)

    playDesc = play['playDescription'].item()
    plt.title(f'Game # {gameId} Play # {playId} \n {playDesc}')

    ims = [[]]
    for time in np.arange(minTime, maxTime + 1):
        patch = update_animation_at_timestep(ax, time, offense=offense, defense=defense, football=football,
                                             plot_blockers=plot_blockers)
        ims.append(patch)

    anim = animation.ArtistAnimation(fig, ims, repeat=False)

    return anim


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


gameId, playId, week = 2022090800, 343, 1

# create_football_field(boxed_view=(0,0,80,NFL_FIELD_HEIGHT), line_of_scrimmage=10, yards_to_go=10)
# plt.show()

# plot_play_events(playId, gameId, week, plot_blockers=True)
# plot_play_tracked_movements(playId, gameId, week)

anim = animate_player_movement(gameId=gameId, playId=playId, weekNumber=week, plot_blockers=True)
save_animation(anim, 'animateOffense.mp4')
