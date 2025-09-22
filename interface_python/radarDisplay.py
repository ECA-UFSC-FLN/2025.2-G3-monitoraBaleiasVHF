import numpy as np

class RadarDisplay:

    def __init__(self, fig, ax, debug=0):
        self.fig = fig
        self.ax = ax
        self.last_angle = 0

        self.cone_width_deg = 20 # Largura do cone em graus (n/2 para cada lado)
        self.max_distance = 100 # Distância máxima do radar

        # O cone será um objeto Polygon
        self.cone = self.ax.fill([], [], color='green', alpha=0.3)[0]
        
        # Conecta o evento de movimento do mouse
        if debug == 1:
            self.fig.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)


    def set_angle(self, angle):
        half_angle = np.deg2rad(self.cone_width_deg / 2)
        start_angle = angle - half_angle
        end_angle = angle + half_angle

        # Número de segmentos do arco
        num_segments = 5
        arc_angles = np.linspace(start_angle, end_angle, num_segments)

        # angulos e raios para o polígono do cone
        # 1. Ponto central na origem (0, 0)
        # 2. Pontos ao longo do arco externo
        # 3. Ponto final para fechar o polígono na origem
        x_coords = np.concatenate(([angle], arc_angles, [angle]))
        y_coords = np.concatenate(([0], np.full(num_segments, self.max_distance), [0]))
        
        # Define coordenadas e da draw no plot
        self.cone.set_xy(np.column_stack([x_coords, y_coords]))
        self.fig.canvas.draw_idle()


    def on_mouse_move(self, event):
        # Verifica mouse dentro do plot
        if event.inaxes is not None and event.inaxes == self.ax:
            theta_rad = event.xdata
            
            # Se a coordenada do evento for None, usa o último ângulo conhecido
            if theta_rad is None:
                theta_rad = self.last_angle
            else:
                # Normaliza o ângulo para 360 graus (0 a 2*pi)
                if theta_rad < 0:
                    theta_rad += 2 * np.pi
                self.last_angle = theta_rad

            self.set_angle(theta_rad)


