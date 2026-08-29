<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Mockup Sistema de Gestión - Los Naranjos</title>
    <style>
        :root {
            --bg-gradient: linear-gradient(135deg, #0A1128 0%, #1C2541 100%);
            --card-bg: #253254;
            --text-main: #FFFFFF;
            --text-muted: #A0AEC0;
            --accent-cyan: #00B4D8;
            --accent-yellow: #FFD166;
            --state-cobre: #D97706;
            --border-color: #3A4B7C;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: var(--bg-gradient);
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            overflow-x: hidden;
        }

        header {
            background-color: #0A1128;
            padding: 15px 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border-color);
        }

        .logo-area {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        .logo-placeholder {
            width: 45px;
            height: 45px;
            background-color: var(--accent-yellow);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #0A1128;
            font-weight: bold;
            font-size: 11px;
            text-align: center;
            line-height: 1;
        }

        .brand-info h1 {
            font-size: 18px;
            color: var(--text-main);
        }

        .brand-info p {
            font-size: 12px;
            color: var(--accent-cyan);
        }

        .user-status {
            text-align: right;
            font-size: 14px;
        }

        .main-container {
            display: flex;
            flex: 1;
            height: calc(100vh - 79px);
        }

        nav {
            width: 260px;
            background-color: rgba(10, 17, 40, 0.6);
            border-right: 1px solid var(--border-color);
            padding: 20px 15px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        nav h3 {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-muted);
            padding-left: 10px;
            margin-bottom: 10px;
        }
        .nav-btn {
            background: transparent;
            border: none;
            color: var(--text-muted);
            padding: 12px 15px;
            text-align: left;
            border-radius: 8px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s ease;
        }

        .nav-btn:hover {
            background-color: rgba(255,255,255,0.05);
            color: var(--text-main);
        }

        .nav-btn.active {
            background-color: var(--accent-cyan);
            color: #0A1128;
            font-weight: bold;
        }

        .workspace {
            flex: 1;
            padding: 30px;
            overflow-y: auto;
        }

        .mockup-screen {
            display: none;
        }

        .mockup-screen.active {
            display: block;
        }

        .screen-title {
            font-size: 22px;
            margin-bottom: 20px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 10px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
        }

        .grid-2 {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 25px;
        }

        .split-view {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
        }

        .card {
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
        }

        .btn-action {
            display: block;
            width: 100%;
            background-color: var(--accent-cyan);
            color: #0A1128;
            border: none;
            padding: 14px;
            border-radius: 8px;
            font-weight: bold;
            cursor: pointer;
            text-align: center;
            font-size: 15px;
            margin-top: 15px;
        }

        .btn-action:hover {
            filter: brightness(1.1);
        }

        .mesa-card {
            text-align: center;
            padding: 35px 20px;
            cursor: pointer;
            transition: transform 0.2s;
        }

        .mesa-card:hover {
            transform: translateY(-3px);
        }

        .mesa-card.libre { border-left: 6px solid var(--accent-cyan); }
        .mesa-card.ocupada { border-left: 6px solid var(--state-cobre); }
        .mesa-card.cuenta { border-left: 6px solid var(--accent-yellow); }

        .mesa-card h4 { font-size: 24px; margin-bottom: 5px; }
        .status-tag {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: bold;
            margin-top: 10px;
        }
        .libre .status-tag { background-color: rgba(0,180,216,0.2); color: var(--accent-cyan); }
        .ocupada .status-tag { background-color: rgba(217,119,6,0.2); color: var(--state-cobre); }
        .cuenta .status-tag { background-color: rgba(255,209,102,0.2); color: var(--accent-yellow); }

        .comanda-list {
            list-style: none;
            margin-top: 15px;
        }

        .comanda-item {
            padding: 12px 0;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .comanda-item .nota {
            font-size: 12px;
            color: var(--accent-yellow);
            display: block;
            margin-top: 4px;
        }

        .menu-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 15px;
        }

        .menu-btn {
            background-color: rgba(255,255,255,0.05);
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 15px;
            border-radius: 8px;
            cursor: pointer;
            text-align: left;
            font-size: 14px;
        }

        .menu-btn:hover {
            background-color: rgba(255,255,255,0.1);
            border-color: var(--accent-cyan);
        }

        .anulacion-box {
            background-color: rgba(239, 68, 68, 0.1);
            border: 1px dashed #EF4444;
            padding: 12px;
            border-radius: 8px;
            margin-top: 20px;
            font-size: 13px;
        }

        .kds-card { background-color: #111827; }
        .kds-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
            margin-bottom: 15px;
        }
        .kds-timer { color: var(--accent-yellow); font-weight: bold; }

        .total-box {
            background-color: rgba(0,0,0,0.2);
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            margin: 20px 0;
            border: 1px solid var(--border-color);
        }
        .total-val {
            font-size: 36px;
            color: var(--accent-yellow);
            font-weight: bold;
            margin-top: 5px;
        }
        .pay-methods {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin-top: 15px;
        }
        .pay-btn {
            background: transparent;
            border: 1px solid var(--border-color);
            color: var(--text-main);
            padding: 12px;
            border-radius: 8px;
            cursor: pointer;
            font-weight: bold;
        }
        .pay-btn:hover {
            background-color: rgba(255,255,255,0.05);
            border-color: var(--accent-cyan);
        }

        .kpi-card { text-align: center; padding: 30px; }
        .kpi-title { font-size: 13px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; margin-bottom: 10px; }
        .kpi-value { font-size: 42px; font-weight: bold; color: var(--text-main); }
        .kpi-value.highlight { color: var(--accent-yellow); }
        .kpi-value.alert { color: #EF4444; }

        .table-products { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .table-products th, .table-products td { padding: 14px; text-align: left; border-bottom: 1px solid var(--border-color); }
        .table-products th { background-color: rgba(0,0,0,0.2); color: var(--text-muted); font-size: 13px; text-transform: uppercase; }
        .switch-panic { padding: 6px 12px; border-radius: 6px; font-weight: bold; font-size: 12px; border: none; cursor: pointer; }
        .switch-panic.disponible { background-color: #10B981; color: white; }
        .switch-panic.agotado { background-color: #EF4444; color: white; }
    </style>
</head>
