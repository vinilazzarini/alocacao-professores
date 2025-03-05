import pandas as pd
import os

# Arquivos CSV
ARQUIVO_PROFESSORES = "professores.csv"
ARQUIVO_DISCIPLINAS = "disciplinas.csv"
ARQUIVO_SALAS = "salas.csv"
ARQUIVO_SOFTWARES = "softwares_laboratorio.csv"

# Criar arquivos caso não existam
if not os.path.exists(ARQUIVO_PROFESSORES):
    pd.DataFrame(columns=["Nome", "Área", "Modalidades", "Disponibilidade"]).to_csv(ARQUIVO_PROFESSORES, index=False)

if not os.path.exists(ARQUIVO_DISCIPLINAS):
    pd.DataFrame(columns=["Nome", "Turma", "Necessita_Lab", "Modalidade", "Créditos_Semanais"]).to_csv(ARQUIVO_DISCIPLINAS, index=False)

if not os.path.exists(ARQUIVO_SALAS):
    pd.DataFrame(columns=["Nome", "Tipo"]).to_csv(ARQUIVO_SALAS, index=False)

if not os.path.exists(ARQUIVO_SOFTWARES):
    pd.DataFrame(columns=["Laboratorio", "Softwares"]).to_csv(ARQUIVO_SOFTWARES, index=False)

# Função para carregar dados do CSV
def carregar_dados(arquivo):
    return pd.read_csv(arquivo)

# Cadastro de salas e laboratórios
def cadastrar_sala():
    nome = input("Nome da sala ou laboratório: ")
    tipo = input("Tipo (Sala / Laboratório): ").strip().lower()

    if tipo not in ["sala", "laboratório"]:
        print("Erro: Escolha 'Sala' ou 'Laboratório'.")
        return

    nova_sala = pd.DataFrame([{
        "Nome": nome,
        "Tipo": tipo.capitalize()
    }])

    nova_sala.to_csv(ARQUIVO_SALAS, mode='a', header=False, index=False)
    print(f"{tipo.capitalize()} '{nome}' cadastrado com sucesso!")

# Cadastro de softwares para laboratórios (após alocação)
def cadastrar_software_laboratorio():
    laboratorios = carregar_dados(ARQUIVO_SALAS)
    laboratorios = laboratorios[laboratorios["Tipo"] == "Laboratório"]

    if laboratorios.empty:
        print("Nenhum laboratório cadastrado!")
        return

    print("\nLaboratórios disponíveis:")
    print(laboratorios)

    lab_nome = input("\nDigite o nome do laboratório para adicionar softwares: ")

    if lab_nome not in laboratorios["Nome"].values:
        print("Erro: Laboratório não encontrado.")
        return

    softwares = input("Digite os softwares necessários (separados por vírgula): ").strip()

    novo_software = pd.DataFrame([{
        "Laboratorio": lab_nome,
        "Softwares": softwares
    }])

    novo_software.to_csv(ARQUIVO_SOFTWARES, mode='a', header=False, index=False)
    print(f"Softwares cadastrados para o laboratório {lab_nome}!")

# Cadastro de professores
def cadastrar_professor():
    nome = input("Nome do professor: ")
    area = input("Área de atuação (Desenvolvimento, Infra, Ambos): ").strip()
    modalidades = input("Modalidades (Presencial, EAD, Híbrido) [Separe por vírgula]: ").strip()
    disponibilidade = input("Disponibilidade (ex: Seg-Manhã, Qua-Noite) [Separe por vírgula]: ").strip()

    novo_professor = pd.DataFrame([{
        "Nome": nome,
        "Área": area,
        "Modalidades": modalidades,
        "Disponibilidade": disponibilidade
    }])

    novo_professor.to_csv(ARQUIVO_PROFESSORES, mode='a', header=False, index=False)
    print(f"Professor {nome} cadastrado com sucesso!")

# Cadastro de disciplinas
def cadastrar_disciplina():
    nome = input("Nome da disciplina: ")
    turma = input("Turma (Ex: 1º período, 3º semestre): ").strip()
    necessidade_lab = input("Precisa de laboratório? (Sim/Não): ").strip().lower() == "sim"
    modalidade = input("Modalidade (Presencial, EAD, Híbrido): ").strip()

    while True:
        try:
            creditos = int(input("Créditos Semanais (horas/aula por semana): ").strip())
            if creditos <= 0:
                print("Erro: O número de créditos semanais deve ser maior que zero.")
                continue
            break
        except ValueError:
            print("Erro: Digite um número válido para os créditos semanais.")

    nova_disciplina = pd.DataFrame([{
        "Nome": nome,
        "Turma": turma,
        "Necessita_Lab": necessidade_lab,
        "Modalidade": modalidade,
        "Créditos_Semanais": creditos
    }])

    nova_disciplina.to_csv(ARQUIVO_DISCIPLINAS, mode='a', header=False, index=False)
    print(f"Disciplina {nome} cadastrada com sucesso!")

# Exibir dados cadastrados
def visualizar_dados():
    professores = carregar_dados(ARQUIVO_PROFESSORES)
    disciplinas = carregar_dados(ARQUIVO_DISCIPLINAS)
    salas = carregar_dados(ARQUIVO_SALAS)
    softwares = carregar_dados(ARQUIVO_SOFTWARES)

    print("\nProfessores Cadastrados:")
    print(professores if not professores.empty else "Nenhum professor cadastrado.")

    print("\nDisciplinas Cadastradas:")
    print(disciplinas if not disciplinas.empty else "Nenhuma disciplina cadastrada.")

    print("\nSalas e Laboratórios Cadastrados:")
    print(salas if not salas.empty else "Nenhuma sala cadastrada.")

    print("\nSoftwares por Laboratório:")
    print(softwares if not softwares.empty else "Nenhum software cadastrado.")

# Menu de interação
def menu():
    while True:
        print("\n--- SISTEMA DE ALOCAÇÃO ---")
        print("1. Cadastrar Professor")
        print("2. Cadastrar Disciplina")
        print("3. Cadastrar Sala / Laboratório")
        print("4. Cadastrar Softwares para Laboratórios")
        print("5. Visualizar Dados")
        print("6. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_professor()
        elif opcao == "2":
            cadastrar_disciplina()
        elif opcao == "3":
            cadastrar_sala()
        elif opcao == "4":
            cadastrar_software_laboratorio()
        elif opcao == "5":
            visualizar_dados()
        elif opcao == "6":
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida, tente novamente.")

# Iniciar menu
menu()