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

# Carregar dados do CSV
def carregar_dados(arquivo):
    return pd.read_csv(arquivo) if os.path.exists(arquivo) else pd.DataFrame()

# Criar grade horária vazia
def criar_grade_vazia():
    return {dia: {h: [] for h in HORARIOS_DIURNO + HORARIOS_NOTURNO} for dia in DIAS_SEMANA}

# Verifica se o professor está disponível no dia e horário
def professor_disponivel(professor, dia, horario):
    dias_disponiveis = professor["Dias_Disponiveis"].split(",") if isinstance(professor["Dias_Disponiveis"], str) else []
    horarios_disponiveis = professor["Horarios_Disponiveis"].split(",") if isinstance(professor["Horarios_Disponiveis"], str) else []
    return dia in dias_disponiveis and horario in horarios_disponiveis

# Verifica se a modalidade da disciplina é aceita pelo professor
def modalidade_aceita(professor, tipo_disciplina):
    modalidades_preferidas = professor["Modalidades_Preferidas"].split(",") if isinstance(professor["Modalidades_Preferidas"], str) else []
    return tipo_disciplina in modalidades_preferidas

# Verifica conflitos
def existe_conflito(grade, professor, turma, sala, dia, horario, tipo_disciplina):
    if not professor_disponivel(professor, dia, horario) or not modalidade_aceita(professor, tipo_disciplina):
        return True
    aulas_no_horario = grade[dia][horario]
    for aula in aulas_no_horario:
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

    # Identificar turmas unificadas
    disciplinas_comuns = {}
    for _, turma in turmas.iterrows():
        for disciplina_nome in turma["Disciplinas"].split(","):
            disciplina_nome = disciplina_nome.strip()
            if disciplina_nome not in disciplinas_comuns:
                disciplinas_comuns[disciplina_nome] = []
            disciplinas_comuns[disciplina_nome].append(turma["Curso"])

    for disciplina_nome, turmas_com_disciplina in disciplinas_comuns.items():
        disciplina = disciplinas[disciplinas["Nome"] == disciplina_nome]
        if disciplina.empty:
            continue
        disciplina = disciplina.iloc[0]
        creditos = int(disciplina["Créditos_Semanais"])
        tipo_disciplina = disciplina["Tipo_Disciplina"]

        # Filtrar professores
        professores_disponiveis = professores[
            (professores["Área"].str.contains(disciplina["Modalidade"], case=False, na=False)) &
            (professores["Modalidades_Preferidas"].str.contains(tipo_disciplina, case=False, na=False))
        ]

        if professores_disponiveis.empty:
            print(f"⚠️ Nenhum professor disponível para {disciplina_nome}")
            continue

        professor = professores_disponiveis.sample(1).iloc[0]

        # Filtrar salas
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

        # Alocar turmas
        for _ in range(creditos):
            for turma in turmas_com_disciplina:
                periodo = turmas[turmas["Curso"] == turma].iloc[0]["Periodo"]
                horarios_disponiveis = HORARIOS_DIURNO if periodo == "Diurno" else HORARIOS_NOTURNO

                horarios_livres = [
                    (d, h) for d in DIAS_SEMANA for h in horarios_disponiveis
                    if not existe_conflito(grade, professor, turma, sala["Nome"], d, h, tipo_disciplina)
                ]

                if not horarios_livres:
                    print(f"⚠️ Não há horários suficientes para {disciplina_nome} ({turma})")
                    continue

                dia, horario = random.choice(horarios_livres)
                grade[dia][horario].append({
                    "Disciplina": disciplina_nome,
                    "Professor": professor["Nome"],
                    "Sala": sala["Nome"],
                    "Turma": turma
                })

    # Verificar mínimo de aulas por professor
    for _, professor in professores.iterrows():
        aulas_atribuidas = sum(
            1 for dia in grade for horario in grade[dia] for aula in grade[dia][horario]
            if aula["Professor"] == professor["Nome"]
        )
        if aulas_atribuidas < 2:
            print(f"⚠️ Professor {professor['Nome']} tem apenas {aulas_atribuidas} aulas.")

    # Criar tabela formatada
    tabela_grade = []
    for dia in DIAS_SEMANA:
        for horario in HORARIOS_DIURNO + HORARIOS_NOTURNO:
            aulas_no_horario = grade[dia][horario]
            if aulas_no_horario:
                for aula in aulas_no_horario:
                    tabela_grade.append([  
                        dia, horario, aula["Turma"], aula["Disciplina"], aula["Professor"], aula["Sala"]
                    ])
            else:
                tabela_grade.append([dia, horario, "-", "-", "-", "-"])

    # Salvar e exibir
    df_grade = pd.DataFrame(tabela_grade, columns=["Dia", "Horário", "Turma", "Disciplina", "Professor", "Sala"])
    df_grade.to_csv("grade_completa.csv", index=False)
    print("\n✅ Grade horária completa gerada! Verifique 'grade_completa.csv'.")
    print("\n📅 GRADE HORÁRIA GERADA 📅\n")
    print(df_grade.to_string(index=False))

# Executar
gerar_grade_completa()
