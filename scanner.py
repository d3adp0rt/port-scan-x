import asyncio
import time
import socket
from typing import List, Tuple, Optional, Callable


async def scan_port(ip: str, port: int, timeout: float = 1.0) -> Tuple[int, str, Optional[int]]:
    """
    Асинхронное сканирование одного порта
    
    Args:
        ip: IP-адрес или домен
        port: номер порта
        timeout: таймаут в секундах
        
    Returns:
        Tuple[порт, статус, время_в_мс]
    """
    try:
        start_time = time.time()
        
        # Создаем асинхронное соединение
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port), 
            timeout=timeout
        )
        
        # Закрываем соединение
        writer.close()
        await writer.wait_closed()
        
        elapsed_ms = round((time.time() - start_time) * 1000)
        return port, "open", elapsed_ms
        
    except asyncio.TimeoutError:
        return port, "timeout", None
    except ConnectionRefusedError:
        return port, "closed", None
    except Exception as e:
        return port, "error", None


async def scan_ports(
    ip: str, 
    ports: List[int], 
    concurrency: int = 500, 
    timeout: float = 1.0,
    progress_callback: Optional[Callable] = None
) -> List[Tuple[int, str, Optional[int]]]:
    """
    Асинхронное сканирование списка портов
    
    Args:
        ip: IP-адрес или домен
        ports: список портов для сканирования
        concurrency: количество одновременных соединений
        timeout: таймаут для каждого порта
        progress_callback: функция обратного вызова для прогресса
        
    Returns:
        Список результатов [(порт, статус, время)]
    """
    # Семафор для ограничения количества одновременных соединений
    semaphore = asyncio.Semaphore(concurrency)
    
    async def scan_with_semaphore(port: int):
        async with semaphore:
            result = await scan_port(ip, port, timeout)
            if progress_callback:
                progress_callback()
            return result
    
    # Запускаем все задачи параллельно
    results = await asyncio.gather(
        *(scan_with_semaphore(port) for port in ports),
        return_exceptions=True
    )
    
    # Фильтруем исключения
    valid_results = []
    for result in results:
        if isinstance(result, tuple):
            valid_results.append(result)
        else:
            # Если произошла ошибка, добавляем как ошибку
            valid_results.append((0, "error", None))
    
    return valid_results


async def validate_host(host: str) -> bool:
    """
    Проверка доступности хоста
    
    Args:
        host: IP-адрес или доменное имя
        
    Returns:
        True если хост доступен, False иначе
    """
    try:
        # Пытаемся резолвить хост
        loop = asyncio.get_event_loop()
        await loop.getaddrinfo(host, None)
        return True
    except Exception:
        return False


def get_common_ports() -> List[int]:
    """
    Возвращает список наиболее часто используемых портов
    """
    return [
        21, 22, 23, 25, 53, 80, 110, 111, 135, 139, 143, 443, 993, 995,
        1723, 3306, 3389, 5432, 5900, 8080, 8443, 8888, 9090
    ]


async def banner_grab(ip: str, port: int, timeout: float = 2.0) -> Optional[str]:
    """
    Получение баннера с открытого порта
    
    Args:
        ip: IP-адрес
        port: порт
        timeout: таймаут
        
    Returns:
        Строка баннера или None
    """
    try:
        reader, writer = await asyncio.wait_for(
            asyncio.open_connection(ip, port),
            timeout=timeout
        )
        
        # Ждем данные в течение короткого времени
        try:
            data = await asyncio.wait_for(reader.read(1024), timeout=1.0)
            banner = data.decode('utf-8', errors='ignore').strip()
            
            writer.close()
            await writer.wait_closed()
            
            return banner if banner else None
        except asyncio.TimeoutError:
            writer.close()
            await writer.wait_closed()
            return None
            
    except Exception:
        return None