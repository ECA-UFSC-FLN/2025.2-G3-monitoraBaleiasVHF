import numpy as np
import os
from typing import Dict, Tuple
from scipy.signal import windows

# Constante física crucial para simulação de RF
VELOCIDADE_LUZ = 299792458.0  # Velocidade da luz no vácuo (metros por segundo)

class SimuladorAntenasDoA:
    """
    Simula sinais I/Q defasados por Ângulo de Incidência (DoA) para antenas espaçadas.
    O TDOA é calculado a partir do ângulo.
    """
    def __init__(self, taxa_amostragem: float, freq_sinal: float, duracao_s: float, 
                 angulo_incidencia_graus: float):
        """
        :param angulo_incidencia_graus: O ângulo (em graus) de onde o sinal está vindo
                                        (0 graus = perpendicular ao array).
        """
        self.taxa_amostragem = taxa_amostragem
        self.freq_sinal = freq_sinal
        self.duracao_s = duracao_s
        self.num_amostras = int(taxa_amostragem * duracao_s)
        self.lambda_onda = VELOCIDADE_LUZ / freq_sinal
        self.angulo_rad = np.radians(angulo_incidencia_graus)
        
        self.antenas: Dict[str, Tuple[float, float]] = {}
        self.sinais_iq: Dict[str, np.ndarray] = {}
        self.tdoas: Dict[str, float] = {}

    def adicionar_antena(self, nome_antena: str, posicao_x: float):
        """
        Adiciona uma antena à simulação, assumindo array linear (Y=0).

        :param nome_antena: Nome descritivo da antena.
        :param posicao_x: Coordenada X da antena (em metros).
        """
        # Adicionamos Y=0 para manter a consistência com o array linear
        self.antenas[nome_antena] = (posicao_x, 0.0)
        
    def _calcular_tdoas(self):
        """
        Calcula as diferenças de tempo (TDOA) em relação à Antena 1 (referência) 
        com base no ângulo de incidência.
        """
        if not self.antenas:
            raise ValueError("Nenhuma antena adicionada.")

        # Ordenar antenas para garantir que Antena 1 é a referência (posição 0.0)
        antenas_ordenadas = sorted(self.antenas.items(), key=lambda item: item[1][0])
        
        antena_ref_nome = antenas_ordenadas[0][0]
        posicao_ref_x = antenas_ordenadas[0][1][0]
        
        self.tdoas = {}
        print("\n--- TDOA e Fases Calculados ---")

        for nome, pos_antena in antenas_ordenadas:
            posicao_x = pos_antena[0]
            
            # 1. Distância extra percorrida em relação à Antena de Referência
            delta_d = (posicao_x - posicao_ref_x) * np.cos(self.angulo_rad)

            # 2. TDOA (diferença de tempo)
            tdoa = delta_d / VELOCIDADE_LUZ
            self.tdoas[nome] = tdoa
            
            # 3. Defasagem de Fase (o verdadeiro objetivo)
            delta_fase_rad = 2 * np.pi * self.freq_sinal * tdoa
            
            atraso_amostras = tdoa * self.taxa_amostragem
            
            print(f"- {nome}: Posição={posicao_x:.3f}m | TDOA={tdoa*1e9:.3f} ns | Fase={np.degrees(delta_fase_rad):.2f}° | Amostras={atraso_amostras:.3f}")


    def gerar_sinais(self):
        self._calcular_tdoas()
        tempo_base = np.arange(self.num_amostras) / self.taxa_amostragem
        self.sinais_iq = {}

        for nome, tdoa in self.tdoas.items():
            tempo_defasado = tempo_base + tdoa
            
            I_componente = np.cos(2 * np.pi * self.freq_sinal * tempo_defasado)
            Q_componente = np.sin(2 * np.pi * self.freq_sinal * tempo_defasado)
            
            sinal_iq = (I_componente + 1j * Q_componente).astype(np.complex64)
            
            # Adiciona Ruído (AWGN) para simular ambiente real
            amplitude_ruido = 0.05
            ruido = amplitude_ruido * (np.random.randn(self.num_amostras) + 1j * np.random.randn(self.num_amostras))
            
            self.sinais_iq[nome] = sinal_iq + ruido


    def salvar_arquivos_iq(self, prefixo_arquivo: str = "sinal_antena"):
        """
        Salva um arquivo IQ separado para cada sinal de antena.
        Ex: 'sinal_antena_A1.iq', 'sinal_antena_A2.iq', etc.
        """
        if not self.sinais_iq:
            raise ValueError("Sinais não gerados. Chame gerar_sinais() antes de salvar.")

        nomes_salvos = []
        for nome_antena, sinal_iq in self.sinais_iq.items():
            # Cria um nome de arquivo exclusivo
            nome_arquivo = f"{prefixo_arquivo}_{nome_antena}.iq"
            
            # Salva o array complexo (I, Q, I, Q...)
            sinal_iq.tofile(nome_arquivo)
            nomes_salvos.append(nome_arquivo)

        print(f"\n✅ Arquivos IQ gerados com sucesso ({len(nomes_salvos)} arquivos):")
        for nome in nomes_salvos:
            print(f"- {nome}")
        return nomes_salvos