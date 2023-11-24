from CastleDefense.utils.extractPlayDataUtils import *
from CastleDefense.utils.visualizeFieldUtils import *
from CastleDefense.utils.customMarker import CustomMarker
import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle
from matplotlib import animation
from matplotlib.animation import FFMpegWriter, FuncAnimation
import warnings
warnings.filterwarnings('ignore')

WINDOW_DISPLAY_SIZE = 6


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

    if plot_blockers:
        blockers_df = get_blocking_players(team_df)
        patch.extend(create_plot_statements_blocking_formation(ax, frameId, blockers_df))

    for _, player in player_data.iterrows():
        # Use Text to display the player's jersey number or position as identifier
        patch.append(ax.text(player['x'], player['y'], player['playerDisplayIdentifier'], va='center', ha='center', color='white', fontsize=10, label='playerDisplayIdentifier'))

        player_orientation_degree = player['o'] if play_direction == 'left' else player['o'] + 180

        # Use a custom marker to display the player's orientation
        # TODO: Create/import svg file for the player marker. Insipiration: https://twitter.com/SethWalder
        player_id = player['playerDisplayIdentifier']

        # custom_player_marker = CustomMarker(text=player_id, color='red')
        custom_player_marker = MarkerStyle(r'$D$')
        custom_player_marker = custom_player_marker.rotated(deg=player_orientation_degree-90)
        # custom_player_marker._transform.rotate_deg(player_orientation_degree-90)  # Marker has right facing standar orientation

        patch.append(ax.plot(player['x'], player['y'], "ro", marker=custom_player_marker, c=team_color, ms=14, label='PlayerCircle'))

        # Calculate and plot players' velocity vectors
        dx, dy = calculate_dx_dy(player['s'], player['dir'])

        patch.append(ax.arrow(player['x'], player['y'], dx, dy, color='grey', width=0.15, shape='full', alpha=0.5, label='VelocityVector'))

    return patch


def create_plot_statements_blocking_formation(ax, frameId, blockers_df, line_color='red'):
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
                ax.plot([blocker['x'], next_blocker['x']], [blocker['y'], next_blocker['y']], color=line_color, label='BlockingLine'))

    return plot_statements


def center_view_on_football(ax, football_data, window_size=WINDOW_DISPLAY_SIZE):
    """
    Centers the view on the football through set_xlim() methods.
    Args:
        ax: Matplotlib axis
        football_data: DataFrame with only the football
        window_size: The size of the window to display around the football
    """
    x_min = football_data['x'].iloc[0] - window_size
    x_max = football_data['x'].iloc[0] + window_size
    y_min = football_data['y'].iloc[0] - window_size
    y_max = football_data['y'].iloc[0] + window_size

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    return ax


def zoom_effect(ax, frameId, football_data, event_frameIds, window_size=WINDOW_DISPLAY_SIZE):
    """
    Zooms out and back in to give context of the play.
    Args:
        ax:
        frameId:
        football_data:
        event_frameIds:
        window_size:
    """
    window_size += event_frameIds[frameId][0]
    return center_view_on_football(ax, football_data, window_size=window_size)


def animate_frameId(ax, frameId, offense, defense, football, event_frameIds=None, plot_blockers=False,
                    center_on_football=False):
    """
    Updates the animation at a specific timestep.
    Args:
        ax: Matplotlib axis
        frameId: integer timestep of play
        offense:
        defense:
        football:
        plot_blockers: Plots the blocking formation with red lines
        center_on_football: Allows camera to follow the football
    """
    patch = []
    football_data = football[football['frameId'] == frameId]

    # Centers the display window on the football like a rolling birds eye view
    if center_on_football:
        if event_frameIds and frameId in event_frameIds.keys():
            zoom_effect(ax, frameId, football_data, event_frameIds)  # Zoom out and back in to give context of the play
            return patch
        elif frameId == football['frameId'].min():
            center_view_on_football(ax, football_data, window_size=INITIAL_ZOOM_OUT_WINDOW)
        else:
            center_view_on_football(ax, football_data)  # Center the view on the football

    # Plot home players
    patch.extend(create_plot_statements_at_frameId(ax, frameId, offense, 'orangered', plot_blockers=plot_blockers))

    # Plot away players
    patch.extend(create_plot_statements_at_frameId(ax, frameId, defense, 'blue'))

    # Plot football
    patch.extend(ax.plot(football_data['x'], football_data['y'], 'D', c='brown', ms=10, data=football_data['club'],
                         label="Football"))

    return patch


def save_animation(anim, animation_path):
    """
    Saves the animation to a file. May need ffmpeg installed and added to system PATH.
    :param anim: An animation object from Matplot Animation Library
    :param animation_path:
    :return:
    """
    anim.save(animation_path, writer=FFMpegWriter(fps=10))
    return


def animate_func_play(playId, gameId, weekNumber, zoomed_view=False, plot_blockers=False, center_on_football=False,
                      zoom_effect_on_events=False, display_position=False, animation_path='animation.mp4'):
    """
    Animates the movement of players and the football for a given play using FuncAnimation.
    """
    plt.close()

    # Load play dataframes
    offense, defense, football = load_play(playId, gameId, weekNumber)
    play = get_play_by_id(gameId, playId)
    yardlineNumber, yardsToGo = get_los_details(play, offense)

    # Assign player display identifier
    offense, defense = assign_player_display_identifier(offense, defense, display_position=display_position)

    event_frameIds = {}  # Key: frameId, Value: (window_size_increase, event_name)
    if zoom_effect_on_events:
        offense, defense, football, event_frameIds = adjust_frameIds_for_initial_zoom(offense, defense, football, event_frameIds)
        offense, defense, football, event_frameIds = adjust_frameIds_for_zoom_effect(offense, defense, football, event_frameIds)

    # Display window
    boxed_view = get_player_max_locations(offense, defense, football) if zoomed_view and not center_on_football else None

    # Create field to animate upon
    fig, ax = create_football_field(boxed_view=boxed_view, line_of_scrimmage=yardlineNumber, yards_to_go=yardsToGo)
    playDesc = play['playDescription'].item()
    ax.set_title(f'Game # {gameId} Play # {playId} \n {playDesc}')

    def update(frameId, ax, offense, defense, football, plot_blockers, center_on_football=False, event_frameIds=None):
        """
        Function used to update each animation timestep (frameId) from FuncAnimation.
        """
        # # Remove all texts, circles, arrows, and footballs from the previous frame unless it is a zoom event
        is_zoom_event = center_on_football and event_frameIds and frameId+1 in event_frameIds.keys()
        if not is_zoom_event:  # Do not remove the previous frame locations during zoom effect since the play is stopped
            # Remove all texts, circles, arrows, and footballs from the previous frame on regular time-consuming events.
            artists_to_remove = ax.findobj(match=lambda x: x.get_label() in ['Football', 'PlayerCircle', 'playerDisplayIdentifier', 'BlockingLine', 'VelocityVector'])
            [artist.remove() for artist in artists_to_remove]

        animate_frameId(ax, frameId + 1, offense=offense, defense=defense, football=football,
                        event_frameIds=event_frameIds, plot_blockers=plot_blockers,
                        center_on_football=center_on_football)

    # Create FuncAnimation
    frames = len(range(int(offense['frameId'].min()), int(offense['frameId'].max())))
    anim = FuncAnimation(fig, update, frames=frames,
                         fargs=(ax, offense, defense, football, plot_blockers, center_on_football, event_frameIds),
                         repeat=False)

    # Save animation
    anim.save(animation_path, writer=FFMpegWriter(fps=10))
    plt.show()  # Display the animation

    return anim


# gameId, playId, week = 2022101609, 2504, 6  # Keneth Walker 21 Yard run
# gameId, playId, week = 2022100908,3537, 5  # 9 Yard catch by P.Hesse
gameId, playId, week = 2022090800, 343, 1  # 2 Yard run


# animate_func_play(playId=playId, gameId=gameId, weekNumber=week, plot_blockers=False, center_on_football=False,
#                   animation_path='animateFuncOffenseWithoutZoom.mp4')
animate_func_play(playId=playId, gameId=gameId, weekNumber=week, plot_blockers=False, center_on_football=True,
                  zoom_effect_on_events=True, display_position=False, animation_path='animateFuncOffense.mp4')
