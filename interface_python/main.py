import radarDisplay as rd
import matplotlib.pyplot as plt

# Configura o gráfico
fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
ax.set_theta_zero_location('N')
ax.set_theta_direction(-1)
ax.set_ylim(0, 100)
ax.set_yticklabels([])
ax.set_title('Baleias')

# Cria a instância da classe que gerencia a interface
# debug = 0 (default): Sem nada
# debug = 1: Radar com mouse
# debug = 2: Coordenada aleatória

radar = rd.RadarDisplay(fig, ax, 1)

plt.show()