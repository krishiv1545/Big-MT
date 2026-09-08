from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import connection
from django.http import JsonResponse

from core_APP.models import User

import json
import subprocess
from datetime import datetime


@login_required
def dev_dashboard(request):
    return render(request, "dev_APP/dev_dashboard.html", {
        "active_tab": "overview",
    })


def dev_logs(request):
    return render(request, "dev_APP/dev_logs.html", {
        "active_tab": "logs",
    })


def get_database_info():
    info = {}

    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        info["version"] = cursor.fetchone()[0]

        cursor.execute("SELECT current_database();")
        info["database"] = cursor.fetchone()[0]

        cursor.execute("SELECT pg_database_size(current_database());")
        size_bytes = cursor.fetchone()[0]
        info["size_bytes"] = size_bytes
        info["size_mb"] = round(size_bytes / (1024 * 1024), 2)

        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_stat_activity
            WHERE datname = current_database();
        """)
        info["connections"] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM pg_tables
            WHERE schemaname NOT IN ('pg_catalog', 'information_schema');
        """)
        info["tables"] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM django_migrations;
        """)
        info["migrations"] = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*)
            FROM "core_APP_user";
        """)
        info["users"] = cursor.fetchone()[0]

    return info


def get_pgbackrest_info():
    try:
        result = subprocess.run(
            [
                "/usr/bin/sudo",
                "-u",
                "postgres",
                "/usr/local/bin/bigmt-pgbackrest-info",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )

        data = json.loads(result.stdout)

        if not data:
            return {
                "status": "error",
                "message": "No pgBackRest information returned.",
            }

        stanza = data[0]

        backups = stanza.get("backup", [])
        archive = stanza.get("archive", [])
        repo = stanza.get("repo", [])

        # pgBackRest returns backups chronologically,
        # so the last entry is the newest backup.
        latest_backup = backups[-1] if backups else None

        full_backups = [
            backup
            for backup in backups
            if backup.get("type") == "full"
        ]

        differential_backups = [
            backup
            for backup in backups
            if backup.get("type") == "diff"
        ]

        latest_full = full_backups[-1] if full_backups else None

        for backup in backups:
            backup['timestamp']['start'] = datetime.fromtimestamp(backup['timestamp']['start'])
            backup['timestamp']['stop'] = datetime.fromtimestamp(backup['timestamp']['stop'])

        return {
            "status": stanza.get("status", {}).get(
                "message",
                "unknown",
            ),
            "stanza": stanza.get("name", "bigmt"),
            "backups": backups[::-1],  # Reverse to show newest first
            "latest_backup": latest_backup,
            "full_backups": full_backups,
            "latest_full": latest_full,
            "differential_backups": differential_backups,
            "archive": archive,
            "repo": repo,
        }

    except subprocess.TimeoutExpired:
        return {
            "status": "error",
            "message": "pgBackRest command timed out.",
        }

    except subprocess.CalledProcessError as exc:
        return {
            "status": "error",
            "message": exc.stderr.strip() or "pgBackRest command failed.",
        }

    except json.JSONDecodeError as exc:
        return {
            "status": "error",
            "message": f"Invalid pgBackRest JSON: {exc}",
        }

    except OSError as exc:
        return {
            "status": "error",
            "message": str(exc),
        }


@login_required
def dev_database(request):
    database = None
    pgbackrest = None
    database_error = None

    try:
        database = get_database_info()
    except Exception as exc:
        database_error = str(exc)

    pgbackrest = get_pgbackrest_info()

    return render(
        request,
        "dev_APP/dev_database.html",
        {
            "active_tab": "database",
            "database": database,
            "database_error": database_error,
            "pgbackrest": pgbackrest,
        },
    )


def dev_system(request):
    return render(request, "dev_APP/dev_system.html", {
        "active_tab": "system",
    })


def live(request):
    return JsonResponse({
        "status": "ok",
    })


def ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        return JsonResponse({
            "status": "ok",
            "database": "ok",
        })

    except Exception:
        return JsonResponse({
            "status": "error",
            "database": "error",
        }, status=503)


def health(request):
    database_ok = False

    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

        database_ok = True
    except Exception:
        pass

    if database_ok:
        return JsonResponse({
            "status": "ok",
            "database": "ok",
        })

    return JsonResponse({
        "status": "error",
        "database": "error",
    }, status=503)