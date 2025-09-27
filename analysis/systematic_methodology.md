# Metodología Sistemática para Análisis de Infraestructura Satelital

## Problema Identificado

El análisis inicial mostró una clasificación poco rigurosa donde un nodo con RTT de 252ms y confidence de 0.5 fue considerado como "posible satelite". Esto no es suficientemente sistemático para un estudio científico.

## Metodología Mejorada

### 1. Sistema de Puntuación Multi-Factor

#### Clasificación Satelital (Requiere evidencia múltiple)
```
Puntuación Satelital = RTT_score + Hostname_score + ASN_score + Geographic_score + IP_range_score

Umbrales:
- Score ≥ 4 AND Confidence ≥ 0.7 → Satelite confirmado
- Score ≥ 6 (cualquier confidence) → Satelite con evidencia fuerte
- Score < 4 → No satelite
```

#### Factores de Puntuación:
- **RTT > 240ms**: +3 puntos (GEO confirmado)
- **RTT > 200ms**: +1 punto (posible satelite)
- **Hostname satelital**: +3 puntos ('sat', 'satellite', 'jupiter', 'spaceway')
- **ASN Hughes**: +2 puntos (7155, 22394)
- **Ubicación internacional**: +1 punto
- **Rango IP Hughes**: Aumenta confidence en 0.6

### 2. Cálculo de Confidence Sistemático

#### Evidencia Fuerte (0.7-0.9)
- Hostname contiene "hughes": +0.8
- ASN confirmado Hughes: +0.9
- Organización Hughes: +0.8

#### Evidencia Moderada (0.3-0.7)
- Nombres satelitales Hughes: +0.6
- RTT > 240ms: +0.7
- RTT > 200ms: +0.3 (menor confidence)
- Rango IP Hughes: +0.6

#### Evidencia Débil (0.1-0.3)
- Servicios detectados: +0.1 por servicio (máx 0.3)
- Ubicación internacional: +0.2

#### Penalizaciones
- RTT < 20ms con indicador satelital: -0.4

### 3. Clasificación Rigurosa

#### Satelites
- **Requiere**: Score ≥ 4 AND Confidence ≥ 0.7
- **O**: Score ≥ 6 (evidencia abrumadora)

#### Gateways
- **Requiere**: Score ≥ 3 AND Confidence ≥ 0.5
- **Factores**: Hostname gateway, RTT 20-100ms, servicios DNS/HTTP

#### Infraestructura Terrestre
- **Requiere**: RTT < 100ms AND Confidence ≥ 0.3
- **Incluye**: Equipos de red, servidores, routers

### 4. Validación Geográfica

#### Rangos Geográficos
- **Norteamérica**: 25°-70°N, 170°-50°W (mercado primario Hughes)
- **Internacional**: Fuera de Norteamérica (más probable infraestructura satelital)

## Aplicación al Caso Actual

### Nodo 69.46.153.145 (Singapur)
```
Análisis sistemático:
- RTT: 252ms → +1 punto (>200ms pero <240ms)
- Hostname: null → +0 puntos
- ASN: null → +0 puntos  
- Ubicación: Singapur → +1 punto (internacional)
- IP Range: 69.46.x.x → +0.6 confidence

Score total: 2 puntos
Confidence: 0.5 (0.3 RTT + 0.2 internacional)

Resultado: NO SATELITE (score < 4, confidence < 0.7)
Clasificación: terrestrial_infrastructure o unknown
```

### Conclusión Sistemática
El nodo **NO debe clasificarse como satelite** porque:
1. Score insuficiente (2 < 4)
2. Confidence baja (0.5 < 0.7)
3. RTT borderline (252ms cerca pero no >240ms)
4. Falta evidencia corroborativa (hostname, ASN)

## Recomendaciones

### Para Confirmar Satelites
1. **RTT > 240ms** (requisito mínimo GEO)
2. **Múltiples mediciones** para confirmar consistencia
3. **Evidencia corroborativa** (hostname, ASN, servicios)
4. **Análisis temporal** para descartar congestión temporal

### Para Estudios Futuros
1. **Mediciones repetidas** en diferentes momentos
2. **Correlación con datos públicos** de Hughes
3. **Análisis de patrones de tráfico**
4. **Validación con herramientas independientes**

## Metodología de Validación

### Criterios de Aceptación
- **Satelite confirmado**: Score ≥ 4 AND Confidence ≥ 0.7
- **Satelite probable**: Score ≥ 6 (evidencia abrumadora)
- **Requiere más análisis**: Score 3-4 OR Confidence 0.5-0.7
- **No satelite**: Score < 3 AND Confidence < 0.5

### Proceso de Revisión
1. Aplicar scoring sistemático
2. Calcular confidence riguroso
3. Validar con criterios múltiples
4. Documentar incertidumbres
5. Recomendar análisis adicional si necesario

Esta metodología asegura que solo los nodos con evidencia sólida y múltiple se clasifiquen como satelitales, evitando falsos positivos y manteniendo rigor científico.
