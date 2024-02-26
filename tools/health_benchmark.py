import psutil
from sqlalchemy import select, text

from definitions import DESC_CPU, DESC_MEMORY


def postgres_health_check(db):
    try:
        result_proxy = db.execute(select(1))
        result = result_proxy.scalar()

        if result == 1:
            return {'check': 'PostgreSQL Health', 'status': 'OK'}
        else:
            return {'check': 'PostgreSQL Health', 'status': 'FAIL'}

    except Exception as e:
        print(e)  # log to console
        return {'check': 'PostgreSQL Health', 'status': 'ERROR', 'detail': 'Internal server error'}


async def redis_health_check(redis):
    try:
        pong = await redis.ping()
        if pong:
            return {'check': 'Redis Health', 'status': 'OK'}
        else:
            return {'check': 'Redis Health', 'status': 'FAIL'}

    except Exception as e:
        print(e)  # log to console
        return {'check': 'Redis Health', 'status': 'ERROR', 'detail': 'Internal server error'}


def check_cpu():
    try:
        cpu_percent = psutil.cpu_percent()

        if 0 <= cpu_percent <= 70:
            return {'check': 'CPU', 'status': 'OK', 'detail': DESC_CPU + str(cpu_percent)}
        elif 71 <= cpu_percent <= 90:
            return {'check': 'CPU', 'status': 'WARNING', 'detail': DESC_CPU + str(cpu_percent)}
        elif 91 <= cpu_percent <= 100:
            return {'check': 'CPU', 'status': 'HIGH', 'detail': DESC_CPU + str(cpu_percent)}
        else:
            return {'check': 'CPU', 'status': 'UNKNOWN', 'detail': 'Cannot determine CPU usage'}
    except Exception as e:
        print(e)  # log to console
        return {'check': 'CPU', 'status': 'UNKNOWN', 'detail': 'Cannot determine CPU usage'}


def check_memory():
    bytes_to_gbs = 1073741824
    avail = round(psutil.virtual_memory().available / bytes_to_gbs, 1)
    total = round(psutil.virtual_memory().total / bytes_to_gbs, 1)
    used_mem = round(((total - avail) / total * 100), 1)  # returning total memory in use in %
    if 0 <= used_mem <= 70:
        return {'check': 'MEM', 'status': 'OK', 'detail': DESC_MEMORY + str(used_mem)}
    elif 71 <= used_mem <= 90:
        return {'check': 'MEM', 'status': 'WARNING', 'detail': DESC_MEMORY + str(used_mem)}
    elif 91 <= used_mem <= 100:
        return {'check': 'MEM', 'status': 'HIGH', 'detail': DESC_MEMORY + str(used_mem)}
    else:
        return {'check': 'MEM', 'status': 'UNKNOWN', 'detail': 'Cannot determine MEM usage'}


# Maintenance tasks

def vacuum_db(db):
    try:
        with db.connection() as conn:
            if conn.in_transaction():
                conn.rollback()

            conn.execution_options(isolation_level="AUTOCOMMIT")
            conn.execute(text("VACUUM"))

        return {"status": "success", "message": "VACUUM operation completed successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def analyze_db(db):
    try:
        db.execute(text("ANALYZE"))
        return {"status": "success", "message": "ANALYZE operation completed successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def reindex_db(db):
    try:
        with db.connection() as conn:
            if conn.in_transaction():
                conn.rollback()

            conn.execution_options(isolation_level="AUTOCOMMIT")

            result = conn.execute(
                text("SELECT indexname FROM pg_indexes WHERE schemaname NOT IN ('pg_catalog', 'information_schema')"))
            indexes = [row[0] for row in result]

            for index_name in indexes:
                conn.execute(text(f"REINDEX INDEX {index_name}"))

        return {"status": "success", "message": "REINDEX operation for all indexes completed successfully."}
    except Exception as e:
        return {"status": "error", "message": str(e)}
