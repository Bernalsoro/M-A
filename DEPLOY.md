# 🚀 Deploy Global Liquidity Dashboard

Guía paso a paso para publicar tu dashboard en **Streamlit Cloud** (gratis).

---

## ⚡ Deployment en 5 Pasos (5 minutos)

### 1️⃣ Asegúrate de tener tu API Key de FRED

Si no la tienes:
1. Ve a: https://fred.stlouisfed.org/
2. Regístrate (gratis)
3. Obtén tu API key: https://fred.stlouisfed.org/docs/api/api_key.html
4. **Cópiala** - la necesitarás en el paso 4

---

### 2️⃣ Crear cuenta en Streamlit Cloud

1. Ve a: https://share.streamlit.io/
2. Click en **"Sign up"**
3. **Conecta con GitHub** (usa tu cuenta de GitHub donde está este repo)
4. Autoriza Streamlit a acceder a tus repos

✅ **Listo** - Ya tienes cuenta

---

### 3️⃣ Deployar la app

1. En Streamlit Cloud, click **"New app"**

2. Rellena el formulario:
   ```
   Repository:     Bernalsoro/M-A
   Branch:         claude/daily-api-updates-019HcJdX9qVDWTd5EDH2JxCa
   Main file path: streamlit_app.py
   ```

3. Click en **"Advanced settings"** (abajo)

4. En **"Python version"**, selecciona: `3.10` o superior

5. **NO hagas click en Deploy todavía** ⚠️

---

### 4️⃣ Configurar Secrets (API Key)

**Antes de deployar**, en la misma pantalla:

1. Busca la sección **"Secrets"**

2. Pega esto en el editor de Secrets:
   ```toml
   FRED_API_KEY = "tu_api_key_aqui"
   ```

   ⚠️ **Importante**: Reemplaza `tu_api_key_aqui` con tu API key real de FRED

3. Verifica que esté bien escrito (sin espacios extra)

---

### 5️⃣ Deploy!

1. Click en **"Deploy"** (botón azul)

2. Espera 2-3 minutos mientras se instala y arranca

3. **¡Listo!** 🎉

Te dará una URL tipo:
```
https://tu-usuario-m-a-xxxxxx.streamlit.app
```

**Esa es tu URL pública** que puedes compartir con cualquiera.

---

## 🌐 URL Pública

Una vez deployado, tu dashboard estará disponible 24/7 en:

```
https://[tu-nombre-de-usuario]-m-a-[hash].streamlit.app
```

Por ejemplo:
```
https://bernalsoro-m-a-claude-daily-api-updates.streamlit.app
```

**Características:**
- ✅ **Siempre activo** (24/7)
- ✅ **URL pública** (puedes compartirla en CV, LinkedIn)
- ✅ **Gratis para siempre**
- ✅ **SSL incluido** (HTTPS automático)
- ✅ **Se actualiza solo** cuando haces push a GitHub

---

## 🔄 Actualización Automática

### Cuando haces cambios en el código:

1. Haces commit y push a tu repo:
   ```bash
   git add .
   git commit -m "Update dashboard"
   git push
   ```

2. **Streamlit Cloud detecta el cambio automáticamente**

3. Re-deploya en 1-2 minutos

**No necesitas hacer nada más.** 🤖

---

## 📊 Datos Actualizados Diariamente

Recuerda que configuraste **GitHub Actions** para actualizar datos cada día:

```
.github/workflows/update-liquidity-data.yml
```

Esto significa:
- ✅ GitHub Actions corre todos los días a las 02:00 UTC
- ✅ Descarga datos nuevos de FRED + yfinance
- ✅ Hace commit automático a tu repo
- ✅ Streamlit Cloud detecta el commit y se actualiza solo

**Tu dashboard siempre tendrá datos frescos.** 🔄

---

## 🛠️ Configuración Post-Deployment

### Cambiar nombre de la app

1. En Streamlit Cloud, ve a tu app
2. Settings (⚙️) → General
3. Cambia **App name** a algo como: `global-liquidity-dashboard`
4. Save

Tu URL cambiará a:
```
https://[usuario]-global-liquidity-dashboard.streamlit.app
```

### Cambiar la branch

Si en el futuro quieres usar la rama `main` en vez de la rama de desarrollo:

1. Settings → General
2. Branch: cambia a `main`
3. Save y redeploy

---

## 🐛 Troubleshooting

### ❌ Error: "ModuleNotFoundError"

**Causa**: Falta alguna dependencia en requirements.txt

**Solución**:
1. Verifica que `liquidity_dashboard/requirements.txt` tenga todas las dependencias
2. Haz push del cambio
3. Streamlit Cloud se actualizará solo

---

### ❌ Error: "FRED_API_KEY no configurada"

**Causa**: No configuraste el secret correctamente

**Solución**:
1. Ve a tu app en Streamlit Cloud
2. Settings (⚙️) → Secrets
3. Verifica que diga exactamente:
   ```toml
   FRED_API_KEY = "tu_key_real"
   ```
4. Save
5. Reboot app

---

### ❌ La app no carga datos

**Causa**: Puede que los datos no estén en el repo

**Solución**: Los datos se generan en la primera ejecución. Si ves un error:

1. Espera 2-3 minutos (la primera carga tarda)
2. Si persiste, verifica en GitHub Actions que el workflow de actualización corrió
3. Los CSVs deben estar en `liquidity_dashboard/data/processed/`

---

### ❌ App se va a sleep

**Comportamiento normal**: Las apps en Streamlit Cloud gratuito:
- Se duermen después de 7 días sin uso
- Se despiertan al primer visitante (tarda ~30 segundos)

**Solución** (si quieres que esté siempre activa):
- Upgrade a plan Pro ($10/mes)
- O simplemente acepta el comportamiento (es normal para uso personal)

---

## 🎨 Personalización

### Cambiar el theme

Edita `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"  # Color principal
backgroundColor = "#0E1117"  # Fondo (modo oscuro)
secondaryBackgroundColor = "#262730"
textColor = "#FAFAFA"
```

Haz push y la app se actualizará sola.

---

### Cambiar título y favicon

Edita `liquidity_dashboard/src/dashboard_app.py`:
```python
st.set_page_config(
    page_title="Mi Dashboard Custom",
    page_icon="💰",  # Emoji como favicon
    layout="wide"
)
```

---

## 📱 Compartir tu Dashboard

### Para CV / LinkedIn:

```
🌍 Global Liquidity Dashboard

Dashboard interactivo que monitorea liquidez global en tiempo real
con actualización automática diaria.

🔗 Live demo: https://tu-url.streamlit.app
💻 Código: https://github.com/Bernalsoro/M-A

Stack: Python, Streamlit, Plotly, FRED API, GitHub Actions
```

### Para procesos de selección:

```
Como proyecto personal, desarrollé un dashboard de análisis de liquidez
global que:

- Consume APIs de la Fed (FRED) y mercados (yfinance)
- Calcula un índice compuesto de liquidez con z-scores normalizados
- Genera señales de trading basadas en regímenes históricos
- Se actualiza automáticamente cada día via GitHub Actions
- Deployado en la nube con CI/CD

Puedes verlo en vivo aquí: [tu-url]
```

---

## 🔐 Seguridad

### ✅ Tu API Key está segura:

- **NO** está en el código (está en Secrets)
- **NO** está visible en la URL
- **NO** aparece en los logs públicos
- Solo tú puedes verla en Settings → Secrets

### 🔓 Tu dashboard es público:

- Cualquiera con la URL puede verlo
- **NO** requiere login
- Esto es intencional (para compartir en CV/LinkedIn)

Si quieres que sea privado:
- Streamlit Cloud Pro permite autenticación
- O puedes agregar un simple password en el código

---

## 📊 Monitoreo

### Ver estadísticas de uso:

1. Ve a tu app en Streamlit Cloud
2. Analytics (📈)

Verás:
- Número de visitantes
- Países de origen
- Uso de recursos (CPU, memoria)

---

## 💡 Next Steps

Una vez deployado:

1. ✅ **Prueba la URL** - Verifica que funciona
2. ✅ **Comparte en LinkedIn** - Es una demo perfecta
3. ✅ **Agrega al CV** - Sección "Proyectos"
4. ✅ **Configura GitHub Actions** - Para updates diarios automáticos
5. ✅ **Personaliza** - Agrega más tickers, colores, etc.

---

## 📞 Ayuda

Si tienes problemas:
1. Revisa los logs en Streamlit Cloud (Manage app → Logs)
2. Verifica que GitHub Actions esté corriendo
3. Abre un issue en el repo de GitHub

---

## 🎉 ¡Felicidades!

Ahora tienes un **dashboard profesional deployado en la nube** con:

- ✅ URL pública y permanente
- ✅ Actualización automática diaria
- ✅ Datos en tiempo real
- ✅ 100% gratis
- ✅ Listo para mostrar en entrevistas

**¡Disfruta tu dashboard! 🚀**
