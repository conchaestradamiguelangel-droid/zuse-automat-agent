"""Minimum Description Length helpers for Fase 2a."""

from __future__ import annotations

import gzip
import json
from typing import Any

import numpy as np


def serializar_modelo(modelo: dict[str, Any]) -> bytes:
    """Serialize candidate models deterministically."""
    tipo = modelo.get("tipo")
    if tipo == "velocidad_constante":
        return f"v:{modelo['period_t']}:{modelo['displacement_x']}".encode("utf-8")
    if tipo == "periodicidad_constante":
        return f"p:{modelo['period_t']}".encode("utf-8")
    if tipo == "conteo_estructuras_constante":
        return f"n:{modelo['n']}".encode("utf-8")
    if tipo == "paridad_constante":
        return f"q:{modelo['valor']}".encode("utf-8")
    return json.dumps(modelo, sort_keys=True, separators=(",", ":")).encode("utf-8")


def mdl_score(modelo: dict[str, Any], residuos: np.ndarray) -> int:
    """Return len(model) + compressed residual length."""
    residual_bytes = np.asarray(residuos).tobytes()
    return len(serializar_modelo(modelo)) + len(gzip.compress(residual_bytes, compresslevel=9))


def mdl_null(datos: np.ndarray) -> int:
    """Null model: constant mean residuals with explicit signed casting."""
    datos_i16 = np.asarray(datos).astype(np.int16)
    media = int(np.round(np.mean(datos_i16)))
    residuos = datos_i16 - media
    return mdl_score({"tipo": "constante_media"}, residuos.astype(np.int16))
