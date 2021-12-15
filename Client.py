import threading
import arcade
import asyncio
import socket
import Server
import pathlib
import json
import PlayerState

HEALTHBAR_WIDTH = 25
HEALTHBAR_HEIGHT = 3
HEALTHBAR_OFFSET_Y = -10
HEALTH_NUMBER_OFFSET_X = -10
HEALTH_NUMBER_OFFSET_Y = -25


class SpriteWithHealth(arcade.AnimatedTimeBasedSprite):
    def __init__(self, image, max_health, scaling):
        super().__init__(image, scaling)
        self.max_health = max_health
        self.cur_health = max_health
        self.move_speed = 3

    def draw_health_number(self):
        """ Draw how many hit points we have """

        health_string = f"{self.cur_health}/{self.max_health}"
        arcade.draw_text(health_string,
                         start_x=self.center_x + HEALTH_NUMBER_OFFSET_X,
                         start_y=self.center_y + HEALTH_NUMBER_OFFSET_Y,
                         font_size=12,
                         color=arcade.color.WHITE)

    def draw_health_bar(self):
        """ Draw the health bar """

        # Draw the 'unhealthy' background
        if self.cur_health < self.max_health:
            arcade.draw_rectangle_filled(center_x=self.center_x,
                                         center_y=self.center_y + HEALTHBAR_OFFSET_Y,
                                         width=HEALTHBAR_WIDTH,
                                         height=3,
                                         color=arcade.color.RED)

        # Calculate width based on health
        health_width = HEALTHBAR_WIDTH * (self.cur_health / self.max_health)

        arcade.draw_rectangle_filled(center_x=self.center_x - 0.5 * (HEALTHBAR_WIDTH - health_width),
                                     center_y=self.center_y - 10,
                                     width=health_width,
                                     height=HEALTHBAR_HEIGHT,
                                     color=arcade.color.GREEN)


class GameClient(arcade.Window):
    def __init__(self, server_add, client_add):
        super().__init__(480, 480)
        self.ip_addr = client_add
        self.player = SpriteWithHealth(pathlib.Path.cwd() / 'assets' / 'wizard.png', 3, 2)
        self.server_address = server_add
        self.map_location = pathlib.Path.cwd() / 'assets' / 'map1.json'
        game_map = arcade.tilemap.load_tilemap(self.map_location)
        self.mapscene = arcade.Scene.from_tilemap(game_map)
        self.floor_list = game_map.sprite_lists['floor_layer']
        self.wall_list = game_map.sprite_lists['wall_layer']
        self.pushable_list = game_map.sprite_lists['pushable_layer']
        self.simple_physics = arcade.PhysicsEngineSimple(self.player, self.wall_list)
        self.player_list = arcade.SpriteList()
        self.player_list.append(self.player)
        self.powerup_list = arcade.SpriteList()
        self.from_server = ""
        #        self.player_state_list = PlayerState.GameState(player_states=[])
        self.actions = PlayerState.PlayerMovement()

    def setup(self):
        self.player = SpriteWithHealth(pathlib.Path.cwd() / 'assets' / 'wizard.png', 3, 2)
        self.player_list.append(self.player)
        self.map_location = pathlib.Path.cwd() / 'assets' / 'map1.json'
        game_map = arcade.tilemap.load_tilemap(self.map_location)
        self.mapscene = arcade.Scene.from_tilemap(game_map)
        self.floor_list = game_map.sprite_lists['floor_layer']
        self.wall_list = game_map.sprite_lists['wall_layer']
        self.pushable_list = game_map.sprite_lists['pushable_layer']
        self.simple_physics = arcade.PhysicsEngineSimple(self.player, self.wall_list)
        self.from_server = ""

    def on_update(self, delta_time: float):
        self.simple_physics.update()
        if self.simple_physics.update():
            self.actions.keys[arcade.key.A] = True
        else:
            self.actions.keys[arcade.key.A] = False

    def on_draw(self):
        arcade.start_render()
        self.mapscene.draw()
        self.player_list.draw()
        self.powerup_list.draw()
        for player in self.player_list:
            player.draw_health_number()
            player.draw_health_bar()

    def on_key_press(self, key: int, modifiers: int):
        if (key in self.actions.keys):
            self.actions.keys[key] = True

    def on_key_release(self, symbol: int, modifiers: int):
        if (symbol in self.actions.keys):
            self.actions.keys[symbol] = False


def setup_client_connection(client: GameClient):
    client_event_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(client_event_loop)
    client_event_loop.create_task(communication_with_server(client, client_event_loop))
    client_event_loop.run_forever()


async def communication_with_server(client: GameClient, event_loop):
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:
        keystate = json.dumps(client.actions.keys)
        UDPClientSocket.sendto(str.encode(keystate), (client.server_address, Server.SERVER_PORT))
        data_packet = UDPClientSocket.recvfrom(1024)
        data = data_packet[0]  # get the encoded string
        decoded_data: PlayerState.GameState = PlayerState.GameState.from_json(data)
        player_dict = decoded_data.player_states
        # target: PlayerState.TargetState = decoded_data.target
        # client.target.center_x = target.xLoc
        #  client.target.center_y = target.yloc
        player_info: PlayerState.PlayerState = player_dict[client.ip_addr]
        client.from_server = player_info.points
        client.player.center_x = player_info.x_loc
        client.player.center_y = player_info.y_loc


def main():
    client_address = Server.find_ip_address()
    server_address = input("what is the IP address of the server:")
    game = GameClient(server_address, client_address)
    client_thread = threading.Thread(target=setup_client_connection, args=(game,), daemon=True)
    client_thread.start()
    arcade.run()


if __name__ == '__main__':
    main()
