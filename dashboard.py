import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.figure_factory as ff
from datetime import datetime, timedelta
import uuid
import re  # Do sprawdzania kryteriów

# --- Konfiguracja strony ---
st.set_page_config(layout="wide", page_title="Garnexpol System Motywacji Garncarzy")

# --- Dane ---
sample_employees = [
    {"id": "E001", "name": "Janusz Lipka", "department": "Zarząd", "role": "Właściciel"},
    {"id": "E002", "name": "Piotr Lipka", "department": "Sprzedaż", "role": "Kierownik działu sprzedaży"},
    {"id": "E003", "name": "Grażyna Lipka", "department": "Marketing", "role": "Koordynator marketingu"},
    {"id": "E004", "name": "Andrzej Lipka", "department": "Magazyn", "role": "Koordynator magazynu"},
    {"id": "E005", "name": "Anna Kowalska", "department": "Sprzedaż", "role": "Specjalista ds. sprzedaży"},
    {"id": "E006", "name": "Marek Nowak", "department": "Marketing", "role": "Specjalista ds. marketingu"},
    {"id": "E007", "name": "Katarzyna Zając", "department": "Magazyn", "role": "Magazynier"},
    {"id": "E008", "name": "Tomasz Wójcik", "department": "Sprzedaż", "role": "Młodszy specjalista ds. sprzedaży"},
    {"id": "E009", "name": "Grzegorz Draun", "department": "Marketing", "role": "Specjalista ds. marketingu"},
    {"id": "E010", "name": "Rafał Buchający", "department": "Sprzedaż", "role": "Przedstawiciel handlowy"},
    {"id": "E011", "name": "Karol Nawrotki", "department": "Magazyn", "role": "Starszy magazynier"},
]

employee_performance_data = {
    "E001": {
        "staż_pracy_lata": 20,
        "subiektywna_ocena_przełożonego": "Wzorowa",
    },
    "E002": {
        "staż_pracy_lata": 10,
        "target_achievement_avg_dept": "105%",
        "zarzadzanie_zespolem_ocena": "Bardzo dobra"
    },
    "E005": {
        "staż_pracy_lata": 3,
        "target_achievement_percentage": 115,
        "target_achievement_avg_YTD": 108,
        "conversion_rate": 28,
        "positive_customer_feedback_count": 22,
        "complaints_count": 1,
        "trainings_completed_count": 3,
        "trainings_list": ["Zaawansowane techniki sprzedaży", "Negocjacje handlowe", "Obsługa systemu CRM"],
        "deklaracja_chęci_awansu": True,
        "subiektywna_ocena_przełożonego": "Bardzo dobra"
    },
    "E006": {
        "staż_pracy_lata": 2.5,
        "campaign_results_roi": "150%",
        "kpi_realization_rate": 95,
        "completed_courses_count": 2,
        "courses_list": ["Google Analytics Advanced", "Meta Ads Pro"],
        "deklaracja_chęci_awansu": True,
        "subiektywna_ocena_przełożonego": "Dobra"
    },
    "E007": {
        "staż_pracy_lata": 4,
        "order_accuracy_rate": 99.5,
        "internal_trainings_completed_count": 2,
        "internal_trainings_list": ["BHP Magazynowe", "Obsługa wózka widłowego"],
        "deklaracja_chęci_awansu": False,
        "subiektywna_ocena_przełożonego": "Dobra"
    },
    "E008": {
        "staż_pracy_lata": 0.8,
        "target_achievement_percentage": 95,
        "target_achievement_avg_YTD": 92,
        "conversion_rate": 15,
        "positive_customer_feedback_count": 5,
        "complaints_count": 0,
        "trainings_completed_count": 1,
        "trainings_list": ["Podstawy sprzedaży"],
        "deklaracja_chęci_awansu": True,
        "subiektywna_ocena_przełożonego": "Zadowalająca, z potencjałem"
    },
    "E009": {  # Grzegorz Draun - Marketing
        "staż_pracy_lata": 1.5,
        "campaign_results_roi": "120%",
        "kpi_realization_rate": 90,
        "completed_courses_count": 1,
        "courses_list": ["Content Marketing Basics"],
        "deklaracja_chęci_awansu": True,
        "subiektywna_ocena_przełożonego": "Dobra"
    },
    "E010": {  # Rafał Buchający - Sprzedaż
        "staż_pracy_lata": 2,
        "target_achievement_percentage": 105,
        "target_achievement_avg_YTD": 102,
        "conversion_rate": 22,
        "positive_customer_feedback_count": 18,
        "complaints_count": 2,
        "trainings_completed_count": 2,
        "trainings_list": ["Obsługa klienta premium", "Prezentacje handlowe"],
        "deklaracja_chęci_awansu": True,
        "subiektywna_ocena_przełożonego": "Dobra"
    },
    "E011": {  # Karol Nawrotki - Magazyn
        "staż_pracy_lata": 5,
        "order_accuracy_rate": 99.8,
        "internal_trainings_completed_count": 3,
        "internal_trainings_list": ["BHP", "Wózek widłowy", "System WMS"],
        "deklaracja_chęci_awansu": True,
        "subiektywna_ocena_przełożonego": "Bardzo dobra"
    }
}

departments = sorted(list(set([e["department"] for e in sample_employees])))
roles_by_department = {
    "Sprzedaż": ["Młodszy specjalista ds. sprzedaży", "Specjalista ds. sprzedaży", "Starszy specjalista ds. sprzedaży",
                 "Kierownik zespołu sprzedażowego", "Manager regionalny"],
    "Marketing": ["Młodszy specjalista ds. marketingu", "Specjalista ds. marketingu",
                  "Starszy specjalista ds. marketingu", "Kierownik zespołu marketingowego"],
    "Magazyn": ["Magazynier", "Starszy magazynier", "Kierownik magazynu", "Specjalista ds. logistyki"],
    "Administracja": ["Koordynator biura"],
    "Zarząd": ["Właściciel", "Kierownik działu"]
}
competencies_list = [
    {"id": "comp1", "name": "Odporność na stres",
     "description": "Umiejętność zachowania spokoju i skutecznego działania w sytuacjach presji, napięcia lub niepewności."},
    {"id": "comp2", "name": "Myślenie krytyczne",
     "description": "Zdolność do logicznej analizy informacji, oceny argumentów i wyciągania trafnych wniosków na podstawie faktów."},
    {"id": "comp3", "name": "Komunikacja",
     "description": "Umiejętność jasnego, zrozumiałego i adekwatnego przekazywania informacji oraz aktywnego słuchania."},
    {"id": "comp4", "name": "Autoprezentacja",
     "description": "Zdolność do świadomego i pozytywnego przedstawiania swojej osoby oraz oferowanych usług lub rozwiązań."},
    {"id": "comp5", "name": "Konwersja",
     "description": "Umiejętność skutecznego przekształcania podejmowanych działań w realne wyniki sprzedażowe."},
    {"id": "comp6", "name": "Transparentność",
     "description": "Postawa oparta na otwartości, szczerości i jasnej komunikacji."},
    {"id": "comp7", "name": "Chęć rozwoju",
     "description": "Motywacja do ciągłego uczenia się, poszukiwania nowych wyzwań i podnoszenia własnych kwalifikacji."},
    {"id": "comp8", "name": "Sumienność",
     "description": "Dokładność, systematyczność i odpowiedzialność w realizacji zadań i zobowiązań."},
    {"id": "comp9", "name": "Zaangażowanie i pasja",
     "description": "Wewnętrzna motywacja, entuzjazm oraz aktywna postawa wobec wykonywanych zadań."}
]
competency_names = [c["name"] for c in competencies_list]
advancement_criteria = {
    "Ogólne": [
        "Staż pracy", "Regularne osiągnięcia przekraczające założony target",
        "Pozytywna ocena arkusza kompetencji i potrzeb rozwojowych",
        "Zaangażowanie w pracę", "Chęć awansu - osiągnięcie pełnego potencjału na aktualnym stanowisku",
        "Subiektywna ocena przełożonego (na podstawie cotygodniowych spotkań)"
    ],
    "Kierownicze": [
        "Umiejętność zarządzania ludźmi", "Samodzielność i odpowiedzialność", "Zdolność do rozwiązywania problemów",
        "Umiejętność komunikacji i budowania autorytetu", "Odporność na stres",
        "Zaufanie przełożonych i autorytet wśród współpracowników", "Rozumienie celów firmy i myślenie strategiczne"
    ],
    "Sprzedaż": [
        "Znajomość pełnego zakresu zadań specjalisty ds. sprzedaży", "Minimum rok pracy na obecnym stanowisku",
        "Regularne osiąganie targetów (miesięcznych planów sprzedaży)",
        "Utrzymywanie wysokiego poziomu konwersji (z leada na klienta)",
        "Pozytywne opinie od klientów", "Niska liczba reklamacji lub skuteczne rozwiązywanie problemów",
        "Skuteczność w prowadzeniu rozmów handlowych (telefonicznych i bezpośrednich)",
        "Umiejętność argumentacji wartości oferty",
        "Profesjonalna autoprezentacja oraz prowadzenie prezentacji i spotkań z klientami",
        "Doskonała wiedza o ofercie i rynku",
        "Umiejętność dopasowania oferty do potrzeb klienta", "Terminowość i skuteczność w planowaniu dnia pracy",
        "Chęć nauki i rozwoju, udział w szkoleniach, deklaracja i gotowość do objęcia nowych obowiązków",
        "Skuteczna współpraca z innymi działami", "Odporność na stres"
    ],
    "Marketing": [
        "Znajomość pełnego zakresu zadań specjalisty ds. marketingu", "Minimum rok pracy na obecnym stanowisku",
        "Udokumentowane wyniki kampanii (wzrost wejść na stronę, wzrost sprzedaży i zaangażowania)",
        "Realizacja KPI (liczba pozyskanych klientów, koszt pozyskania potencjalnych klientów)",
        "Inicjatywa w tworzeniu skutecznych strategii marketingowych i ich wdrażaniu",
        "Umiejętność myślenia strategicznego",
        "Znajomość narzędzi (np. Google Analytics, Meta Ads, CRM)",
        "Umiejętność analizowania danych i wyciągania wniosków",
        "Ukończone kursy/szkolenia branżowe (np. z performance marketingu, automatyzacji)",
        "Skuteczna współpraca z innymi działami",
        "Chęć nauki i rozwoju, deklaracja i gotowość do objęcia nowych obowiązków",
        "Rzetelność, sumienność, komunikatywność i terminowość",
        "Gotowość do zarządzania projektami, budżetem i zespołem",
        "Sprawna i terminowa reakcja na zgłoszenia klientów (np. reklamacja, zapytania, uwagi)"
    ],
    "Magazyn": [
        "Znajomość pełnego zakresu zadań magazyniera", "Minimum rok pracy na obecnym stanowisku",
        "Przestrzeganie terminów i efektywne zarządzanie czasem",
        "Wysoka wydajność (brak błędów w kompletacji zamówień, brak zniszczeń zamówień)",
        "Znajomość procedur logistycznych i BHP", "Umiejętność pracy zespołowej i komunikatywność",
        "Chęć nauki i rozwoju, deklaracja i gotowość do objęcia nowych obowiązków", "Zachowywanie porządku",
        "Zaangażowanie, punktualność i rzetelność",
        "Ukończone szkolenia wewnętrzne lub zewnętrzne (np. na operatora wózka widłowego, szkolenia BHP, kursy doszkalające)",
        "Gotowość do pracy w systemie zmianowym", "Dobra opinia wśród współpracowników i przełożonych"
    ]
}
advancement_criteria["Kierownicze"] = advancement_criteria["Ogólne"] + advancement_criteria["Kierownicze"]

# --- Inicjalizacja Session State ---
if 'assessments' not in st.session_state: st.session_state.assessments = []
if 'idps' not in st.session_state: st.session_state.idps = []
if 'tasks' not in st.session_state:
    st.session_state.tasks = [
        {"id": str(uuid.uuid4()), "name": "Przygotowanie raportu kwartalnego", "assignee": "Anna Kowalska",
         "status": "W trakcie", "progress": 75, "priority": "Wysoki",
         "deadline": datetime.now().date() + timedelta(days=10),
         "start_date": datetime.now().date() - timedelta(days=5)},
        {"id": str(uuid.uuid4()), "name": "Organizacja kampanii marketingowej XYZ", "assignee": "Marek Nowak",
         "status": "Do zrobienia", "progress": 10, "priority": "Wysoki",
         "deadline": datetime.now().date() + timedelta(days=30), "start_date": datetime.now().date()},
    ]
if 'task_to_edit_id' not in st.session_state: st.session_state.task_to_edit_id = None
if 'editing_task' not in st.session_state: st.session_state.editing_task = False


# --- Funkcje Pomocnicze ---
def calculate_average_competency_score(employee_id, assessments_list):
    """Oblicza średnią ocenę kompetencji dla pracownika."""
    employee_assessments = [a for a in assessments_list if a["employee_id"] == employee_id]
    if not employee_assessments:
        return None

    # Preferuj ostatnią ocenę przełożonego
    supervisor_assessments = sorted(
        [a for a in employee_assessments if a["assessor_type"] == "Ocena przełożonego"],
        key=lambda x: x["date"], reverse=True
    )
    if supervisor_assessments:
        latest_assessment = supervisor_assessments[0]
    else:  # Jeśli brak oceny przełożonego, weź ostatnią jakąkolwiek
        latest_assessment = sorted(employee_assessments, key=lambda x: x["date"], reverse=True)[0]

    ratings = latest_assessment["ratings"].values()
    if ratings:
        return round(sum(ratings) / len(ratings), 2)
    return None


def check_criterion_status(criterion_text, employee_obj, performance_data, avg_comp_score):
    """Sprawdza status spełnienia kryterium przez pracownika."""
    text = criterion_text.lower()
    status = "N/A"
    details = ""

    # Ogólne
    if "staż pracy" in text or "minimum rok pracy" in text:
        min_years_match = re.search(r"minimum (\w+) rok", text)
        min_years = 1
        if min_years_match:
            # Prosta konwersja słów na liczby, można rozbudować
            year_words = {"rok": 1, "dwa": 2, "trzy": 3}  # Uproszczone
            if min_years_match.group(1) in year_words:
                min_years = year_words[min_years_match.group(1)]

        staz = performance_data.get("staż_pracy_lata", 0)
        if staz >= min_years:
            status = "✅ Spełnione"
        else:
            status = f"❌ Niespełnione (Staż: {staz}l, Wymagane: {min_years}l)"
        return status

    if "pozytywna ocena arkusza kompetencji" in text:
        if avg_comp_score is not None:
            if avg_comp_score >= 5.0:  # Przykładowy próg dla "pozytywnej"
                status = f"✅ Spełnione (Śr. {avg_comp_score}/7)"
            elif avg_comp_score >= 4.0:
                status = f"⚠️ Częściowo (Śr. {avg_comp_score}/7)"
            else:
                status = f"❌ Wymaga poprawy (Śr. {avg_comp_score}/7)"
        else:
            status = "Brak ocen"
        return status

    if "chęć awansu" in text or "deklaracja i gotowość" in text:
        chce_awans = performance_data.get("deklaracja_chęci_awansu")
        if chce_awans is True:
            status = "✅ Spełnione (Deklaracja: Tak)"
        elif chce_awans is False:
            status = "❌ Niespełnione (Deklaracja: Nie)"
        else:
            status = "Brak deklaracji"
        return status

    if "subiektywna ocena przełożonego" in text:
        ocena_przelozonego = performance_data.get("subiektywna_ocena_przełożonego", "N/A")
        status = f"ℹ️ Info (Ocena: {ocena_przelozonego})"  # To jest bardziej informacyjne
        return status

    # Sprzedaż
    if "regularne osiąganie targetów" in text:
        target_ytd = performance_data.get("target_achievement_avg_YTD")
        if target_ytd is not None:
            if target_ytd >= 100:
                status = f"✅ Spełnione (Śr. YTD: {target_ytd}%)"
            elif target_ytd >= 90:
                status = f"⚠️ Częściowo (Śr. YTD: {target_ytd}%)"
            else:
                status = f"❌ Wymaga poprawy (Śr. YTD: {target_ytd}%)"
        else:
            status = "Brak danych YTD"
        return status

    if "poziomu konwersji" in text:
        konwersja = performance_data.get("conversion_rate")
        if konwersja is not None:
            # Załóżmy próg np. 20% dla specjalisty
            if konwersja >= 20:
                status = f"✅ Spełnione ({konwersja}%)"
            else:
                status = f"❌ Wymaga poprawy ({konwersja}%)"
        else:
            status = "Brak danych"
        return status

    if "pozytywne opinie od klientów" in text:
        opinie = performance_data.get("positive_customer_feedback_count", 0)
        if opinie >= 10:
            status = f"✅ Spełnione ({opinie} opinii)"  # Przykładowy próg
        else:
            status = f"ℹ️ Info ({opinie} opinii)"
        return status

    if "niska liczba reklamacji" in text:
        reklamacje = performance_data.get("complaints_count")
        if reklamacje is not None:
            if reklamacje <= 2:
                status = f"✅ Spełnione ({reklamacje} reklamacji)"  # Przykładowy próg
            else:
                status = f"❌ Wymaga uwagi ({reklamacje} reklamacji)"
        else:
            status = "Brak danych"
        return status

    # Marketing
    if "udokumentowane wyniki kampanii" in text or "realizacja kpi" in text:
        roi = performance_data.get("campaign_results_roi")
        kpi_rate = performance_data.get("kpi_realization_rate")
        if roi or kpi_rate:
            res_str = []
            if roi: res_str.append(f"ROI: {roi}")
            if kpi_rate: res_str.append(f"KPI: {kpi_rate}%")
            status = f"✅ Info ({', '.join(res_str)})"  # Traktujemy jako informację do oceny
        else:
            status = "Brak danych"
        return status

    # Magazyn
    if "wysoka wydajność" in text or "brak błędów" in text:
        accuracy = performance_data.get("order_accuracy_rate")
        if accuracy is not None:
            if accuracy >= 99.0:
                status = f"✅ Spełnione ({accuracy}%)"
            else:
                status = f"❌ Wymaga poprawy ({accuracy}%)"
        else:
            status = "Brak danych"
        return status

    if "ukończone szkolenia" in text or "ukończone kursy" in text:
        szkolenia_count_keys = ["trainings_completed_count", "completed_courses_count",
                                "internal_trainings_completed_count"]
        count = 0
        for key in szkolenia_count_keys:
            if key in performance_data:
                count = performance_data[key]
                break
        if count > 0:
            status = f"✅ Spełnione (Liczba: {count})"
        else:
            status = f"❌ Brak"
        return status

    return status  # Domyślnie N/A jeśli nie pasuje do żadnego


# --- Nawigacja ---
st.sidebar.title("Menu")
selected_module = st.sidebar.radio("Wybierz moduł:",
                                   ["Arkusz Oceny Kompetencji", "Arkusz Potrzeb Rozwojowych (IPR)",
                                    "Arkusz Poziomu Realizacji Zadań", "Kryteria Awansu"])

# --- Moduł 1: Arkusz Oceny Kompetencji ---
if selected_module == "Arkusz Oceny Kompetencji":
    st.header("📝 Arkusz Oceny Kompetencji")
    col1, col2 = st.columns([1, 2])
    with col1:  # Formularz oceny
        st.subheader("Wprowadź Ocenę")
        employee_names = [e["name"] for e in sample_employees]
        selected_employee_name_comp = st.selectbox("Pracownik:", employee_names, key="comp_employee_select")
        selected_employee_obj_comp = next(e for e in sample_employees if e["name"] == selected_employee_name_comp)
        assessor_type_comp = st.radio("Oceniający:", ["Ocena własna (Pracownik)", "Ocena przełożonego"],
                                      key="comp_assessor_type")
        assessment_date_comp = st.date_input("Data oceny:", datetime.now().date(), key="comp_date")
        ratings_comp = {}
        for comp in competencies_list:
            slider_key = f"comp_rating_{selected_employee_obj_comp['id']}_{assessor_type_comp}_{comp['id']}_{str(assessment_date_comp)}"
            st.markdown(f"**{comp['name']}**")
            st.caption(comp['description'])
            ratings_comp[comp['name']] = st.slider("Ocena (1-7):", 1, 7, 4, key=slider_key,
                                                   label_visibility="collapsed")
        strengths_comp = st.text_area("Mocne strony:",
                                      key=f"comp_strengths_{selected_employee_obj_comp['id']}_{assessor_type_comp}_{str(assessment_date_comp)}")
        dev_areas_comp = st.text_area("Obszary do rozwoju:",
                                      key=f"comp_dev_areas_{selected_employee_obj_comp['id']}_{assessor_type_comp}_{str(assessment_date_comp)}")
        comments_comp = st.text_area("Dodatkowe komentarze:",
                                     key=f"comp_comments_{selected_employee_obj_comp['id']}_{assessor_type_comp}_{str(assessment_date_comp)}")
        if st.button("Zapisz Ocenę Kompetencji", key="comp_save"):
            assessment_id = str(uuid.uuid4())
            st.session_state.assessments.append({
                "id": assessment_id, "employee_id": selected_employee_obj_comp["id"],
                "employee_name": selected_employee_name_comp,
                "assessor_type": assessor_type_comp, "date": assessment_date_comp, "ratings": ratings_comp,
                "strengths": strengths_comp, "dev_areas": dev_areas_comp, "comments": comments_comp
            })
            st.success(f"Ocena dla {selected_employee_name_comp} została zapisana!")
    with col2:  # Wyświetlanie zapisanych ocen
        st.subheader("Zapisane Oceny i Profil Kompetencji")
        if not st.session_state.assessments:
            st.info("Brak zapisanych ocen.")
        else:
            employee_names_with_assessments = sorted(
                list(set([a["employee_name"] for a in st.session_state.assessments])))
            if not employee_names_with_assessments:
                st.info("Brak ocen do wyświetlenia.")
            else:
                view_employee_name_comp = st.selectbox("Wyświetl oceny dla:", employee_names_with_assessments,
                                                       key="comp_view_employee")
                assessments_for_employee = [a for a in st.session_state.assessments if
                                            a["employee_name"] == view_employee_name_comp]
                if not assessments_for_employee:
                    st.warning(f"Brak ocen dla {view_employee_name_comp}")
                else:
                    assessment_options = {f"{a['date']} - {a['assessor_type']} (ID: {a['id'][:8]})": a['id'] for a in
                                          sorted(assessments_for_employee, key=lambda x: x['date'], reverse=True)}
                    selected_assessment_label_comp = st.selectbox("Wybierz ocenę:", list(assessment_options.keys()),
                                                                  key="comp_view_assessment_select")
                    if selected_assessment_label_comp:
                        selected_assessment_id_comp = assessment_options[selected_assessment_label_comp]
                        assessment_to_display = next(
                            a for a in assessments_for_employee if a["id"] == selected_assessment_id_comp)
                        st.markdown(
                            f"#### Profil dla: {assessment_to_display['employee_name']} ({assessment_to_display['date']} - {assessment_to_display['assessor_type']})")
                        radar_data = assessment_to_display['ratings']
                        fig = go.Figure(data=[
                            go.Scatterpolar(r=list(radar_data.values()) + [list(radar_data.values())[0]],
                                            theta=list(radar_data.keys()) + [list(radar_data.keys())[0]],
                                            fill='toself')])
                        fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[1, 7])),
                                          title="Profil Kompetencji")
                        st.plotly_chart(fig, use_container_width=True)
                        exp = st.expander("Szczegóły Oceny (mocne strony, obszary rozwoju, komentarze)")
                        exp.write(f"**Mocne strony:** {assessment_to_display['strengths'] or 'Nie podano.'}")
                        exp.write(f"**Obszary do rozwoju:** {assessment_to_display['dev_areas'] or 'Nie podano.'}")
                        exp.write(f"**Komentarze:** {assessment_to_display['comments'] or 'Nie podano.'}")

                        # Uproszczony widok historyczny
                        if len(assessments_for_employee) > 1:
                            st.markdown("---")
                            st.markdown("##### Historia wybranej kompetencji")
                            selected_comp_for_history = st.selectbox("Wybierz kompetencję do śledzenia:",
                                                                     competency_names, key="comp_history_select")
                            history_data = {"dates": [], "scores": []}
                            for assess_hist in sorted(assessments_for_employee,
                                                      key=lambda x: x['date']):  # Sortuj chronologicznie
                                if selected_comp_for_history in assess_hist["ratings"]:
                                    history_data["dates"].append(assess_hist["date"])
                                    history_data["scores"].append(assess_hist["ratings"][selected_comp_for_history])
                            if len(history_data["dates"]) > 1:
                                fig_hist = go.Figure(data=[go.Scatter(x=history_data["dates"], y=history_data["scores"],
                                                                      mode='lines+markers')])
                                fig_hist.update_layout(title=f"Historia ocen dla: {selected_comp_for_history}",
                                                       xaxis_title="Data Oceny", yaxis_title="Ocena (1-7)",
                                                       yaxis=dict(range=[1, 7]))
                                st.plotly_chart(fig_hist, use_container_width=True)
                            elif len(history_data["dates"]) == 1:
                                st.info("Dostępna tylko jedna ocena dla tej kompetencji.")
                            else:
                                st.info("Brak historii dla wybranej kompetencji.")


# --- Moduł 2: Arkusz Potrzeb Rozwojowych (IPR) ---
elif selected_module == "Arkusz Potrzeb Rozwojowych (IPR)":
    st.header("🌱 Arkusz Potrzeb Rozwojowych (Indywidualny Plan Rozwoju)")
    # (Logika IPR bez zmian w tej iteracji, pozostaje jak w poprzedniej wersji)
    col1_idp, col2_idp = st.columns([1, 2])
    with col1_idp:
        st.subheader("Wprowadź Plan Rozwoju")
        employee_names_idp = [e["name"] for e in sample_employees]
        selected_employee_name_idp = st.selectbox("Pracownik:", employee_names_idp, key="idp_employee_select")
        selected_employee_obj_idp = next(e for e in sample_employees if e["name"] == selected_employee_name_idp)
        form_type_idp = st.radio("Wersja formularza:", ["Plan pracownika", "Plan przełożonego"], key="idp_form_type")
        plan_date_idp = st.date_input("Data planu:", datetime.now().date(), key="idp_date")
        st.markdown("#### Cele Rozwojowe")
        short_term_goals = st.text_area("Krótkoterminowe:", height=100,
                                        key=f"idp_short_goals_{selected_employee_obj_idp['id']}_{form_type_idp}")
        long_term_goals = st.text_area("Długoterminowe:", height=100,
                                       key=f"idp_long_goals_{selected_employee_obj_idp['id']}_{form_type_idp}")
        st.markdown("#### Działania Rozwojowe")
        needed_trainings = st.text_area("Potrzebne szkolenia:", height=100,
                                        key=f"idp_trainings_{selected_employee_obj_idp['id']}_{form_type_idp}")
        dev_actions = st.text_area("Inne działania:", height=100,
                                   key=f"idp_actions_{selected_employee_obj_idp['id']}_{form_type_idp}")
        timeframes = st.text_input("Ramy czasowe:",
                                   key=f"idp_timeframes_{selected_employee_obj_idp['id']}_{form_type_idp}")
        st.markdown("#### Informacje Dodatkowe")
        company_dev_directions = st.text_area("Kierunki rozwoju firmy (kontekst):", height=100,
                                              key=f"idp_company_dev_{selected_employee_obj_idp['id']}_{form_type_idp}")
        difficulties = st.text_area("Przewidywane trudności:", height=100,
                                    key=f"idp_difficulties_{selected_employee_obj_idp['id']}_{form_type_idp}")
        dev_since_last = st.radio("Rozwój od ostatniej oceny?", ("Tak", "Nie", "Nie dotyczy"),
                                  key=f"idp_dev_last_{selected_employee_obj_idp['id']}_{form_type_idp}")
        time_for_dev = st.text_input("Czas na rozwój (np. godz./tydzień):",
                                     key=f"idp_time_alloc_{selected_employee_obj_idp['id']}_{form_type_idp}")
        readiness_new_duties = st.checkbox("Gotowość na nowe obowiązki",
                                           key=f"idp_readiness_{selected_employee_obj_idp['id']}_{form_type_idp}")
        if st.button("Zapisz Plan Rozwoju", key="idp_save"):
            idp_id = str(uuid.uuid4())
            st.session_state.idps.append({
                "id": idp_id, "employee_id": selected_employee_obj_idp["id"],
                "employee_name": selected_employee_name_idp,
                "form_type": form_type_idp, "plan_date": plan_date_idp, "short_term_goals": short_term_goals,
                "long_term_goals": long_term_goals, "needed_trainings": needed_trainings, "dev_actions": dev_actions,
                "timeframes": timeframes, "company_dev_directions": company_dev_directions,
                "difficulties": difficulties,
                "dev_since_last": dev_since_last, "time_for_dev": time_for_dev,
                "readiness_new_duties": readiness_new_duties
            })
            st.success(f"Plan rozwoju dla {selected_employee_name_idp} został zapisany!")
    with col2_idp:
        st.subheader("Zapisane Plany Rozwoju")
        if not st.session_state.idps:
            st.info("Brak zapisanych planów.")
        else:
            view_employee_name_idp_display = st.selectbox("Wyświetl plany dla:", sorted(
                list(set([i["employee_name"] for i in st.session_state.idps]))), key="idp_view_employee_display")
            idps_for_employee_display = [i for i in st.session_state.idps if
                                         i["employee_name"] == view_employee_name_idp_display]
            if not idps_for_employee_display:
                st.warning(f"Brak planów dla {view_employee_name_idp_display}")
            else:
                idp_options_display = {f"{i['plan_date']} - {i['form_type']} (ID: {i['id'][:8]})": i['id'] for i in
                                       sorted(idps_for_employee_display, key=lambda x: x['plan_date'], reverse=True)}
                selected_idp_label_display = st.selectbox("Wybierz plan:", list(idp_options_display.keys()),
                                                          key="idp_view_select_display")
                if selected_idp_label_display:
                    idp_to_display = next(i for i in idps_for_employee_display if
                                          i["id"] == idp_options_display[selected_idp_label_display])
                    st.markdown(
                        f"#### Plan dla: {idp_to_display['employee_name']} ({idp_to_display['plan_date']} - {idp_to_display['form_type']})")
                    for key, value in idp_to_display.items():
                        if key not in ["id", "employee_id", "employee_name", "form_type", "plan_date"]:
                            st.markdown(
                                f"**{key.replace('_', ' ').capitalize()}:** {value if value not in [None, ''] else 'Nie podano.'}")

# --- Moduł 3: Arkusz Poziomu Realizacji Zadań ---
elif selected_module == "Arkusz Poziomu Realizacji Zadań":
    st.header("📊 Arkusz Poziomu Realizacji Zadań")

    # Formularz dodawania/edycji zadania
    form_title = "Dodaj Nowe Zadanie"
    submit_label = "Dodaj Zadanie"
    default_task_data = {"name": "", "assignee": sample_employees[0]["name"], "status": "Do zrobienia", "progress": 0,
                         "priority": "Średni", "start_date": datetime.now().date(),
                         "deadline": datetime.now().date() + timedelta(days=7)}

    if st.session_state.editing_task and st.session_state.task_to_edit_id:
        task_data_to_edit = next((t for t in st.session_state.tasks if t["id"] == st.session_state.task_to_edit_id),
                                 None)
        if task_data_to_edit:
            form_title = f"Edytuj Zadanie: {task_data_to_edit['name']}"
            submit_label = "Zapisz Zmiany"
            default_task_data = task_data_to_edit
        else:  # Jeśli task zniknął, zresetuj edycję
            st.session_state.editing_task = False
            st.session_state.task_to_edit_id = None

    with st.expander(form_title, expanded=True if st.session_state.editing_task else False):
        with st.form(key="task_form",
                     clear_on_submit=not st.session_state.editing_task):  # Nie czyść przy edycji, chyba że po zapisie
            task_name = st.text_input("Nazwa zadania:", value=default_task_data["name"])
            task_assignee_name = st.selectbox("Przypisany do:", [e["name"] for e in sample_employees],
                                              index=[e["name"] for e in sample_employees].index(
                                                  default_task_data["assignee"]) if default_task_data["assignee"] in [
                                                  e["name"] for e in sample_employees] else 0)
            task_status = st.selectbox("Status:", ["Do zrobienia", "W trakcie", "Zakończone"],
                                       index=["Do zrobienia", "W trakcie", "Zakończone"].index(
                                           default_task_data["status"]))
            task_progress = st.slider("Postęp (%):", 0, 100, default_task_data["progress"])
            task_priority = st.selectbox("Priorytet:", ["Niski", "Średni", "Wysoki"],
                                         index=["Niski", "Średni", "Wysoki"].index(default_task_data["priority"]))
            d_col1, d_col2 = st.columns(2)
            task_start_date = d_col1.date_input("Data rozpoczęcia:", value=default_task_data["start_date"])
            task_deadline = d_col2.date_input("Termin realizacji:", value=default_task_data["deadline"])

            submitted = st.form_submit_button(submit_label)
            if submitted:
                if task_name and task_assignee_name:
                    if task_start_date > task_deadline:
                        st.error("Data rozpoczęcia nie może być późniejsza niż termin realizacji.")
                    else:
                        if st.session_state.editing_task and st.session_state.task_to_edit_id:
                            # Aktualizacja istniejącego zadania
                            for i, task in enumerate(st.session_state.tasks):
                                if task["id"] == st.session_state.task_to_edit_id:
                                    st.session_state.tasks[i] = {
                                        "id": st.session_state.task_to_edit_id, "name": task_name,
                                        "assignee": task_assignee_name,
                                        "status": task_status, "progress": task_progress, "priority": task_priority,
                                        "deadline": task_deadline, "start_date": task_start_date
                                    }
                                    break
                            st.success(f"Zadanie '{task_name}' zostało zaktualizowane.")
                            st.session_state.editing_task = False
                            st.session_state.task_to_edit_id = None
                            st.rerun()  # Aby odświeżyć formularz i listę
                        else:
                            # Dodanie nowego zadania
                            new_task_id = str(uuid.uuid4())
                            st.session_state.tasks.append({
                                "id": new_task_id, "name": task_name, "assignee": task_assignee_name,
                                "status": task_status, "progress": task_progress, "priority": task_priority,
                                "deadline": task_deadline, "start_date": task_start_date
                            })
                            st.success(f"Zadanie '{task_name}' zostało dodane.")
                            # st.rerun() # Aby odświeżyć listę i wyczyścić pola (clear_on_submit powinno to robić)
                else:
                    st.error("Nazwa zadania i przypisany pracownik są wymagane.")

    st.markdown("---")
    st.subheader("Wizualizacja Zadań")
    display_type = st.radio("Typ wizualizacji:", ["Tablica Kanban", "Wykres Gantta", "Lista Zadań"], horizontal=True,
                            key="task_display_type")

    if not st.session_state.tasks:
        st.info("Brak zadań do wyświetlenia.")
    else:
        if display_type == "Lista Zadań":
            df_tasks = pd.DataFrame(st.session_state.tasks)
            st.dataframe(df_tasks, use_container_width=True, hide_index=True, column_config={
                "id": None,  # Ukryj ID
                "name": st.column_config.TextColumn("Nazwa Zadania", width="large"),
                "assignee": "Przypisany", "status": "Status",
                "progress": st.column_config.ProgressColumn("Postęp", format="%d%%", min_value=0, max_value=100),
                "priority": "Priorytet", "start_date": "Start", "deadline": "Termin"
            })
            for task in st.session_state.tasks:  # Przyciski edycji/usuwania pod tabelą (alternatywa)
                # Można by dodać przyciski edycji/usuwania tutaj, jeśli st.dataframe nie wspiera ich bezpośrednio
                pass


        elif display_type == "Tablica Kanban":
            cols_kanban = st.columns(3)
            statuses_kanban = ["Do zrobienia", "W trakcie", "Zakończone"]
            status_map_kanban = {"Do zrobienia": "📋 Do zrobienia", "W trakcie": "⏳ W trakcie",
                                 "Zakończone": "✅ Zakończone"}
            for i, status_key in enumerate(statuses_kanban):
                with cols_kanban[i]:
                    st.subheader(status_map_kanban[status_key])
                    tasks_in_status = [t for t in st.session_state.tasks if t["status"] == status_key]
                    if not tasks_in_status: st.caption("Brak zadań.")
                    for task in tasks_in_status:
                        with st.container(border=True):
                            st.markdown(f"**{task['name']}**")
                            st.caption(f"Przypisany: {task['assignee']} | Priorytet: {task['priority']}")
                            st.caption(f"Start: {task['start_date']} | Termin: {task['deadline']}")
                            st.progress(task['progress'])
                            btn_cols = st.columns(2)
                            if btn_cols[0].button("✏️ Edytuj", key=f"edit_task_kanban_{task['id']}",
                                                  use_container_width=True):
                                st.session_state.task_to_edit_id = task['id']
                                st.session_state.editing_task = True
                                st.rerun()  # Aby otworzyć formularz edycji
                            if btn_cols[1].button("🗑️ Usuń", key=f"delete_task_kanban_{task['id']}", type="secondary",
                                                  use_container_width=True):
                                st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                                st.rerun()
                        st.markdown("---")


        elif display_type == "Wykres Gantta":
            gantt_data = [dict(Task=t["name"], Start=t["start_date"].strftime('%Y-%m-%d'),
                               Finish=t["deadline"].strftime('%Y-%m-%d'), Resource=t["status"], Complete=t["progress"])
                          for t in st.session_state.tasks]
            if not gantt_data:
                st.info("Brak danych do wykresu Gantta.")
            else:
                colors_gantt = {'Do zrobienia': 'rgb(220,20,60)', 'W trakcie': 'rgb(30,144,255)',
                                'Zakończone': 'rgb(50,205,50)'}
                try:
                    fig_gantt = ff.create_gantt(gantt_data, colors=colors_gantt, index_col='Resource',
                                                show_colorbar=True, group_tasks=True, title="Harmonogram Zadań")
                    st.plotly_chart(fig_gantt, use_container_width=True)
                except Exception as e:
                    st.error(f"Błąd generowania wykresu Gantta: {e}")

# --- Moduł 4: Kryteria Awansu ---
elif selected_module == "Kryteria Awansu":
    st.header("🏆 Kryteria Awansu w Garnexpol")
    st.sidebar.subheader("Filtruj Kryteria")
    available_categories = list(advancement_criteria.keys())
    criteria_category_selection = st.sidebar.selectbox("Kategoria kryteriów:", ["Wszystkie"] + available_categories,
                                                       key="adv_cat_select_sidebar")
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Lub dane i kryteria dla pracownika:**")
    employee_names_adv = [""] + [e["name"] for e in sample_employees]
    selected_employee_name_adv = st.sidebar.selectbox("Pracownik:", employee_names_adv, key="adv_employee_select")

    if selected_employee_name_adv:
        employee_obj_adv = next(e for e in sample_employees if e["name"] == selected_employee_name_adv)
        performance = employee_performance_data.get(employee_obj_adv["id"], {})
        avg_comp_score = calculate_average_competency_score(employee_obj_adv["id"], st.session_state.assessments)

        st.subheader(f"Ocena Potencjału Awansowego: {employee_obj_adv['name']}")
        st.caption(f"Dział: {employee_obj_adv['department']} | Rola: {employee_obj_adv['role']}")

        with st.container(border=True):  # Kluczowe wskaźniki
            st.markdown("##### 📊 Kluczowe Wskaźniki Pracownika")
            if performance or avg_comp_score is not None:
                cols_perf = st.columns(3)
                cols_perf[0].metric("Staż Pracy (lata)", f"{performance.get('staż_pracy_lata', 'N/A')}")
                cols_perf[1].metric("Śr. Ocena Kompetencji",
                                    f"{avg_comp_score if avg_comp_score is not None else 'N/A'}/7")
                cols_perf[2].metric("Ocena Przełożonego", str(performance.get('subiektywna_ocena_przełożonego', 'N/A')))
                # ... (reszta metryk działowych jak poprzednio)
                if employee_obj_adv["department"] == "Sprzedaż":
                    # ... (metryki sprzedaży)
                    pass
                # Pozostałe metryki...
            else:
                st.info("Brak szczegółowych danych o wynikach i ocenach dla tego pracownika.")
            st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):  # Kryteria Awansu
            st.markdown("##### 📜 Kryteria Awansu")
            for group_name, criteria_in_group in [("Ogólne", advancement_criteria["Ogólne"]),
                                                  (f"Dla Działu: {employee_obj_adv['department']}",
                                                   advancement_criteria.get(employee_obj_adv['department'], [])),
                                                  ("Kierownicze (dodatkowe)",
                                                   [c for c in advancement_criteria["Kierownicze"] if
                                                    c not in advancement_criteria["Ogólne"]])]:

                is_managerial_role = any(keyword in employee_obj_adv["role"].lower() for keyword in
                                         ["kierownik", "manager", "koordynator", "właściciel"])
                if group_name.startswith("Kierownicze") and not is_managerial_role:
                    continue  # Nie pokazuj kryteriów kierowniczych jeśli rola nie jest kierownicza

                if criteria_in_group:  # Tylko jeśli są jakieś kryteria w grupie
                    st.markdown(f"###### {group_name}:")
                    for criterion in criteria_in_group:
                        status_eval = check_criterion_status(criterion, employee_obj_adv, performance, avg_comp_score)
                        st.markdown(f"- {criterion} <small style='color:gray;'><i>[{status_eval}]</i></small>",
                                    unsafe_allow_html=True)
                    st.markdown("---")

    elif criteria_category_selection != "Wszystkie":  # Widok wg kategorii
        st.subheader(f"Kryteria Awansu: {criteria_category_selection}")
        if criteria_category_selection in advancement_criteria:
            with st.expander(f"Rozwiń dla: **{criteria_category_selection}**", expanded=True):
                for i, criterion in enumerate(advancement_criteria[criteria_category_selection]):
                    st.markdown(f"{i + 1}. {criterion}")
    elif criteria_category_selection == "Wszystkie":  # Wszystkie kategorie
        st.subheader("Wszystkie Kategorie Kryteriów Awansu")
        for category, criteria_list in advancement_criteria.items():
            with st.expander(f"Kategoria: **{category}**"):
                for i, criterion in enumerate(criteria_list): st.markdown(f"{i + 1}. {criterion}")

    st.markdown("---")
    st.subheader("🪜 Drabina Awansu")  # Drabina awansu
    # ... (kod drabiny awansu jak poprzednio)
    col_s, col_m, col_w = st.columns(3)
    for col, dept_name, color in zip([col_s, col_m, col_w], ["Sprzedaż", "Marketing", "Magazyn"],
                                     ["#1E90FF", "#32CD32", "#FF8C00"]):
        with col:
            with st.container(border=True):
                st.markdown(f"<h5 style='text-align: center; color: {color};'>{dept_name.upper()}</h5>",
                            unsafe_allow_html=True)
                st.markdown("---")
                for role in roles_by_department.get(dept_name, []):
                    st.markdown(f"<p style='text-align: center;'>{role}</p>", unsafe_allow_html=True)

# --- Stopka ---
st.sidebar.markdown("---")
st.sidebar.info("Garnexpol System Zarządzania")
