import pandas as pd
import random
import os

# Arquivos CSV
ARQUIVO_PROFESSORES = "professores.csv"
ARQUIVO_DISCIPLINAS = "disciplinas.csv"
ARQUIVO_TURMAS = "turmas.csv"
ARQUIVO_SALAS = "salas.csv"

# Estrutura de horários
HORARIOS_DIURNO = ["07:30-08:20", "08:20-09:10", "09:30-10:20", "10:20-11:10"]
HORARIOS_NOTURNO = ["19:10-20:00", "20:00-20:50", "21:00-21:50", "21:50-22:40"]
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

# Função para carregar dados do CSV
def carregar_dados(arquivo):
    return pd.read_csv(arquivo) if os.path.exists(arquivo) else pd.DataFrame()

# Criar grade horária vazia (cada célula é uma lista para permitir múltiplas aulas, se necessário)
def criar_grade_vazia():
    return {dia: {h: [] for h in HORARIOS_DIURNO + HORARIOS_NOTURNO} for dia in DIAS_SEMANA}

# Função para verificar se o professor está disponível (usa a disponibilidade do professor, que contém strings como "Seg-Manhã")
def professor_disponivel(professor, dia, horario):
    disponibilidade = professor["Disponibilidade"].split(",") if isinstance(professor["Disponibilidade"], str) else []
    dia_sigla = dia[:3]  # Ex: "Seg" para "Segunda"
    # Verifica se algum item na disponibilidade começa com o dia
    for disp in disponibilidade:
        if disp.strip().startswith(dia_sigla):
            return True
    return False

# Verifica se a modalidade (tipo de aula) da disciplina é aceita pelo professor
def modalidade_aceita(professor, tipo_disciplina):
    modalidades = professor["Modalidades"].split(",") if isinstance(professor["Modalidades"], str) else []
    return tipo_disciplina in [m.strip() for m in modalidades]

# Verifica conflitos: impede que o mesmo professor, turma ou sala tenham aula no mesmo horário
def existe_conflito(grade, professor, turma, sala, dia, horario, tipo_disciplina):
    if not professor_disponivel(professor, dia, horario) or not modalidade_aceita(professor, tipo_disciplina):
        return True
    for aula in grade[dia][horario]:
        if aula["Professor"] == professor["Nome"] or aula["Turma"] == turma or aula["Sala"] == sala:
            return True
    return False

# Gerar grade para todas as turmas
def gerar_grade_completa():
    professores = carregar_dados(ARQUIVO_PROFESSORES)
    disciplinas = carregar_dados(ARQUIVO_DISCIPLINAS)
    turmas = carregar_dados(ARQUIVO_TURMAS)
    salas = carregar_dados(ARQUIVO_SALAS)

    if professores.empty or disciplinas.empty or turmas.empty or salas.empty:
        print("Erro: Todos os dados precisam estar cadastrados!")
        return

    grade = criar_grade_vazia()

    # Agrupar as disciplinas pelas turmas que as cursam (turmas unificadas)
    disciplinas_comuns = {}
    for _, turma in turmas.iterrows():
        # O campo "Disciplinas" foi armazenado entre aspas (ex: "Programação I,Banco de Dados,Algoritmos")
        disciplinas_lista = turma["Disciplinas"].strip('"').split(",")
        for disciplina_nome in disciplinas_lista:
            disciplina_nome = disciplina_nome.strip()
            if disciplina_nome not in disciplinas_comuns:
                disciplinas_comuns[disciplina_nome] = []
            disciplinas_comuns[disciplina_nome].append(turma["Curso"])

    for disciplina_nome, turmas_com_disciplina in disciplinas_comuns.items():
        disciplina_df = disciplinas[disciplinas["Nome"] == disciplina_nome]
        if disciplina_df.empty:
            continue
        disciplina = disciplina_df.iloc[0]
        creditos = int(disciplina["Créditos_Semanais"])
        # Definir o tipo da disciplina com base no campo "Necessita_Lab": se True, usamos "Laboratório", caso contrário "Sala"
        tipo_disciplina = "Laboratório" if str(disciplina["Necessita_Lab"]).lower() == "true" else "Sala"

        # Filtrar os professores disponíveis para essa disciplina
        professores_disponiveis = professores[
            (professores["Área"].str.contains(disciplina["Área"], case=False, na=False)) &
            (professores["Modalidades"].str.contains(tipo_disciplina, case=False, na=False))
        ]
        if professores_disponiveis.empty:
            print(f"⚠️ Nenhum professor disponível para {disciplina_nome}")
            continue
        professor = professores_disponiveis.sample(1).iloc[0]

        # Filtrar as salas disponíveis para o tipo de disciplina
        if tipo_disciplina == "Laboratório":
            salas_disponiveis = salas[salas["Tipo"] == "Laboratório"]
        elif tipo_disciplina == "Sala":
            salas_disponiveis = salas[salas["Tipo"] == "Sala"]
        else:
            salas_disponiveis = salas

        if salas_disponiveis.empty:
            print(f"⚠️ Nenhuma sala disponível para {disciplina_nome}")
            continue
        sala = salas_disponiveis.sample(1).iloc[0]

        # Alocar cada crédito (bloco de aula) para cada turma que cursa a disciplina
        for _ in range(creditos):
            for turma_nome in turmas_com_disciplina:
                turma_df = turmas[turmas["Curso"] == turma_nome]
                if turma_df.empty:
                    continue
                turma_info = turma_df.iloc[0]
                # Use o novo campo "Periodo" que contém "Matutino" ou "Noturno"
                periodo_diario = turma_info["Periodo"].lower()
                if periodo_diario == "matutino":
                    horarios_disponiveis = HORARIOS_DIURNO
                elif periodo_diario == "noturno":
                    horarios_disponiveis = HORARIOS_NOTURNO
                else:
                    # Se o valor não for reconhecido, usa os horários diurnos por padrão
                    horarios_disponiveis = HORARIOS_DIURNO

                # Obter horários livres sem conflito
                horarios_livres = [
                    (d, h) for d in DIAS_SEMANA for h in horarios_disponiveis
                    if not existe_conflito(grade, professor, turma_nome, sala["Nome"], d, h, tipo_disciplina)
                ]
                if not horarios_livres:
                    print(f"⚠️ Não há horários suficientes para {disciplina_nome} ({turma_nome})")
                    continue
                dia, horario = random.choice(horarios_livres)
                grade[dia][horario].append({
                    "Disciplina": disciplina_nome,
                    "Professor": professor["Nome"],
                    "Sala": sala["Nome"],
                    "Turma": turma_nome
                })
                print(f"Aula de {disciplina_nome} com {professor['Nome']} para a turma {turma_nome} alocada em {sala['Nome']} no {dia} {horario}")

    # Verificar se cada professor tem pelo menos 2 aulas
    for _, professor in professores.iterrows():
        aulas_atribuidas = sum(
            1 for dia in grade for horario in grade[dia] for aula in grade[dia][horario]
            if aula["Professor"] == professor["Nome"]
        )
        if aulas_atribuidas < 2:
            print(f"⚠️ Professor {professor['Nome']} tem apenas {aulas_atribuidas} aulas.")

    # Criar tabela formatada para exibição
    tabela_grade = []
    for dia in DIAS_SEMANA:
        for horario in HORARIOS_DIURNO + HORARIOS_NOTURNO:
            aulas_no_horario = grade[dia][horario]
            if aulas_no_horario:
                for aula in aulas_no_horario:
                    tabela_grade.append([dia, horario, aula["Turma"], aula["Disciplina"], aula["Professor"], aula["Sala"]])
            else:
                tabela_grade.append([dia, horario, "-", "-", "-", "-"])

    df_grade = pd.DataFrame(tabela_grade, columns=["Dia", "Horário", "Turma", "Disciplina", "Professor", "Sala"])
    df_grade.to_csv("grade_completa.csv", index=False)
    print("\n✅ Grade horária completa gerada! Verifique 'grade_completa.csv'.\n")
    print(df_grade.to_string(index=False))
    return grade

# Executar
gerar_grade_completa()
