# Données

Ce dossier documente le jeu utilisé par le projet. **Le fichier Excel n’est pas versionné** dans ce dépôt.

## Nom

`marketing_campaign_dataset.xlsx`

## Origine

Fichier Excel local, conservé hors du dépôt GitHub, dans le dossier parent du dépôt (voir « Placement local » ci-dessous) :

`../marketing_campaign_dataset/marketing_campaign_dataset.xlsx`

Aucune licence publique n’est jointe au fichier. Il n’est donc **pas** téléchargeable depuis GitHub.

## Rôle

Source unique des 200 005 campagnes. Le fichier a été importé une fois dans PostgreSQL (`marketing_analysis.public.marketing_campaigns`). Les scripts Python et le dashboard lisent **PostgreSQL**, pas l’Excel.

## Structure

- 200 005 lignes (une ligne = une campagne)
- 15 colonnes originales
- période des dates : 2021-01-01 → 2021-12-31

Colonnes : `campaign_id`, `company`, `campaign_type`, `target_audience`, `duration_days`, `channel_used`, `conversion_rate`, `acquisition_cost`, `roi`, `location`, `campaign_date`, `clicks`, `impressions`, `engagement_score`, `customer_segment`.

## Taille

Environ 17 Mo. Trop volumineux et sans licence explicite pour un versionnement GitHub systématique.

## Placement local

Le dataset reste volontairement **en dehors** du dépôt, dans le dossier parent :

```text
Data/marketing_campaign_dataset/marketing_campaign_dataset.xlsx
```

Chemin relatif depuis la racine de `marketing-campaign-analysis` :

```text
../marketing_campaign_dataset/marketing_campaign_dataset.xlsx
```

Ce fichier n’est pas fourni par le clone GitHub. Une copie éventuelle dans `data/` n’est pas exigée par les scripts.

Les analyses ne rechargent pas l’Excel : elles exigent une base PostgreSQL déjà peuplée (rôle `data_project`, base `marketing_analysis`, table `public.marketing_campaigns`).
