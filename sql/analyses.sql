-- =============================================================================
-- Analyses SQL — lecture seule
-- Base : marketing_analysis
-- Table : public.marketing_campaigns
-- Aucun INSERT / UPDATE / DELETE / DDL dans ce fichier.
-- =============================================================================

-- Extraction complète (utilisée ensuite par Pandas)
SELECT *
FROM public.marketing_campaigns
ORDER BY campaign_id;

-- KPI par type de campagne
SELECT
    campaign_type,
    COUNT(*) AS campaign_count,
    AVG(roi) AS avg_roi
FROM public.marketing_campaigns
GROUP BY campaign_type
ORDER BY avg_roi DESC;

-- Classes de ROI (CASE)
SELECT
    CASE
        WHEN roi < 4 THEN 'Faible'
        WHEN roi < 6 THEN 'Moyen'
        ELSE 'Élevé'
    END AS roi_category,
    COUNT(*) AS campaign_count,
    AVG(roi) AS avg_roi
FROM public.marketing_campaigns
GROUP BY roi_category
ORDER BY avg_roi;

-- Campagnes Email (extrait détaillé)
SELECT
    campaign_id,
    company,
    campaign_type,
    channel_used,
    acquisition_cost,
    roi,
    clicks,
    impressions,
    engagement_score
FROM public.marketing_campaigns
WHERE campaign_type = 'Email'
ORDER BY campaign_id;

-- Volumes et ROI par entreprise
SELECT
    company,
    COUNT(*) AS n,
    AVG(roi) AS avg_roi,
    AVG(acquisition_cost) AS avg_cost
FROM public.marketing_campaigns
GROUP BY company
ORDER BY n DESC;

-- Volumes par canal
SELECT
    channel_used,
    COUNT(*) AS n,
    AVG(roi) AS avg_roi
FROM public.marketing_campaigns
GROUP BY channel_used
ORDER BY channel_used;

-- Audience
SELECT
    target_audience,
    COUNT(*) AS n,
    AVG(roi) AS avg_roi
FROM public.marketing_campaigns
GROUP BY target_audience
ORDER BY n DESC;

-- Segment
SELECT
    customer_segment,
    COUNT(*) AS n,
    AVG(roi) AS avg_roi
FROM public.marketing_campaigns
GROUP BY customer_segment
ORDER BY n DESC;

-- Localisation
SELECT
    location,
    COUNT(*) AS n,
    AVG(roi) AS avg_roi
FROM public.marketing_campaigns
GROUP BY location
ORDER BY n DESC;

-- Volume mensuel 2021
SELECT
    DATE_TRUNC('month', campaign_date)::date AS month_start,
    COUNT(*) AS n,
    AVG(roi) AS avg_roi
FROM public.marketing_campaigns
GROUP BY DATE_TRUNC('month', campaign_date)
ORDER BY month_start;

-- Croisement entreprise × canal (contrôle de couverture)
SELECT
    company,
    channel_used,
    COUNT(*) AS n,
    AVG(roi) AS avg_roi
FROM public.marketing_campaigns
GROUP BY company, channel_used
ORDER BY company, channel_used;
