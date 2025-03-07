import pandas as pd
import random
import os

# Arquivos CSV
ARQUIVO_PROFESSORES = "professores.csv"
ARQUIVO_DISCIPLINAS = "disciplinas.csv"
ARQUIVO_TURMAS = "turmas.csv"
ARQUIVO_SALAS = "salas.csv"

# Horários disponíveis para cada período
HORARIOS_DIURNO = ["07:30-08:20", "08:20-09:10", "09:30-10:20", "10:20-11:10"]
HORARIOS_NOTURNO = ["19:10-20:00", "20:00-20:50", "21:00-21:50", "21:50-22:40"]
DIAS_SEMANA = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"]

# Função para carregar dados do CSV
def carregar_dados(arquivo):
    return pd.read_csv(arquivo) if os.path.exists(arquivo) else pd.DataFrame()

# Cria uma grade vazia: dicionário com dia -> horário -> lista de sessões
def criar_grade_vazia():
    return {dia: {h: [] for h in HORARIOS_DIURNO + HORARIOS_NOTURNO} for dia in DIAS_SEMANA}

# Verifica se o professor está disponível no dia e período (Matutino ou Noturno)
# O campo "Disponibilidade" do professor deve estar no formato "Seg-Matutino,Ter-Noturno,Qua-Matutino", etc.
def professor_disponivel(professor, dia, periodo):
    disponibilidade = professor["Disponibilidade"].split(",") if isinstance(professor["Disponibilidade"], str) else []
    for disp in disponibilidade:
        partes = disp.strip().split("-")
        if len(partes) == 2:
            dia_prof, per_prof = partes
            if dia.startswith(dia_prof.strip()[:3]) and per_prof.strip().capitalize() == periodo:
                return True
    return False

# Verifica se a modalidade da disciplina é aceita pelo professor
def modalidade_aceita(professor, modalidade_disciplina):
    mod = professor["Modalidades"].split(",") if isinstance(professor["Modalidades"], str) else []
    mod = [m.strip().lower() for m in mod]
    return modalidade_disciplina.strip().lower() in mod

# Verifica se há conflito: se já existe uma aula no mesmo dia e horário com o mesmo professor ou mesma sala
def existe_conflito(grade, professor_nome, turma, sala, dia, horario):
    for aula in grade[dia][horario]:
        if aula["Professor"] == professor_nome or aula["Sala"] == sala:
            return True
    return False

# Função para gerar a grade de aulas
def gerar_grade_completa():
    professores = carregar_dados(ARQUIVO_PROFESSORES)
    disciplinas_df = carregar_dados(ARQUIVO_DISCIPLINAS)
    turmas = carregar_dados(ARQUIVO_TURMAS)
    salas = carregar_dados(ARQUIVO_SALAS)
    
    if professores.empty or disciplinas_df.empty or turmas.empty or salas.empty:
        print("Erro: Todos os dados precisam estar cadastrados!")
        return
    
    grade = criar_grade_vazia()
    registros = []  # Lista para armazenar cada sessão alocada
    
    # Para cada turma, alocar cada disciplina em um único dia da semana
    for _, turma in turmas.iterrows():
        curso = turma["Curso"]
        semestre = turma["Semestre"]
        periodo_turma = turma["Periodo"].strip().capitalize()  # "Matutino" ou "Noturno"
        qtd_alunos = int(turma["Quantidade_Alunos"])
        # Obter a lista de disciplinas (removendo aspas se houver)
        disciplinas_lista = turma["Disciplinas"].strip('"').split(",")
        
        for disciplina_nome in disciplinas_lista:
            disciplina_nome = disciplina_nome.strip()
            disc_sel = disciplinas_df[disciplinas_df["Nome"] == disciplina_nome]
            if disc_sel.empty:
                print(f"⚠️ Disciplina {disciplina_nome} não encontrada para a turma {curso}.")
                continue

            disciplina = disc_sel.iloc[0]
            creditos = int(disciplina["Créditos_Semanais"])
            # Definir o tipo de sala necessário: se Necessita_Lab for true, usa "Laboratório"; caso contrário, "Sala"
            tipo_sala = "Laboratório" if str(disciplina["Necessita_Lab"]).strip().lower() == "true" else "Sala"
            modalidade_disciplina = disciplina["Modalidade"]  # Ex: "Presencial"
            
            # Filtrar professores disponíveis: professor pode lecionar se sua área é igual à área da disciplina ou for "Ambos"
            # e se suas modalidades incluem a modalidade da disciplina.
            professores_disponiveis = professores[
                professores["Área"].apply(lambda x: x.strip().lower() == disciplina["Área"].strip().lower() or x.strip().lower() == "ambos") &
                professores["Modalidades"].apply(lambda x: modalidade_disciplina.strip().lower() in [m.strip().lower() for m in x.split(",")])
            ]

            if professores_disponiveis.empty:
                print(f"⚠️ Nenhum professor disponível para {disciplina_nome} na turma {curso}.")
                continue
            # Embaralhar os professores disponíveis para variar a alocação
            professores_disponiveis = professores_disponiveis.sample(frac=1).reset_index(drop=True)
            
            professor_alocado = None
            dia_alocado = None
            # Escolher um dia em que algum professor disponível esteja livre, conforme sua disponibilidade no período da turma
            dias_possiveis = DIAS_SEMANA.copy()
            random.shuffle(dias_possiveis)
            for dia in dias_possiveis:
                for _, prof in professores_disponiveis.iterrows():
                    if professor_disponivel(prof, dia, periodo_turma):
                        professor_alocado = prof
                        dia_alocado = dia
                        break
                if professor_alocado is not None:
                    break
            if professor_alocado is None or dia_alocado is None:
                print(f"⚠️ Nenhum professor com disponibilidade para {disciplina_nome} na turma {curso}.")
                continue
            
            # Selecionar uma sala do tipo requerido com capacidade suficiente
            salas_possiveis = salas[salas["Tipo"].str.strip().str.lower() == tipo_sala.strip().lower()]
            salas_possiveis = salas_possiveis[salas_possiveis["Capacidade"].astype(int) >= qtd_alunos]
            if salas_possiveis.empty:
                print(f"⚠️ Nenhuma {tipo_sala} com capacidade suficiente para {disciplina_nome} na turma {curso}.")
                continue
            sala_alocada = salas_possiveis.sample(1).iloc[0]
            
            # Selecionar os horários para alocar todos os créditos da disciplina naquele dia_alocado e período da turma
            lista_horarios = HORARIOS_DIURNO.copy() if periodo_turma == "Matutino" else HORARIOS_NOTURNO.copy()
            random.shuffle(lista_horarios)
            if len(lista_horarios) < creditos:
                print(f"⚠️ Não há horários suficientes para alocar {creditos} créditos de {disciplina_nome} na turma {curso} no dia {dia_alocado}.")
                continue
            horarios_alocados = []
            for horario in lista_horarios:
                # Verificar se já há conflito: professor ou sala já alocados naquele horário para outro turno
                if not existe_conflito(grade, professor_alocado["Nome"], curso, sala_alocada["Nome"], dia_alocado, horario):
                    horarios_alocados.append(horario)
                    if len(horarios_alocados) == creditos:
                        break
            if len(horarios_alocados) < creditos:
                print(f"⚠️ Não foi possível alocar todos os {creditos} créditos para {disciplina_nome} na turma {curso} no dia {dia_alocado}.")
                continue
            
            # Alocar cada sessão na grade e registrar a alocação
            for horario in horarios_alocados:
                grade[dia_alocado][horario].append({ 
                    "Disciplina": disciplina_nome,
                    "Professor": professor_alocado["Nome"],
                    "Sala": sala_alocada["Nome"],
                    "Turma": curso
                })
                registros.append({
                    "Curso": curso,
                    "Semestre": semestre,
                    "Disciplina": disciplina_nome,
                    "Professor": professor_alocado["Nome"],
                    "Sala": sala_alocada["Nome"],
                    "Dia": dia_alocado,
                    "Horário": horario,
                    "Período": periodo_turma
                })
            print(f"✅ {disciplina_nome} da turma {curso} alocada no dia {dia_alocado} com {professor_alocado['Nome']} em {sala_alocada['Nome']} nos horários: {', '.join(horarios_alocados)}")
    
    # Criar DataFrame com a grade completa, ordenado por dia e horário
    df_grade = pd.DataFrame(registros)
    if not df_grade.empty:
        df_grade = df_grade.sort_values(by=["Curso", "Dia", "Horário"])
        df_grade.to_csv("grade_completa.csv", index=False)
        print("\n✅ Grade horária completa gerada! Verifique 'grade_completa.csv'.\n")
        print(df_grade.to_string(index=False))
    else:
        print("Nenhuma aula foi alocada.")
    return grade

# Executar a geração da grade
gerar_grade_completa()