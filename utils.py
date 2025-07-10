import re
import socket
import ipaddress
import json
from typing import List, Union, Dict, Any
from datetime import datetime


def parse_ports(port_string: str) -> List[int]:
    """
    Парсинг строки портов в список интов
    
    Поддерживаемые форматы:
    - "80" - один порт
    - "80,443,8080" - список портов
    - "20-80" - диапазон портов
    - "20-80,443,8080-8090" - комбинированный формат
    
    Args:
        port_string: строка с портами
        
    Returns:
        Список портов
        
    Raises:
        ValueError: если формат некорректен
    """
    if not port_string or not port_string.strip():
        raise ValueError("Пустая строка портов")
    
    ports = set()
    
    # Разделяем по запятым
    parts = port_string.strip().split(',')
    
    for part in parts:
        part = part.strip()
        
        if '-' in part:
            # Диапазон портов
            try:
                start, end = map(int, part.split('-'))
                if start < 1 or end > 65535 or start > end:
                    raise ValueError(f"Некорректный диапазон портов: {part}")
                ports.update(range(start, end + 1))
            except ValueError as e:
                if "invalid literal" in str(e):
                    raise ValueError(f"Некорректный формат диапазона: {part}")
                raise
        else:
            # Один порт
            try:
                port = int(part)
                if port < 1 or port > 65535:
                    raise ValueError(f"Порт вне диапазона 1-65535: {port}")
                ports.add(port)
            except ValueError:
                raise ValueError(f"Некорректный номер порта: {part}")
    
    return sorted(list(ports))


def validate_ip_or_domain(host: str) -> bool:
    """
    Проверка корректности IP-адреса или доменного имени
    
    Args:
        host: IP-адрес или доменное имя
        
    Returns:
        True если корректно, False иначе
    """
    if not host or not host.strip():
        return False
    
    host = host.strip()
    
    # Проверка IP-адреса
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    
    # Проверка доменного имени
    if len(host) > 253:
        return False
    
    # Простая проверка формата домена
    domain_pattern = re.compile(
        r'^(?!-)[A-Za-z0-9-]{1,63}(?<!-)(\.[A-Za-z0-9-]{1,63})*$'
    )
    
    return bool(domain_pattern.match(host))


def resolve_hostname(hostname: str) -> str:
    """
    Резолвинг доменного имени в IP-адрес
    
    Args:
        hostname: доменное имя
        
    Returns:
        IP-адрес
        
    Raises:
        socket.gaierror: если не удалось резолвить
    """
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        raise


def parse_cidr(cidr: str) -> List[str]:
    """
    Парсинг CIDR-нотации в список IP-адресов
    
    Args:
        cidr: CIDR-нотация (например, "192.168.1.0/24")
        
    Returns:
        Список IP-адресов
        
    Raises:
        ValueError: если CIDR некорректен
    """
    try:
        network = ipaddress.ip_network(cidr, strict=False)
        return [str(ip) for ip in network.hosts()]
    except ValueError:
        raise ValueError(f"Некорректная CIDR-нотация: {cidr}")


def get_port_description(port: int) -> str:
    """
    Получение описания порта
    
    Args:
        port: номер порта
        
    Returns:
        Описание порта
    """
    well_known_ports = {
        21: "FTP",
        22: "SSH",
        23: "Telnet",
        25: "SMTP",
        53: "DNS",
        80: "HTTP",
        110: "POP3",
        111: "RPC",
        135: "RPC Endpoint",
        139: "NetBIOS",
        143: "IMAP",
        443: "HTTPS",
        993: "IMAPS",
        995: "POP3S",
        1723: "PPTP",
        3306: "MySQL",
        3389: "RDP",
        5432: "PostgreSQL",
        5900: "VNC",
        8080: "HTTP Proxy",
        8443: "HTTPS Alt",
        8888: "HTTP Alt",
        9090: "HTTP Alt"
    }
    
    return well_known_ports.get(port, f"Port {port}")


def save_results_txt(results: List[Dict[str, Any]], filename: str, host: str):
    """
    Сохранение результатов в текстовый файл
    
    Args:
        results: список результатов
        filename: имя файла
        host: сканируемый хост
    """
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"Port Scan Results for {host}\n")
        f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Ports Scanned: {len(results)}\n")
        f.write("-" * 50 + "\n\n")
        
        for result in results:
            port = result['port']
            status = result['status']
            time_ms = result.get('time_ms', 'N/A')
            description = get_port_description(port)
            
            f.write(f"Port {port:5d} ({description:15s}): {status:8s}")
            if time_ms != 'N/A':
                f.write(f" ({time_ms}ms)")
            f.write("\n")


def save_results_json(results: List[Dict[str, Any]], filename: str, host: str):
    """
    Сохранение результатов в JSON файл
    
    Args:
        results: список результатов
        filename: имя файла
        host: сканируемый хост
    """
    output = {
        "host": host,
        "scan_date": datetime.now().isoformat(),
        "total_ports": len(results),
        "results": results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)


def format_time(milliseconds: int) -> str:
    """
    Форматирование времени в читаемый вид
    
    Args:
        milliseconds: время в миллисекундах
        
    Returns:
        Отформатированная строка времени
    """
    if milliseconds is None:
        return "N/A"
    
    if milliseconds < 1000:
        return f"{milliseconds}ms"
    else:
        seconds = milliseconds / 1000
        return f"{seconds:.1f}s"


def get_status_color(status: str) -> str:
    """
    Получение цвета для статуса порта
    
    Args:
        status: статус порта
        
    Returns:
        Цвет в формате CSS
    """
    colors = {
        "open": "#4CAF50",      # зеленый
        "closed": "#9E9E9E",    # серый
        "timeout": "#FF9800",   # оранжевый
        "error": "#F44336"      # красный
    }
    
    return colors.get(status, "#000000")


def create_summary(results: List[Dict[str, Any]]) -> Dict[str, int]:
    """
    Создание сводки результатов сканирования
    
    Args:
        results: список результатов
        
    Returns:
        Словарь со статистикой
    """
    summary = {
        "total": len(results),
        "open": 0,
        "closed": 0,
        "timeout": 0,
        "error": 0
    }
    
    for result in results:
        status = result.get("status", "error")
        if status in summary:
            summary[status] += 1
    
    return summary