import numpy as np

# --- 1. Parâmetros do nosso "Estúdio de Gravação" ---

taxa_amostragem = 300000
duracao_gravacao = 1.0
frequencia_central = 433.0e6
frequencia_tag = 433.022e6
duracao_tag = 0.04
inicio_tag = 0.45

# ---======================================================---
# --- PARTE A SER MODIFICADA PARA CADA ANTENA (Passos 1 a 4) ---
# ---======================================================---

# O "volume" do sinal. VAI MUDAR para cada antena.
amplitude_sinal = 0.2 # Valor inicial para a antena Norte

# O nome do arquivo de saída. VAI MUDAR para cada antena.
nome_arquivo_saida = "oeste.iq" # Valor inicial para a antena Norte

# ---======================================================---
# --- Fim da parte a ser modificada                      ---
# ---======================================================---


print(f"Gerando arquivo '{nome_arquivo_saida}' com amplitude {amplitude_sinal}...")

# --- 2. Gerar o Ruído de Fundo (Estática) ---

num_amostras = int(duracao_gravacao * taxa_amostragem)
ruido_i = np.random.randn(num_amostras) * 0.1
ruido_q = np.random.randn(num_amostras) * 0.1
ruido_complexo = ruido_i + 1j * ruido_q

# --- 3. Gerar o Sinal Puro da Tag (o "Bip") ---

frequencia_offset = frequencia_tag - frequencia_central
num_amostras_tag = int(duracao_tag * taxa_amostragem)
tempo_tag = np.arange(num_amostras_tag) / taxa_amostragem
sinal_tag_complexo = amplitude_sinal * np.exp(1j * 2 * np.pi * frequencia_offset * tempo_tag)

# --- 4. Misturar o Sinal da Tag com o Ruído de Fundo ---

sinal_final_complexo = np.copy(ruido_complexo)
inicio_amostra_tag = int(inicio_tag * taxa_amostragem)
fim_amostra_tag = inicio_amostra_tag + num_amostras_tag
sinal_final_complexo[inicio_amostra_tag:fim_amostra_tag] += sinal_tag_complexo

# --- 5. Salvar o Sinal em um Arquivo Binário ---

sinal_final_i = np.real(sinal_final_complexo)
sinal_final_q = np.imag(sinal_final_complexo)
sinal_intercalado = np.empty(num_amostras * 2, dtype=np.int8)
sinal_intercalado[0::2] = (sinal_final_i * 127).astype(np.int8)
sinal_intercalado[1::2] = (sinal_final_q * 127).astype(np.int8)

with open(nome_arquivo_saida, "wb") as f:
    f.write(sinal_intercalado.tobytes())

print(f"Arquivo '{nome_arquivo_saida}' gerado com sucesso!")