import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Connexion DB
def get_connection():
    conn = sqlite3.connect('hotel.db')
    conn.row_factory = sqlite3.Row
    return conn

conn = get_connection()
c = conn.cursor()

st.set_page_config(page_title="Gestion Hôtel", layout="wide")
st.title("🏨 Application de Gestion des Réservations")

menu = [
    "Accueil",
    "Voir Clients",
    "Ajouter Client",
    "Modifier Client",
    "Supprimer Client",
    "Voir Réservations",
    "Filtrer Réservations",
    "Ajouter Réservation",
    "Chambres Disponibles",
    "Statistiques",
    "Exporter CSV",
    "Évaluations",
    "À propos"
]
choice = st.sidebar.selectbox("📋 Menu", menu)

# ----------- FONCTIONS --------------

def charger_clients():
    c.execute("SELECT * FROM Client")
    return c.fetchall()


def charger_reservations():
    conn = sqlite3.connect("hotel.db")
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute("""
    SELECT c.Nom, v.NomVille AS Ville, ch.numero,
           r.DateArrivee, r.DateDepart
    FROM Reservation r
    JOIN Client c ON r.IdClient = c.IdClient
    JOIN Chambre ch ON r.IdChambre = ch.IdChambre
    JOIN Hotel h ON ch.IdHotel = h.IdHotel
    JOIN Ville v ON h.IdVille = v.IdVille
    """)

    return c.fetchall()


def charger_evaluations():
    c.execute("""
    SELECT e.IdEvaluation, cl.Nom, e.Note, e.Commentaire, e.DateEvaluation
    FROM Evaluation e
    JOIN Reservation r ON e.IdReservation = r.IdReservation
    JOIN Client cl ON r.IdClient = cl.IdClient
    ORDER BY e.DateEvaluation DESC
    """)
    return c.fetchall()

# ----------- PAGES ------------------

if choice == "Accueil":
    st.markdown("## 👋 Bienvenue dans l'application de gestion des hôtels !")
    st.info("Utilisez le menu à gauche pour naviguer entre les options.")

elif choice == "Voir Clients":
    st.subheader("📋 Liste des clients")
    clients = charger_clients()
    for cl in clients:
        st.markdown(f"🧍 **{cl['Nom']}** | 📍 {cl['Adresse']}, {cl['Ville']} | 📞 {cl['NumTel']} | ✉️ {cl['Email']}")

elif choice == "Ajouter Client":
    st.subheader("➕ Ajouter un nouveau client")
    with st.form("form_ajout_client"):
        nom = st.text_input("Nom complet")
        adresse = st.text_input("Adresse")
        ville = st.text_input("Ville")
        code_postal = st.number_input("Code postal", step=1, format="%d")
        email = st.text_input("Email")
        tel = st.text_input("Téléphone")
        submit = st.form_submit_button("Ajouter")

        if submit:
            try:
                c.execute("INSERT INTO Client (Adresse, Ville, Code_postal, Email, NumTel, Nom) VALUES (?, ?, ?, ?, ?, ?)",
                          (adresse, ville, code_postal, email, tel, nom))
                conn.commit()
                st.success("✅ Client ajouté avec succès.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

elif choice == "Modifier Client":
    st.subheader("✏️ Modifier les infos d’un client")
    clients = charger_clients()
    noms = [cl['Nom'] for cl in clients]
    selected_nom = st.selectbox("Choisir un client à modifier", noms)
    if selected_nom:
        client = next(cl for cl in clients if cl['Nom'] == selected_nom)
        with st.form("form_modif_client"):
            nom = st.text_input("Nom complet", client['Nom'])
            adresse = st.text_input("Adresse", client['Adresse'])
            ville = st.text_input("Ville", client['Ville'])
            code_postal = st.number_input("Code postal", value=client['Code_postal'], step=1, format="%d")
            email = st.text_input("Email", client['Email'])
            tel = st.text_input("Téléphone", client['NumTel'])
            submit = st.form_submit_button("Modifier")

            if submit:
                try:
                    c.execute("""UPDATE Client SET Nom=?, Adresse=?, Ville=?, Code_postal=?, Email=?, NumTel=?
                                 WHERE IdClient=?""",
                              (nom, adresse, ville, code_postal, email, tel, client['IdClient']))
                    conn.commit()
                    st.success("✅ Informations modifiées.")
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

elif choice == "Supprimer Client":
    st.subheader("❌ Supprimer un client")
    clients = charger_clients()
    noms = [cl['Nom'] for cl in clients]
    selected_nom = st.selectbox("Choisir un client à supprimer", noms)
    if selected_nom:
        client = next(cl for cl in clients if cl['Nom'] == selected_nom)
        if st.button(f"Confirmer suppression de {selected_nom}"):
            try:
                c.execute("DELETE FROM Reservation WHERE IdClient=?", (client['IdClient'],))
                # c.execute("DELETE FROM Evaluation WHERE IdClient=?", (client['IdClient'],))
                c.execute("""
    DELETE FROM Evaluation
    WHERE IdReservation IN (SELECT IdReservation FROM Reservation WHERE IdClient=?)
""", (client['IdClient'],))

                c.execute("DELETE FROM Client WHERE IdClient=?", (client['IdClient'],))
                conn.commit()
                st.success(f"✅ Client {selected_nom} supprimé avec ses réservations et évaluations.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")

elif choice == "Voir Réservations":
    st.subheader("📅 Réservations")
    reservations = charger_reservations()
    for r in reservations:
        st.markdown(f"🛏️ **Client :** {r['Nom']} | 📍 Hôtel : {r['Ville']} | 🏠 Chambre : {r['numero']} | 📅 Du {r['DateArrivee']} au {r['DateDepart']}")

elif choice == "Filtrer Réservations":
    st.subheader("🔍 Filtrer les réservations")
    reservations = charger_reservations()
    print(dict(reservations[0]))
    df = pd.DataFrame(reservations, columns=['Nom', 'numero', 'Ville', 'DateArrivee', 'DateDepart'])
    noms_clients = df['Nom'].unique().tolist()
    client_filter = st.multiselect("Filtrer par client", noms_clients)
    date_debut = st.date_input("Date début filtre", value=datetime(2020, 1, 1))
    date_fin = st.date_input("Date fin filtre", value=datetime.now())

    if st.button("Filtrer"):
        filt = df[
            (df['DateArrivee'] >= str(date_debut)) &
            (df['DateDepart'] <= str(date_fin))
        ]
        if client_filter:
            filt = filt[filt['Nom'].isin(client_filter)]
        if filt.empty:
            st.warning("Aucune réservation trouvée avec ces critères.")
        else:
            st.dataframe(filt)

elif choice == "Ajouter Réservation":
    st.subheader("➕ Nouvelle Réservation")
    clients = charger_clients()
    client_dict = {cl['Nom']: cl['IdClient'] for cl in clients}
    c.execute("SELECT IdChambre, numero FROM Chambre")
    chambres = c.fetchall()
    chambre_dict = {f"Chambre {ch[1]}": ch[0] for ch in chambres}

    with st.form("form_ajout_resa"):
        client_choix = st.selectbox("Client", list(client_dict.keys()))
        chambre_choix = st.selectbox("Chambre", list(chambre_dict.keys()))
        date_arrivee = st.date_input("Date d'arrivée")
        date_depart = st.date_input("Date de départ")
        submit = st.form_submit_button("Réserver")

        if submit:
            if date_depart <= date_arrivee:
                st.error("❌ La date de départ doit être après la date d'arrivée.")
            else:
                try:
                    c.execute("INSERT INTO Reservation (DateArrivee, DateDepart, IdClient, IdChambre) VALUES (?, ?, ?, ?)",
                              (str(date_arrivee), str(date_depart), client_dict[client_choix], chambre_dict[chambre_choix]))
                    conn.commit()
                    st.success("✅ Réservation ajoutée !")
                except Exception as e:
                    st.error(f"❌ Erreur : {e}")

elif choice == "Chambres Disponibles":
    st.subheader("🛏️ Rechercher les chambres disponibles")
    date_debut = st.date_input("📅 Date de début")
    date_fin = st.date_input("📅 Date de fin")

    if date_debut > date_fin:
        st.error("❌ La date de début doit être avant la date de fin.")
    else:
        if st.button("🔍 Chercher"):
            query = '''
                SELECT ch.IdChambre, ch.numero, ch.Etage, t.Type, h.IdVille
                FROM Chambre ch
                JOIN TypeChambre t ON ch.IdType = t.IdType
                JOIN Hotel h ON ch.IdHotel = h.IdHotel
                WHERE ch.IdChambre NOT IN (
                    SELECT IdChambre FROM Reservation
                    WHERE NOT (
                        DateDepart <= ? OR DateArrivee >= ?
)

                )
            '''
            c.execute(query, (str(date_fin), str(date_debut)))
            result = c.fetchall()

            if result:
                st.success(f"✅ {len(result)} chambre(s) trouvée(s) !")
                for chm in result:
                    st.markdown(f"🛏️ **Chambre {chm[1]}** | 🏨 {chm[4]} | 🏢 Étage: {chm[2]} | 💰 Type: {chm[3]}")
            else:
                st.warning(" Aucune chambre disponible dans cette période.")

elif choice == "Statistiques":
    st.subheader("📊 Statistiques générales")
    # Nb clients
    c.execute("SELECT COUNT(*) FROM Client")
    nb_clients = c.fetchone()[0]
    # Nb réservations
    c.execute("SELECT COUNT(*) FROM Reservation")
    nb_resas = c.fetchone()[0]
    # Nb hôtels
    c.execute("SELECT COUNT(*) FROM Hotel")
    nb_hotels = c.fetchone()[0]
    # Moyenne notes (s'il y a table Evaluation)
    c.execute("SELECT AVG(Note) FROM Evaluation")
    avg_note = c.fetchone()[0]
    avg_note = round(avg_note,2) if avg_note else "N/A"

    st.markdown(f"""
    - Nombre total de clients : **{nb_clients}**  
    - Nombre total de réservations : **{nb_resas}**  
    - Nombre total d'hôtels : **{nb_hotels}**  
    - Note moyenne clients : **{avg_note}**
    """)

elif choice == "Exporter CSV":
    st.subheader("📁 Exporter les données en CSV")

    dataset = st.selectbox("Choisir la table à exporter", ["Clients", "Réservations", "Évaluations"])
    if st.button("Exporter"):
        if dataset == "Clients":
            c.execute("SELECT * FROM Client")
            data = c.fetchall()
            df = pd.DataFrame(data, columns=[desc[0] for desc in c.description])
        elif dataset == "Réservations":
            c.execute("""
                SELECT r.IdReservation, c.Nom, ch.numero, h.IdVille, r.DateArrivee, r.DateDepart
                FROM Reservation r
                JOIN Client c ON r.IdClient = c.IdClient
                JOIN Chambre ch ON r.IdChambre = ch.IdChambre
                JOIN Hotel h ON ch.IdHotel = h.IdHotel
            """)
            data = c.fetchall()
            df = pd.DataFrame(data, columns=['IdReservation','Nom','numero','Ville','DateArrivee','DateDepart'])
        elif dataset == "Évaluations":
            c.execute("""
                SELECT e.IdEvaluation, c.Nom, e.Note, e.Commentaire, e.DateEvaluation
                FROM Evaluation e
                JOIN Reservation r ON e.IdReservation = r.IdReservation
                JOIN Client c ON r.IdClient = c.IdClient;
            """)
            data = c.fetchall()
            df = pd.DataFrame(data, columns=['IdEvaluation','Nom','Note','Commentaire','DateEvaluation'])

        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(label=f"Télécharger {dataset} CSV", data=csv, file_name=f"{dataset}.csv", mime="text/csv")

elif choice == "Évaluations":
    st.subheader("💬 Gestion des évaluations (notes & commentaires clients)")
    clients = charger_clients()
    client_dict = {cl['Nom']: cl['IdClient'] for cl in clients}

    # Afficher les évaluations existantes
    st.markdown("### Liste des évaluations")
    evaluations = charger_evaluations()
    if evaluations:
        for e in evaluations:
            st.markdown(f"👤 **{e['Nom']}** - Note : {e['Note']} / 5")
            st.markdown(f"📝 Commentaire : {e['Commentaire']}")
            st.markdown(f"📅 Date : {e['DateEvaluation']}")
            st.markdown("---")
    else:
        st.info("Aucune évaluation pour le moment.")

    st.markdown("### Ajouter une nouvelle évaluation")
    with st.form("form_ajout_eval"):
        client_choix = st.selectbox("Client", list(client_dict.keys()))
        note = st.slider("Note (1 à 5)", 1, 5, 3)
        commentaire = st.text_area("Commentaire")
        submit = st.form_submit_button("Ajouter évaluation")

        if submit:
            try:
                # On récupère la dernière réservation du client pour relier l'évaluation
                c.execute("""
                    SELECT r.IdReservation FROM Reservation r
                    WHERE r.IdClient = ? ORDER BY r.DateDepart DESC LIMIT 1
                """, (client_dict[client_choix],))
                resa = c.fetchone()
                if resa:
                    id_resa = resa['IdReservation']
                    date_eval = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    c.execute("""
                        INSERT INTO Evaluation (IdReservation, Note, Commentaire, DateEvaluation)
                        VALUES (?, ?, ?, ?)
                    """, (id_resa, note, commentaire, date_eval))
                    conn.commit()
                    st.success("✅ Évaluation ajoutée avec succès !")
                else:
                    st.error("❌ Ce client n'a pas de réservation récente pour évaluer.")
            except Exception as e:
                st.error(f"❌ Erreur : {e}")


elif choice == "Statistiques générales":
    st.subheader("📊 Statistiques générales")

    # Nombre total de clients
    c.execute("SELECT COUNT(*) FROM Client")
    total_clients = c.fetchone()[0]

    # Nombre total de réservations
    c.execute("SELECT COUNT(*) FROM Reservation")
    total_reservations = c.fetchone()[0]

    # Nombre total de chambres
    c.execute("SELECT COUNT(*) FROM Chambre")
    total_chambres = c.fetchone()[0]

    st.metric("Nombre total de clients", total_clients)
    st.metric("Nombre total de réservations", total_reservations)
    st.metric("Nombre total de chambres", total_chambres)

    # Statistiques sur les notes (moyenne)
    c.execute("SELECT AVG(Note) FROM Evaluation")
    avg_note = c.fetchone()[0]
    if avg_note is None:
        st.info("Aucune évaluation enregistrée.")
    else:
        st.metric("Note moyenne des évaluations", f"{avg_note:.2f} / 5")

elif choice == "Exporter les données":
    st.subheader("📁 Exporter les données en CSV")

    table = st.selectbox("Choisir la table à exporter", ["Client", "Reservation", "Chambre", "Evaluation"])

    if st.button("Exporter"):
        try:
            c.execute(f"SELECT * FROM {table}")
            data = c.fetchall()
            headers = [description[0] for description in c.description]

            import pandas as pd
            df = pd.DataFrame(data, columns=headers)

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Télécharger CSV",
                data=csv,
                file_name=f"{table}.csv",
                mime="text/csv",
            )
        except Exception as e:
            st.error(f"Erreur lors de l'export : {e}")

elif choice == "Filtrer Réservations":
    st.subheader("🔍 Filtrer les réservations")

    c.execute("SELECT Nom FROM Client")
    clients = [row[0] for row in c.fetchall()]
    clients.insert(0, "Tous")

    client_filter = st.selectbox("Filtrer par client", clients)
    date_debut = st.date_input("Date début", value=None)
    date_fin = st.date_input("Date fin", value=None)

    query = '''
        SELECT r.IdReservation, c.Nom, ch.numero, h.IdVille, r.DateArrivee, r.DateDepart
        FROM Reservation r
        JOIN Client c ON r.IdClient = c.IdClient
        JOIN Chambre ch ON r.IdChambre = ch.IdChambre
        JOIN Hotel h ON ch.IdHotel = h.IdHotel
        WHERE 1=1
    '''
    params = []

    if client_filter != "Tous":
        query += " AND c.Nom = ?"
        params.append(client_filter)

    if date_debut and date_fin:
        query += " AND r.DateArrivee >= ? AND r.DateDepart <= ?"
        params.append(str(date_debut))
        params.append(str(date_fin))

    c.execute(query, params)
    results = c.fetchall()

    if results:
        for r in results:
            st.markdown(f"🛏️ **Client :** {r[1]} | 📍 Hôtel : {r[3]} | 🏠 Chambre : {r[2]} | 📅 Du {r[4]} au {r[5]}")
    else:
        st.warning("Aucune réservation trouvée avec ces critères.")

elif choice == "À propos":
    st.subheader("ℹ️ À propos du projet")

    st.markdown("""
    ## 🏨 Application de Gestion des Réservations d’Hôtels

    Ce projet a été réalisé dans le cadre du module **Bases de Données**  
    de l’année universitaire **2024-2025**.

    ### 🎯 Objectif :
    Concevoir une base de données pour un système de gestion des réservations d’hôtels,  
    puis créer une interface web simple pour :
    - Gérer les **clients** (ajouter, modifier, supprimer)
    - Gérer les **réservations** (ajouter, filtrer par date ou client)
    - Vérifier la disponibilité des **chambres**
    - Gérer les **évaluations** des clients
    - Exporter les données en **CSV**
    - Afficher des **statistiques générales**

    ### 👩‍💻 Réalisé par :
    - **[Hajar]**
    - **[El batoul]**

    ### 🛠️ Technologies utilisées :
    - **SQLite** : Base de données légère et embarquée
    - **Streamlit** : Framework Python pour créer des applications web interactives
    - **Python** : Langage principal

    ### 🧑‍🏫 Encadré par :
    - **Pr. J. ZAHIR**

    Merci de tester et d’utiliser cette application.  
    Pour toute question ou amélioration, n’hésitez pas à me contacter !

    ---
    _© 2025 Gestion Hôtel - Tous droits réservés_
    """)

    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/4/4b/Hotel_icon.svg/1024px-Hotel_icon.svg.png", width=150)

charger_reservations()