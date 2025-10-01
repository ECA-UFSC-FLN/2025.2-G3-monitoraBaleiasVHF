import numpy as np
import os
from scipy.signal import correlate

# Constante física crucial para simulação de RF
VELOCIDADE_LUZ = 299792458.0  # Velocidade da luz no vácuo (metros por segundo)

class AnalisadorDoA:
    """
    Analisa dados I/Q brutos de um array linear uniforme (ULA) para estimar 
    o TDOA e, consequentemente, o Ângulo de Incidência (DoA).
    """
    def __init__(self, taxa_amostragem: float, freq_sinal: float, espacamento_d: float):
        """
        :param taxa_amostragem: Frequência de amostragem em S/s.
        :param freq_sinal: Frequência da portadora do sinal (Hz).
        :param espacamento_d: Distância entre antenas adjacentes (em metros).
        """
        self.taxa_amostragem = taxa_amostragem
        self.freq_sinal = freq_sinal
        self.espacamento_d = espacamento_d
        self.lambda_onda = VELOCIDADE_LUZ / freq_sinal

    def obter_sinal_do_arquivo(self, nome_arquivo: str) -> np.ndarray:
        """
        Lê um único arquivo IQ binário.
        """
        try:
            # np.fromfile carrega o arquivo binário para um array complexo (complex64)
            dados_lidos = np.fromfile(nome_arquivo, dtype=np.complex64)
            if len(dados_lidos) == 0:
                 raise ValueError("Arquivo está vazio ou não pôde ser lido.")
            return dados_lidos
        except FileNotFoundError:
            raise FileNotFoundError(f"ERRO: Arquivo '{nome_arquivo}' não encontrado.")


    def _estimar_fase_fft_precisa(self, sinal_ref: np.ndarray, sinal_defasado: np.ndarray) -> float:
        """
        Estima o TDOA/Fase no domínio da frequência, onde a portadora é dominante.
        Este método é mais estável para sinais simulados de banda estreita.
        """
        # 1. Aplicar FFT
        fft_ref = np.fft.fft(sinal_ref)
        fft_defasado = np.fft.fft(sinal_defasado)
        
        # 2. Localizar o Pico da Frequência (Portadora)
        # Encontra o índice correspondente à frequência de pico (o bin da portadora)
        indice_pico = np.argmax(np.abs(fft_ref))
        
        # 3. Calcular a Diferença de Fase APENAS no bin da portadora
        # A defasagem entre os dois sinais está inteiramente contida nesta fase
        fase_ref = np.angle(fft_ref[indice_pico])
        fase_defasado = np.angle(fft_defasado[indice_pico])
        
        # Diferença de Fase (intervalo de -pi a pi)
        delta_fase_rad = fase_defasado - fase_ref
        
        # Ajuste para garantir que a diferença esteja dentro do intervalo [-pi, pi]
        delta_fase_rad = np.arctan2(np.sin(delta_fase_rad), np.cos(delta_fase_rad))
        
        return delta_fase_rad

    def calcular_doa(self, sinal_ref: np.ndarray, sinal_defasado: np.ndarray) -> float:
        """
        Calcula o Ângulo de Incidência (DoA) a partir de dois arrays I/Q.
        """
        if sinal_ref.shape != sinal_defasado.shape:
            print("AVISO: Os sinais têm tamanhos diferentes.")
            return np.nan

        # 1. ESTIMAÇÃO: Encontrar a Diferença de Fase (NOVA ABORDAGEM)
        delta_fase_rad = self._estimar_fase_fft_precisa(sinal_ref, sinal_defasado)
        
        # 2. CÁLCULO GEOMÉTRICO: Fase para Cosseno
        # cos(theta) = (Delta_Fase * lambda) / (2 * pi * d)
        lambda_sobre_d = self.lambda_onda / self.espacamento_d
        cos_theta = (delta_fase_rad * lambda_sobre_d) / (2 * np.pi)

        # 3. TRATAMENTO DE ERRO
        cos_theta = np.clip(cos_theta, -1.0, 1.0) 

        # 4. RESULTADO INICIAL
        angulo_doa_radianos = np.arccos(cos_theta)
        angulo_doa_graus = np.degrees(angulo_doa_radianos)
        
        # 5. CORREÇÃO DO QUADRANTE (Baseada no SINAL da Fase)
        # Fase NEGATIVA significa que a antena defasada está ATRASADA (sinal veio de >90 graus)
        if delta_fase_rad < 0:
            angulo_doa_graus = 180.0 - angulo_doa_graus

        print(f"  > Fase Estimada: {np.degrees(delta_fase_rad):.2f}° | cos(theta): {cos_theta:.4f}")
        
        return angulo_doa_graus