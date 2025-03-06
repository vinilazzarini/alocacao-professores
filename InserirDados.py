import pandas as pd
import os

# Arquivos CSV
ARQUIVO_PROFESSORES = "professores.csv"
ARQUIVO_DISCIPLINAS = "disciplinas.csv"
ARQUIVO_TURMAS = "turmas.csv"
ARQUIVO_SALAS = "salas.csv"
ARQUIVO_SOFTWARES = "softwares_laboratorio.csv"

# Criar arquivos caso não existam (atualizado o cabeçalho de turmas)
for arquivo, colunas in [
    (ARQUIVO_PROFESSORES, ["Nome", "Área", "Modalidades", "Disponibilidade"]),
    (ARQUIVO_DISCIPLINAS, ["Nome", "Necessita_Lab", "Modalidade", "Créditos_Semanais", "Área"]),
    (ARQUIVO_TURMAS, ["Curso", "Semestre", "Periodo", "Quantidade_Alunos", "Disciplinas"]),
    (ARQUIVO_SALAS, ["Nome", "Tipo", "Capacidade"]),
    (ARQUIVO_SOFTWARES, ["Laboratorio", "Softwares"])
]:
    if not os.path.exists(arquivo):
        pd.DataFrame(columns=colunas).to_csv(arquivo, index=False)

# Função para carregar dados do CSV
def carregar_dados(arquivo):
    return pd.read_csv(arquivo)

# Função para formatar como string com aspas para listas
def formatar_lista_como_string(lista):
    if isinstance(lista, list):
        return '"' + ",".join([item.strip() for item in lista]) + '"'
    return lista

# Cadastro de salas e laboratórios
def cadastrar_sala():
    nome = input("Nome da sala ou laboratório: ")
    tipo = input("Tipo (Sala / Laboratório): ").strip().lower()
    
    if tipo not in ["sala", "laboratório"]:
        print("Erro: Escolha 'Sala' ou 'Laboratório'.")
        return
    
    while True:
        try:
            capacidade = int(input("Capacidade máxima da sala/laboratório: "))
            if capacidade <= 0:
                print("Erro: Capacidade deve ser maior que zero.")
                continue
            break
        except ValueError:
            print("Erro: Digite um número válido para a capacidade.")

    nova_sala = pd.DataFrame([{
        "Nome": nome,
        "Tipo": tipo.capitalize(),
        "Capacidade": capacidade
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
    softwares = formatar_lista_como_string(softwares.split(","))

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
    modalidades = formatar_lista_como_string(modalidades.split(","))
    # Disponibilidade agora deve ser cadastrada no formato "Seg-Matutino" ou "Seg-Noturno"
    disponibilidade = input("Disponibilidade (ex: Seg-Matutino, Qua-Noturno) [Separe por vírgula]: ").strip()
    disponibilidade = formatar_lista_como_string(disponibilidade.split(","))

    novo_professor = pd.DataFrame([{
        "Nome": nome,
        "Área": area,
        "Modalidades": modalidades,
        "Disponibilidade": disponibilidade
    }])

    novo_professor.to_csv(ARQUIVO_PROFESSORES, mode='a', header=False, index=False)
    print(f"Professor {nome} cadastrado com sucesso!")

# Cadastro de disciplinas (com área)
def cadastrar_disciplina():
    nome = input("Nome da disciplina: ")
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
    
    area = input("Área da disciplina (ex: Desenvolvimento, Infraestrutura, Outros): ").strip()

    nova_disciplina = pd.DataFrame([{
        "Nome": nome,
        "Necessita_Lab": necessidade_lab,
        "Modalidade": modalidade,
        "Créditos_Semanais": creditos,
        "Área": area
    }])

    nova_disciplina.to_csv(ARQUIVO_DISCIPLINAS, mode='a', header=False, index=False)
    print(f"Disciplina {nome} cadastrada com sucesso!")

# Cadastro de turmas (agora com "Semestre" e "Periodo" Matutino/Noturno)
def cadastrar_turma():
    curso = input("Nome do curso: ")
    
    while True:
        try:
            semestre = int(input("Semestre (1 a 8): "))
            if semestre < 1 or semestre > 8:
                print("Erro: O semestre deve estar entre 1 e 8.")
                continue
            break
        except ValueError:
            print("Erro: Digite um número válido para o semestre.")

    periodo = input("Período (Matutino ou Noturno): ").strip().capitalize()
    while periodo not in ["Matutino", "Noturno"]:
        print("Erro: O período deve ser Matutino ou Noturno.")
        periodo = input("Período (Matutino ou Noturno): ").strip().capitalize()

    while True:
        try:
            quantidade_alunos = int(input("Quantidade de alunos: "))
            if quantidade_alunos <= 0:
                print("Erro: A quantidade de alunos deve ser maior que zero.")
                continue
            break
        except ValueError:
            print("Erro: Digite um número válido para a quantidade de alunos.")

    disciplinas = input("Disciplinas que essa turma cursará (separadas por vírgula): ").strip()
    disciplinas = formatar_lista_como_string(disciplinas.split(","))

    nova_turma = pd.DataFrame([{
        "Curso": curso,
        "Semestre": semestre,
        "Periodo": periodo,
        "Quantidade_Alunos": quantidade_alunos,
        "Disciplinas": disciplinas
    }])

    nova_turma.to_csv(ARQUIVO_TURMAS, mode='a', header=False, index=False)
    print(f"Turma do curso {curso} cadastrada com sucesso!")

# Exibir dados cadastrados
def visualizar_dados():
    professores = carregar_dados(ARQUIVO_PROFESSORES)
    disciplinas = carregar_dados(ARQUIVO_DISCIPLINAS)
    turmas = carregar_dados(ARQUIVO_TURMAS)
    salas = carregar_dados(ARQUIVO_SALAS)
    softwares = carregar_dados(ARQUIVO_SOFTWARES)

    print("\nProfessores Cadastrados:")
    print(professores if not professores.empty else "Nenhum professor cadastrado.")

    print("\nDisciplinas Cadastradas:")
    print(disciplinas if not disciplinas.empty else "Nenhuma disciplina cadastrada.")

    print("\nTurmas Cadastradas:")
    print(turmas if not turmas.empty else "Nenhuma turma cadastrada.")

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
        print("3. Cadastrar Turma")
        print("4. Cadastrar Sala / Laboratório")
        print("5. Cadastrar Softwares para Laboratórios")
        print("6. Visualizar Dados")
        print("7. Sair")
        opcao = input("Escolha uma opção: ")

        if opcao == "1":
            cadastrar_professor()
        elif opcao == "2":
            cadastrar_disciplina()
        elif opcao == "3":
            cadastrar_turma()
        elif opcao == "4":
            cadastrar_sala()
        elif opcao == "5":
            cadastrar_software_laboratorio()
        elif opcao == "6":
            visualizar_dados()
        elif opcao == "7":
            print("Encerrando o sistema...")
            break
        else:
            print("Opção inválida, tente novamente.")

menu()
