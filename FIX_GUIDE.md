# 🔧 Guide de Correction - Service Email

## 🐛 Problème

```bash
curl -X 'POST' \
  'https://travliaq-sending-mail-production.up.railway.app/send-trip-summary-email' \
  -d '{"summary_id": "8cc800aa-4656-4d08-a7fc-e8744786801c"}'

# ❌ Erreur 404
{
  "ok": false,
  "error": "SUMMARY_NOT_FOUND",
  "detail": "Trip summary not found"
}
```

---

## ✅ Corrections appliquées

### 1. **Ajout du champ `trip_code`**

[src/app/services/supabase_client.py](e:\CrewTravliaq\Travliaq-Sending-Mail\src\app\services\supabase_client.py)

```python
class TripSummary(BaseModel):
    # ...
    trip_code: Optional[str]  # ✅ AJOUTÉ ligne 18
    # ...
```

### 2. **Validation `pipeline_status` corrigée**

[src/app/api/email_routes.py](e:\CrewTravliaq\Travliaq-Sending-Mail\src\app\api\email_routes.py)

```python
# ✅ AVANT : Refusait SUCCESS
if summary.pipeline_status.upper() not in {"COMPLETED", "READY", "DONE"}:

# ✅ APRÈS : Accepte SUCCESS
if summary.pipeline_status.upper() not in {"SUCCESS", "COMPLETED", "READY", "DONE"}:
```

---

## ⚠️ CRITIQUE : Corriger la SERVICE KEY

### Problème actuel

Dans ton `.env` :
```env
# ❌ MAUVAIS : C'est l'ANON key !
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpbmJubWxmcGZmbXlqbWt3YmNvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTc5NDQ2MTQsImV4cCI6MjA3MzUyMDYxNH0.yrju-Pv4OlfU9Et-mRWg0GRHTusL7ZpJevqKemJFbuA
```

**Décodage du JWT** :
```json
{
  "role": "anon"  // ❌ MAUVAIS !
}
```

### Solution

#### Étape 1 : Récupère la vraie SERVICE ROLE key

1. Va sur [Supabase Dashboard](https://supabase.com/dashboard/project/cinbnmlfpffmyjmkwbco/settings/api)
2. **Settings** > **API**
3. Copie la clé **`service_role`** (dans la section "Project API keys")

**Elle doit ressembler à ça** (décodage) :
```json
{
  "role": "service_role"  // ✅ BON !
}
```

#### Étape 2 : Mets à jour `.env`

```env
SUPABASE_URL=https://cinbnmlfpffmyjmkwbco.supabase.co
# ✅ REMPLACE PAR TA VRAIE SERVICE_ROLE KEY
SUPABASE_SERVICE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNpbmJubWxmcGZmbXlqbWt3YmNvIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc1Nzk0NDYxNCwiZXhwIjoyMDczNTIwNjE0fQ.METS_TA_VRAIE_SERVICE_ROLE_KEY_ICI
```

#### Étape 3 : Mets à jour Railway

**Via l'interface Railway** :
1. Va sur [Railway Dashboard](https://railway.app/dashboard)
2. Sélectionne **Travliaq-Sending-Mail**
3. **Variables** > Trouve `SUPABASE_SERVICE_KEY`
4. Remplace par la **vraie service_role key**
5. Redéploie

**Via CLI** :
```bash
cd Travliaq-Sending-Mail
railway variables set SUPABASE_SERVICE_KEY="TA_VRAIE_SERVICE_ROLE_KEY"
railway up
```

---

## 🧪 Test

### 1. Test local

```bash
# Démarre le service
cd Travliaq-Sending-Mail
uvicorn src.app.main:app --reload

# Dans un autre terminal
curl -X 'POST' \
  'http://localhost:8000/send-trip-summary-email' \
  -H 'Content-Type: application/json' \
  -d '{"summary_id": "8cc800aa-4656-4d08-a7fc-e8744786801c"}'
```

**Résultat attendu** :
```json
{
  "ok": true,
  "email_id": "re_...",
  "summary_id": "8cc800aa-4656-4d08-a7fc-e8744786801c"
}
```

### 2. Vérifier que le summary existe

Avant de tester, vérifie dans Supabase SQL Editor :

```sql
SELECT
  id,
  trip_code,
  user_email,
  destination,
  pipeline_status
FROM trip_summaries
WHERE id = '8cc800aa-4656-4d08-a7fc-e8744786801c';
```

Si ça retourne 0 ligne :
- ❌ Le summary n'existe pas avec cet ID
- ✅ Génère un nouveau trip via la pipeline
- ✅ Utilise le nouveau `summary_id` retourné

### 3. Test Railway (après déploiement)

```bash
curl -X 'POST' \
  'https://travliaq-sending-mail-production.up.railway.app/send-trip-summary-email' \
  -H 'Content-Type: application/json' \
  -d '{"summary_id": "NOUVEAU_SUMMARY_ID"}'
```

---

## 📊 Debugging

### Erreur 404 "SUMMARY_NOT_FOUND"

**Causes possibles** :
1. ❌ **SERVICE KEY incorrecte** (anon au lieu de service_role)
2. ❌ **summary_id** n'existe pas dans `trip_summaries`
3. ❌ **RLS policies** bloquent l'accès

**Solutions** :
1. ✅ Utilise la service_role key
2. ✅ Vérifie que le summary existe (SQL ci-dessus)
3. ✅ Les policies RLS sont bypassées avec service_role

### Erreur 409 "SUMMARY_NOT_READY"

**Cause** :
- `pipeline_status` n'est pas "SUCCESS"

**Solution** :
- Vérifie le status :
```sql
SELECT pipeline_status FROM trip_summaries WHERE id = '...';
```
- Si `FAILED` ou autre, relance la pipeline

### Erreur 500 "INTERNAL_ERROR"

**Regarder les logs Railway** :
```bash
railway logs
```

Ou dans l'interface : **Deployments** > Dernier déploiement > **View Logs**

---

## ✅ Checklist

- [ ] Champ `trip_code` ajouté au modèle `TripSummary`
- [ ] Validation `pipeline_status` accepte "SUCCESS"
- [ ] **SERVICE_ROLE key** configurée (pas anon key)
- [ ] Variables Railway mises à jour
- [ ] Service redéployé
- [ ] Test avec un vrai `summary_id`
- [ ] Email reçu avec succès

---

## 🎉 Une fois corrigé

Le workflow complet fonctionnera :

```
Pipeline termine
    ↓
trip_summaries créé avec :
  - id: "xyz-abc-123..."
  - trip_code: "OSLO-2025-101D4A"
  - pipeline_status: "SUCCESS"
  - user_email: "user@example.com"
    ↓
Email envoyé automatiquement :
  POST /send-trip-summary-email
  {"summary_id": "xyz-abc-123..."}
    ↓
Ton service envoie l'email 📧
```

---

**Questions ? Besoin d'aide pour trouver la service_role key ?**
