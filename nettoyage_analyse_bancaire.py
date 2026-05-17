
import pandas as pd
df=pd.read_excel('donnees_bancaires_sales.xlsx')

df.info()
df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%Y', errors='coerce')


# Vérifier les valeurs manquantes
print(f"Valeurs manquantes dans Date (avant): {df['Date'].isna().sum()}")
# Remplir les valeurs manquantes: forward fill puis back fill pour les débuts
df['Date'] = df['Date'].ffill().bfill()
print(f"Valeurs manquantes dans Date (après ffill/bfill): {df['Date'].isna().sum()}")

#on passe à la colonne Montant apres on va rvenir sur les noms
print('\n=== ANALYSE DE LA COLONNE MONTANT ===\n')
print(df['Montant'].describe())
print(f"Valeurs manquantes (NaN): {df['Montant'].isna().sum()}")

# Détection des anomalies
print("\n--- DETECTION DES ANOMALIES ---")

# 1. Vérifier le type de chaque valeur
print(f"Type de la colonne: {df['Montant'].dtype}")

# 2. Chercher les valeurs contenant des lettres, espaces ou caractères spéciaux
non_numerique = df[df['Montant'].astype(str).str.contains(r'[a-zA-Z\s]', regex=True, na=False)]
print(f"\nValeurs avec lettres ou espaces: {len(non_numerique)}")
if len(non_numerique) > 0:
    print("Exemples:")
    print(non_numerique[['Montant']].head(10))

# 3. Chercher les valeurs négatives
try:
    montant_numeric = pd.to_numeric(df['Montant'], errors='coerce')
    negatif_count = (montant_numeric < 0).sum()
    print(f"\nValeurs négatives: {negatif_count}")
    if negatif_count > 0:
        print("Exemples:")
        print(df[montant_numeric < 0][['Montant']].head(10))
except:
    print("\nImpossible de convertir en numérique")

# 4. Chercher les espaces en début/fin
espaces = df[df['Montant'].astype(str).str.startswith(' ') | df['Montant'].astype(str).str.endswith(' ')]
print(f"\nValeurs avec espaces en début/fin: {len(espaces)}")
if len(espaces) > 0:
    print("Exemples:")
    print(espaces[['Montant']].head(10))

# 5. Vérifier les valeurs zéro
if (montant_numeric == 0).sum() > 0:
    print(f"\nValeurs zéro: {(montant_numeric == 0).sum()}")

# 6. Afficher les uniques pour inspection visuelle
print(f"\nNombre de valeurs uniques: {df['Montant'].nunique()}")
print("\nExemples de valeurs uniques:")
print(df['Montant'].unique()[:20])

# --- NETTOYAGE DE LA COLONNE MONTANT ---
print("\n=== NETTOYAGE DE LA COLONNE MONTANT ===\n")

# 1. Supprimer les espaces inutiles
df['Montant'] = df['Montant'].astype(str).str.strip()

# 2. Supprimer les lettres (garder: chiffres, signe moins)
df['Montant'] = df['Montant'].astype(str).str.replace(r'[a-zA-Z]', '', regex=True)

# 3. Supprimer les points (décimales)
df['Montant'] = df['Montant'].astype(str).str.replace('.', '')

# 4. Convertir en numérique (supprimer les caractères non numériques sauf -)
df['Montant'] = pd.to_numeric(df['Montant'].astype(str).str.replace(r'[^\d-]', '', regex=True), errors='coerce')

# 5. Prendre la valeur absolue pour rendre positifs les nombres négatifs
df['Montant'] = df['Montant'].abs()

# 6. Convertir en integer
df['Montant'] = df['Montant'].astype('Int64', errors='ignore')

# 5. Vérifier le résultat du nettoyage
print(f"Valeurs manquantes après nettoyage: {df['Montant'].isna().sum()}")
print(f"\nStatistiques après nettoyage:")
print(df['Montant'].describe())
print(f"\nValeurs négatives: {(df['Montant'] < 0).sum()}")
print(f"\nExemples après nettoyage:")
print(df[['Montant']].head(15))

# --- GESTION DES NA DANS MONTANT ---
print("\n=== GESTION DES NA DANS MONTANT ===\n")

# Calculer la médiane de Montant (sans les NaN)
mediane_montant = df['Montant'].median()
print(f"Médiane de Montant: {mediane_montant}")

# Identifier les lignes avec NA dans Montant
na_montant = df['Montant'].isna()
print(f"Lignes avec NA dans Montant: {na_montant.sum()}")

# Pour chaque NA, vérifier si Date et Client ont des données
# Si oui: remplacer par la médiane; sinon: marquer pour suppression
df['a_supprimer'] = False

for idx in df[na_montant].index:
    if pd.notna(df.loc[idx, 'Date']) and pd.notna(df.loc[idx, 'Client']):
        # Date et Client ont des données: remplir par la médiane
        df.loc[idx, 'Montant'] = mediane_montant
    else:
        # Date ou Client sont vides: marquer pour suppression
        df.loc[idx, 'a_supprimer'] = True

# Afficher les stats
print(f"Lignes à supprimer: {df['a_supprimer'].sum()}")
print(f"Lignes avec Montant rempli par médiane: {na_montant.sum() - df['a_supprimer'].sum()}")

# Supprimer les lignes marquées
df = df[~df['a_supprimer']].drop(columns=['a_supprimer'])

# Convertir Montant en entier
df['Montant'] = df['Montant'].astype(int)
df['Type_Transaction'] = df['Type_Transaction'].fillna('Inconnu')
df['Type_Transaction'] = df['Type_Transaction'].str.replace('Prelevement', 'Prélèvement')
df['Type_Transaction'] = df['Type_Transaction'].str.replace('Viremnt', 'Virement')
df['Type_Transaction'] = df['Type_Transaction'].str.strip()
print(df['Type_Transaction'].value_counts())
print(df['Type_Transaction'].isna().sum())
print(df['Type_Transaction'].unique())
print(df['Type_Transaction'])
print(df[['Date', 'Client', 'Montant']].head(15))
#On passe à la colonne categorie

df['Categorie'] = df['Categorie'].str.replace('loisirs', 'Loisirs')
df['Categorie'] = df['Categorie'].str.replace('alimentation', 'Alimentation')
df['Categorie'] = df['Categorie'].str.replace('TRANSPORT', 'Transport')
df['Categorie'] = df['Categorie'].str.strip()
df['Categorie'] = df['Categorie'].fillna('Inconnu')
print(df['Categorie'] )  
print(df['Categorie'].isna().sum())
print(df['Categorie'].unique())
print(df['Categorie'].value_counts())

#On passe à la colonne Description
df['Description'] = df['Description'].str.strip()
df['Description'] = df['Description'].fillna('Inconnu')
print(df['Description'])
print(df['Description'].isna().sum())
print(df['Description'].unique())
print(df['Description'].value_counts())

#On paase la colonne Statut
df['Statut'] = df['Statut'].str.strip()
df['Statut'] = df['Statut'].fillna('Inconnu')
df['Statut'] = df['Statut'].str.replace('en_attente', 'En attente')
df['Statut'] = df['Statut'].str.replace('VALIDE', 'Validé')
print(df['Statut'])
print(df['Statut'].isna().sum())
print(df['Statut'].unique())
print(df['Statut'].value_counts())

#On passe à la colonne Numero_Compte
df['Numero_Compte'] = df['Numero_Compte'].str.strip()
df['Numero_Compte'] = df['Numero_Compte'].fillna('Inconnu')
print(df['Numero_Compte'])
print(df['Numero_Compte'].isna().sum())
print(df['Numero_Compte'].unique())
print(df['Numero_Compte'].value_counts())
print('\nOn va verfier\n')
#  Trouver et voir les comptes avec plusieurs clients
comptes_partages = df.groupby('Numero_Compte')['Client'].nunique()
comptes_suspects = comptes_partages[comptes_partages > 1]
if len(comptes_suspects) > 0:
    lignes_suspectes = df[df['Numero_Compte'].isin(comptes_suspects.index)]
    
    # Trier par numéro de compte pour voir les clients côte à côte
    lignes_suspectes_triees = lignes_suspectes.sort_values('Numero_Compte')
    
    print("\nDétails des comptes suspects :")
    print(lignes_suspectes_triees[['Numero_Compte', 'Client']])

print('\nLes colonnes\n')
print(df.columns)
print(df)
df.info()
print(df.describe)

# 1. Top 10 clients avec formatage des montants
gros_clients = df.groupby('Client')['Montant'].sum().sort_values(ascending=False).head(10)
print("\nTop 10 des clients par montant total :")
for client, montant in gros_clients.items():
    print(f"{client}:{int(montant)}")


total_montant = df['Montant'].sum()
print(f"\nMontant total de toutes les transactions : {total_montant}")

date_plus_productives = df.groupby(df['Date'].dt.date)['Montant'].sum().sort_values(ascending=False).head(10)
print("\nTop 10 des dates les plus productives :")
print(date_plus_productives)

# 4. Catégories avec nombre de transactions
print("\nTop 10 des catégories les plus rentables :")
categorie_stats = df.groupby('Categorie').agg({
    'Montant': ['sum', 'count', 'mean']
}).round(2)
categorie_stats.columns = ['Montant_total', 'Nb_transactions', 'Montant_moyen']
print(categorie_stats.sort_values('Montant_total', ascending=False).head(10))

# 5. Types de transactions
print("\nTop 10 des types de transactions les plus rentables :")
transaction_stats = df.groupby('Type_Transaction').agg({
    'Montant': ['sum', 'count']
}).round(2)
transaction_stats.columns = ['Montant_total', 'Nb_transactions']
print(transaction_stats.sort_values('Montant_total', ascending=False).head(10))


meilleur_statut = df.groupby('Statut')['Montant'].sum().sort_values(ascending=False).head(10)
print("\nTop 10 des statuts les plus rentables :")
print(meilleur_statut)

meilleure_description = df.groupby('Description')['Montant'].sum().sort_values(ascending=False).head(10)
print("\nTop 10 des descriptions les plus rentables :")
print(meilleure_description)


import matplotlib.pyplot as plt
plt.figure(figsize=(10,6))
plt.bar(gros_clients.head(10).index, gros_clients.head(10).values, color='skyblue')
plt.xlabel('Client')
plt.ylabel('Montant')
plt.title('Top 10 des produits les plus vendus')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

plt.figure(figsize=(10,6))
plt.barh(meilleur_statut.head(5).index, meilleur_statut.head(5).values, color='red')
plt.xlabel('Statut')
plt.xlabel('Montant')
plt.title('Top 5 des meilleurs statuts')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()



with pd.ExcelWriter('donnees_bancaires.xlsx', engine='openpyxl') as writer:

    total_montant = pd.DataFrame({'le montant total des transaction': [total_montant ]})
    total_montant .to_excel(writer, sheet_name='CA_Total', index=False)
    

    date_plus_productives.to_excel(writer, sheet_name='Date_Top10')
    

    meilleure_description.to_excel(writer, sheet_name='Description_Top10')
    
    
    meilleur_statut.to_excel(writer, sheet_name='Statut_Top5')
    
    
    categorie_stats.to_excel(writer, sheet_name='top 5 des categories')
    
    
    transaction_stats.to_excel(writer, sheet_name='Dates_Top5')
    
    gros_clients.to_excel(writer, sheet_name='Gros_client')
    
    df.to_excel(writer, sheet_name='Donnees_Completes', index=False)

print("\n✓ Export réussi ! Fichier 'analyse_ventes.xlsx' créé avec les feuilles:")






























