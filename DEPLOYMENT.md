# Cómo Publicar tu M&A Analyst Hub Online (Gratis) 🌐

Esta guía te explica cómo tener tu app **siempre online** usando Streamlit Community Cloud.

## ¿Qué es Streamlit Community Cloud?

- **100% Gratis** para apps públicas
- **Siempre online** (24/7)
- **URL personalizada**: `tu-usuario.streamlit.app`
- **Actualización automática** cuando haces push al repo
- **Recursos**: Suficiente para apps como esta (1 GB RAM, 1 CPU core)

## Pasos para Publicar (5 minutos)

### 1. Crea una cuenta en Streamlit Cloud

1. Ve a: https://streamlit.io/cloud
2. Haz clic en **"Sign up"**
3. Conecta tu cuenta de GitHub

### 2. Deploya tu app

1. Una vez dentro, haz clic en **"New app"**
2. Selecciona:
   - **Repository**: `Bernalsoro/M-A`
   - **Branch**: `claude/ma-analyst-hub-01LwCugHj4D8Cuao8K9DEbo1` (o la que tengas)
   - **Main file path**: `app.py`
3. Haz clic en **"Deploy!"**

### 3. ¡Listo!

- Tu app estará en: `https://[tu-nombre]-m-a-analyst-hub.streamlit.app`
- Se actualizará automáticamente cada vez que hagas push al repo
- Puedes compartir la URL con quien quieras

## Configuración Adicional (Opcional)

### Personalizar la URL

En Streamlit Cloud, ve a **Settings** > **General** y puedes:
- Cambiar el nombre de la app
- Personalizar la URL

### Variables de Entorno

Si en el futuro necesitas API keys o secretos:
1. Ve a **Settings** > **Secrets**
2. Añade tus variables en formato TOML

### Dominios Personalizados

Si tienes un dominio propio:
1. Upgrade a Streamlit for Teams (de pago)
2. O usa un reverse proxy/CNAME

## Límites del Plan Gratuito

- **Apps públicas**: Ilimitadas
- **Recursos por app**: 1 GB RAM, 1 CPU core
- **Usuarios simultáneos**: ~50 (más que suficiente para portfolio)
- **Tiempo de inactividad**: La app se "duerme" tras 7 días sin uso (se reactiva al visitarla)

## Alternativas (si necesitas más)

### Opción 2: Render.com (también gratis)
```bash
# Crear un render.yaml
```

### Opción 3: Heroku (gratis con limitaciones)
```bash
# Crear un Procfile
```

### Opción 4: Railway.app (500 horas gratis/mes)
```bash
# Deploy directo desde GitHub
```

## Consejos Pro 💡

1. **Mantén el repo actualizado**: Cada push = deploy automático
2. **Monitoriza el uso**: Streamlit Cloud te muestra analytics básicos
3. **Optimiza el rendimiento**:
   - Usa `@st.cache_data` para funciones pesadas
   - Evita operaciones lentas en cada rerun
4. **Añade un favicon**: Crea `.streamlit/config.toml` con tu icono

## ¿Problemas?

### La app no arranca
- Revisa que `requirements.txt` esté completo
- Mira los logs en Streamlit Cloud (botón "Manage app" > "Logs")

### Error de dependencias
- Asegúrate de que las versiones en `requirements.txt` sean compatibles
- Prueba localmente con `pip install -r requirements.txt`

### La app es lenta
- Usa `@st.cache_data` para operaciones costosas
- Reduce el tamaño de los datos iniciales

## Contacto

Si tienes dudas sobre el deployment, abre un issue en el repo o consulta:
- Docs oficiales: https://docs.streamlit.io/streamlit-community-cloud
- Foro de Streamlit: https://discuss.streamlit.io/
