import Analyser
import SimuladorAntenas
import numpy as np

def comparar_sinais_tolerancia(orig, lido, nome):
    if orig.shape != lido.shape:
        print(f"[{nome}] ❌ Tamanhos diferentes: {orig.shape} vs {lido.shape}")
        return
    iguais = np.allclose(orig, lido, atol=1e-6)
    print(f"[{nome}] ✅ Iguais (com tolerância): {iguais}")

def compara_tudo():
    comparar_sinais_tolerancia(sinal_A1, sinal_A1read, "A1")
    comparar_sinais_tolerancia(sinal_A2, sinal_A2read, "A2")
    comparar_sinais_tolerancia(sinal_A3, sinal_A3read, "A3")
    comparar_sinais_tolerancia(sinal_A4, sinal_A4read, "A4")


VELOCIDADE_LUZ = 299792458.0

# ----------------------------------------------------------------------
# --- EXEMPLO DE USO PARA DETERMINAÇÃO DE ÂNGULO (DoA) ---
# ----------------------------------------------------------------------

# Criando os dados de teste
taxa_amostragem = 100000000.0   # 10 MS/s (Maior resolução melhora o FFT)
freq_sinal = 433000000.0      # 433 MHz
duracao = 0.001               # 1 ms
lambda_onda = VELOCIDADE_LUZ / freq_sinal
d_espacamento = lambda_onda / 2 
ANGULO_VERDADEIRO = 100.0      # Ângulo que o sistema precisa descobrir (funciona só de 0 a 90)

simulador = SimuladorAntenas.SimuladorAntenasDoA(taxa_amostragem, freq_sinal, duracao, ANGULO_VERDADEIRO)

# Instanciar antenas
simulador.adicionar_antena('A1', 0.0)
simulador.adicionar_antena('A2', d_espacamento)
simulador.adicionar_antena('A3', 2*d_espacamento)
simulador.adicionar_antena('A4', 3*d_espacamento)

simulador.gerar_sinais()
arquivos_gerados = simulador.salvar_arquivos_iq("sinal_antena")

# Extrair os sinais simulados originais
sinal_A1 = simulador.sinais_iq['A1']
sinal_A2 = simulador.sinais_iq['A2']
sinal_A3 = simulador.sinais_iq['A3']
sinal_A4 = simulador.sinais_iq['A4']

print(f"\n[Verdadeiro Ângulo de Incidência: {ANGULO_VERDADEIRO}°]")


# --- PARTE B: ANÁLISE (O que o seu DSP faria) ---
analisador = Analyser.AnalisadorDoA(taxa_amostragem, freq_sinal, d_espacamento)

# Ler os sinais salvos nos arquivos IQ
sinal_A1read = analisador.obter_sinal_do_arquivo("sinal_antena_A1.iq")
sinal_A2read = analisador.obter_sinal_do_arquivo("sinal_antena_A2.iq")
sinal_A3read = analisador.obter_sinal_do_arquivo("sinal_antena_A3.iq")
sinal_A4read = analisador.obter_sinal_do_arquivo("sinal_antena_A4.iq")

# Cálculo com sinais originais
# angulo_estimado1 = analisador.calcular_doa(sinal_A1, sinal_A2)
# angulo_estimado2 = analisador.calcular_doa(sinal_A2, sinal_A3)
# angulo_estimado3 = analisador.calcular_doa(sinal_A3, sinal_A4)

# Cálculo com sinais lidos dos arquivos .iq
angulo_estimado1 = analisador.calcular_doa(sinal_A1read, sinal_A2read)
angulo_estimado2 = analisador.calcular_doa(sinal_A2read, sinal_A3read)
angulo_estimado3 = analisador.calcular_doa(sinal_A3read, sinal_A4read)
angulo_medio = (angulo_estimado1 + angulo_estimado2 + angulo_estimado3)/3

print(f"\n[Ângulo Estimado a partir dos Dados I/Q: {angulo_estimado1:.2f}°]")
print(f"\n[Ângulo Estimado a partir dos Dados I/Q: {angulo_estimado2:.2f}°]")
print(f"\n[Ângulo Estimado a partir dos Dados I/Q: {angulo_estimado3:.2f}°]")
print(f"\n[Ângulo Estimado MÉDIO: {angulo_medio:.2f}°]")
