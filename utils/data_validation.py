"""
Validación de datos para modelos de valoración
"""
from typing import List, Union, Any


class ValidationError(Exception):
    """Error personalizado para validaciones"""
    pass


def validate_positive(value: Union[int, float], name: str = "Value") -> Union[int, float]:
    """
    Valida que un valor sea positivo

    Args:
        value: Valor a validar
        name: Nombre del valor para mensajes de error

    Returns:
        El valor si es válido

    Raises:
        ValidationError: Si el valor no es positivo
    """
    if value <= 0:
        raise ValidationError(f"{name} debe ser positivo, recibido: {value}")
    return value


def validate_percentage(value: float, name: str = "Percentage",
                       allow_negative: bool = False) -> float:
    """
    Valida que un valor sea un porcentaje válido

    Args:
        value: Valor a validar (en decimal, ej: 0.10 para 10%)
        name: Nombre del valor para mensajes de error
        allow_negative: Si se permiten porcentajes negativos

    Returns:
        El valor si es válido

    Raises:
        ValidationError: Si el valor no es un porcentaje válido
    """
    if not allow_negative and value < 0:
        raise ValidationError(f"{name} no puede ser negativo, recibido: {value}")

    if abs(value) > 1:
        raise ValidationError(
            f"{name} parece estar en porcentaje, debe estar en decimal (ej: 0.10 en lugar de 10)"
        )

    return value


def validate_list(values: List[Any], min_length: int = 1,
                 name: str = "List") -> List[Any]:
    """
    Valida que una lista tenga la longitud mínima

    Args:
        values: Lista a validar
        min_length: Longitud mínima requerida
        name: Nombre de la lista para mensajes de error

    Returns:
        La lista si es válida

    Raises:
        ValidationError: Si la lista no cumple los requisitos
    """
    if not isinstance(values, list):
        raise ValidationError(f"{name} debe ser una lista")

    if len(values) < min_length:
        raise ValidationError(
            f"{name} debe tener al menos {min_length} elementos, tiene {len(values)}"
        )

    return values


def validate_non_negative(value: Union[int, float], name: str = "Value") -> Union[int, float]:
    """
    Valida que un valor no sea negativo

    Args:
        value: Valor a validar
        name: Nombre del valor para mensajes de error

    Returns:
        El valor si es válido

    Raises:
        ValidationError: Si el valor es negativo
    """
    if value < 0:
        raise ValidationError(f"{name} no puede ser negativo, recibido: {value}")
    return value


def validate_in_range(value: float, min_val: float, max_val: float,
                     name: str = "Value") -> float:
    """
    Valida que un valor esté en un rango específico

    Args:
        value: Valor a validar
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
        name: Nombre del valor para mensajes de error

    Returns:
        El valor si es válido

    Raises:
        ValidationError: Si el valor está fuera del rango
    """
    if not min_val <= value <= max_val:
        raise ValidationError(
            f"{name} debe estar entre {min_val} y {max_val}, recibido: {value}"
        )
    return value
