# coding: utf-8
import os
import json
import re
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

DB_FILE = 'pedidos_render.json'
SECRET_SYNC_TOKEN = os.environ.get('SYNC_SECRET', 'spfc2026_segredo_sync')

HTML_RASTREIO = r"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tricolor Tickets — Acompanhamento do Torcedor</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --spfc-red: #E41B17;
            --spfc-red-hover: #ff3333;
            --spfc-red-glow: rgba(228, 27, 23, 0.4);
            --spfc-black: #0D0E12;
            --spfc-white: #FFFFFF;
            --spfc-gold: #F1C40F;
            --spfc-gold-glow: rgba(241, 196, 15, 0.4);
            --spfc-card: rgba(18, 19, 26, 0.88);
            --spfc-border: rgba(255, 255, 255, 0.10);
            --spfc-muted: #8E94A5;
            --spfc-text: #F1F2F6;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(180deg, rgba(8, 9, 13, 0.72) 0%, rgba(13, 14, 18, 0.88) 100%),
                        url('/morumbi_festa_noite.jpg') center center / cover no-repeat fixed;
            color: var(--spfc-text);
            min-height: 100vh;
            padding: 24px 16px;
            display: flex;
            justify-content: center;
        }

        .container {
            width: 100%;
            max-width: 580px;
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        /* LISTRAS TRICOLORES OFICIAIS (VERMELHO / BRANCO / PRETO) */
        .tricolor-stripe {
            height: 5px;
            width: 100%;
            border-radius: 4px 4px 0 0;
            background: linear-gradient(90deg, 
                var(--spfc-red) 0%, var(--spfc-red) 33.33%, 
                var(--spfc-white) 33.33%, var(--spfc-white) 66.66%, 
                #000000 66.66%, #000000 100%
            );
        }

        /* CARDS GERAIS COM EFEITO VIDRO FOSCO E GLOW SUAVE DE SINALIZADOR */
        .glass-card {
            background: var(--spfc-card);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(228, 27, 23, 0.35);
            border-radius: 14px;
            box-shadow: 0 16px 36px rgba(0, 0, 0, 0.75), 0 0 25px rgba(228, 27, 23, 0.12);
            overflow: hidden;
        }

        /* HEADER */
        .header-card {
            padding: 22px 18px 20px;
            text-align: center;
            position: relative;
        }
        .header-badge {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: #000;
            border: 1px solid var(--spfc-border);
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 900;
            letter-spacing: 0.5px;
            color: #fff;
            margin-bottom: 10px;
        }
        .header-title {
            font-size: 20px;
            font-weight: 900;
            color: #fff;
            letter-spacing: -0.5px;
        }
        .header-subtitle {
            font-size: 12px;
            color: var(--spfc-muted);
            margin-top: 4px;
        }

        /* MATCH CARD — ORGANIZADO & CLIMA DE DECISÃO */
        .match-card {
            padding: 16px 18px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            position: relative;
        }
        .match-competition-badge {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            background: rgba(0, 0, 0, 0.65);
            border: 1px solid rgba(228, 27, 23, 0.45);
            padding: 6px 16px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 800;
            color: #fff;
            letter-spacing: 0.5px;
            text-transform: uppercase;
            align-self: center;
            box-shadow: 0 0 12px rgba(228, 27, 23, 0.2);
        }
        .match-teams-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 4px 6px;
        }
        .team-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            width: 42%;
            text-align: center;
        }
        .team-initials {
            font-size: 11px;
            font-weight: 900;
            background: rgba(228, 27, 23, 0.25);
            color: #ff4757;
            padding: 2px 8px;
            border-radius: 4px;
            border: 1px solid rgba(228, 27, 23, 0.4);
            letter-spacing: 1px;
        }
        .team-box.away .team-initials {
            background: rgba(255, 255, 255, 0.1);
            color: #fff;
            border-color: rgba(255, 255, 255, 0.2);
        }
        .team-name {
            font-size: 15px;
            font-weight: 900;
            color: #fff;
            letter-spacing: -0.3px;
        }
        .team-role {
            font-size: 10px;
            font-weight: 700;
            color: var(--spfc-muted);
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }
        .match-vs-divider {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .vs-text {
            font-size: 15px;
            font-weight: 900;
            color: var(--spfc-red);
            background: #000;
            width: 34px;
            height: 34px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            border: 2px solid rgba(228, 27, 23, 0.6);
            box-shadow: 0 0 12px rgba(228, 27, 23, 0.5);
        }
        .match-meta-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 8px;
            width: 100%;
        }
        .meta-pill {
            background: rgba(0, 0, 0, 0.55);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 8px 6px;
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            gap: 2px;
        }
        .meta-label {
            font-size: 9px;
            font-weight: 700;
            color: var(--spfc-muted);
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .meta-value {
            font-size: 11px;
            font-weight: 800;
            color: #fff;
            white-space: nowrap;
        }

        /* SEARCH CARD */
        .search-card {
            padding: 22px 20px;
            text-align: center;
        }
        .input-cpf {
            width: 100%;
            background: #000;
            border: 1px solid var(--spfc-border);
            padding: 12px;
            border-radius: 8px;
            color: #fff;
            font-family: 'JetBrains Mono', monospace;
            font-size: 16px;
            text-align: center;
            margin: 12px 0;
            outline: none;
            transition: border-color 0.2s;
        }
        .input-cpf:focus { border-color: var(--spfc-red); }
        .btn-search {
            width: 100%;
            background: var(--spfc-red);
            color: #fff;
            border: none;
            padding: 12px;
            border-radius: 8px;
            font-weight: 800;
            font-size: 14px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn-search:hover { background: var(--spfc-red-hover); }

        /* STATUS HERO CARD (EM ANDAMENTO) */
        .hero-progress {
            padding: 20px 18px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            border-top: 3px solid var(--spfc-red);
        }
        .status-badge-active {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(228, 27, 23, 0.15);
            border: 1px solid rgba(228, 27, 23, 0.5);
            padding: 5px 14px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 800;
            color: #ff5252;
            letter-spacing: 0.5px;
        }
        .pulse-red-dot {
            width: 8px;
            height: 8px;
            background: var(--spfc-red);
            border-radius: 50%;
            animation: pulseRed 1.5s infinite;
        }
        @keyframes pulseRed {
            0% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(228, 27, 23, 0.7); }
            70% { transform: scale(1); opacity: 1; box-shadow: 0 0 0 6px rgba(228, 27, 23, 0); }
            100% { transform: scale(0.95); opacity: 0.8; box-shadow: 0 0 0 0 rgba(228, 27, 23, 0); }
        }

        .hero-progress-title {
            font-size: 17px;
            font-weight: 900;
            color: #fff;
        }
        .hero-progress-desc {
            font-size: 12px;
            color: #c5cbd8;
            line-height: 1.5;
        }
        .order-info-grid {
            width: 100%;
            background: rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 8px;
            padding: 12px 14px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px;
            text-align: left;
            font-size: 11px;
        }

        /* HERO CARD (CONCLUÍDO COM SUCESSO) */
        .hero-success {
            padding: 24px 18px;
            text-align: center;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 12px;
            border-top: 3px solid var(--spfc-gold);
            background: linear-gradient(145deg, rgba(30, 20, 20, 0.95) 0%, rgba(15, 15, 22, 0.98) 100%);
            box-shadow: 0 10px 30px rgba(241, 196, 15, 0.15);
        }
        .hero-badge-gold {
            background: var(--spfc-gold);
            color: #000;
            font-size: 11px;
            font-weight: 900;
            padding: 5px 14px;
            border-radius: 20px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .hero-success-title {
            font-size: 19px;
            font-weight: 900;
            color: #fff;
        }
        .hero-details-grid {
            width: 100%;
            background: rgba(0, 0, 0, 0.55);
            border: 1px solid rgba(241, 196, 15, 0.3);
            border-radius: 10px;
            padding: 14px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            text-align: left;
            margin-top: 4px;
        }
        .detail-item {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .detail-label {
            font-size: 10px;
            font-weight: 700;
            color: var(--spfc-gold);
            text-transform: uppercase;
        }
        .detail-val {
            font-size: 13px;
            font-weight: 800;
            color: #fff;
        }

        /* TIMELINE */
        .timeline-card {
            padding: 20px 18px;
        }
        .timeline-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 18px;
        }
        .timeline-title-text {
            font-size: 14px;
            font-weight: 900;
            color: #fff;
        }
        .live-tag {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            font-size: 10px;
            font-weight: 700;
            color: var(--spfc-red);
            background: rgba(228, 27, 23, 0.1);
            padding: 3px 8px;
            border-radius: 6px;
            border: 1px solid rgba(228, 27, 23, 0.3);
        }

        .timeline {
            display: flex;
            flex-direction: column;
            gap: 20px;
            position: relative;
            padding-left: 32px;
        }
        .timeline::before {
            content: '';
            position: absolute;
            left: 11px;
            top: 10px;
            bottom: 10px;
            width: 2px;
            background: #2b2e40;
        }

        .step-item {
            position: relative;
        }
        .step-icon {
            position: absolute;
            left: -32px;
            top: 0;
            width: 24px;
            height: 24px;
            border-radius: 50%;
            background: #191b26;
            border: 2px solid #363a52;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 800;
            color: var(--spfc-muted);
            z-index: 2;
        }
        .step-item.completed .step-icon {
            background: var(--spfc-red);
            border-color: #fff;
            color: #fff;
            box-shadow: 0 0 8px var(--spfc-red-glow);
        }
        .step-item.active .step-icon {
            background: #000;
            border-color: var(--spfc-gold);
            color: var(--spfc-gold);
            box-shadow: 0 0 10px var(--spfc-gold-glow);
        }
        .step-item.success .step-icon {
            background: var(--spfc-gold);
            border-color: #fff;
            color: #000;
            box-shadow: 0 0 12px var(--spfc-gold-glow);
        }

        .step-content {
            display: flex;
            flex-direction: column;
            gap: 3px;
        }
        .step-heading {
            font-size: 13px;
            font-weight: 700;
            color: #fff;
        }
        .step-desc {
            font-size: 11px;
            color: #a4adc1;
            line-height: 1.4;
        }
        .step-time {
            font-size: 10px;
            color: #72798e;
            font-family: 'JetBrains Mono', monospace;
            margin-top: 2px;
        }

        /* DISCLAIMER LEGAL & NOTA DE INDEPENDÊNCIA */
        .disclaimer-card {
            padding: 16px 18px;
            background: rgba(10, 11, 16, 0.85);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            text-align: center;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }
        .disclaimer-title {
            font-size: 11px;
            font-weight: 800;
            color: var(--spfc-muted);
            letter-spacing: 0.5px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
        }
        .disclaimer-text {
            font-size: 11px;
            color: #7d8498;
            line-height: 1.5;
            text-align: justify;
        }
        .disclaimer-text strong {
            color: #a6afc5;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- HEADER -->
        <div class="glass-card">
            <div class="tricolor-stripe"></div>
            <div class="header-card">
                <div class="header-badge">
                    <span style="color:var(--spfc-red)">●</span>
                    <span style="color:#fff">●</span>
                    <span style="color:#666">●</span>
                    <span>TRICOLOR TICKETS</span>
                </div>
                <h1 class="header-title">Acompanhamento do Torcedor</h1>
                <p class="header-subtitle">Assessoria e Suporte Independente ao Torcedor São-Paulino</p>
            </div>
        </div>

        <!-- MATCH INFO (ORGANIZADO & CLIMA DE DECISÃO) -->
        <div class="glass-card match-card">
            <div class="match-competition-badge">
                <span>🏆</span>
                <span id="matchComp">CONMEBOL Sul-Americana • Quartas</span>
            </div>
            <div class="match-teams-row">
                <div class="team-box home">
                    <span class="team-initials">SPFC</span>
                    <span class="team-name">SÃO PAULO FC</span>
                    <span class="team-role">MANDANTE</span>
                </div>
                <div class="match-vs-divider">
                    <div class="vs-text">VS</div>
                </div>
                <div class="team-box away">
                    <span class="team-initials" id="opponentInitials">BOC</span>
                    <span class="team-name" id="opponentName">BOCA JUNIORS</span>
                    <span class="team-role">VISITANTE</span>
                </div>
            </div>
            <div class="match-meta-grid">
                <div class="meta-pill">
                    <span class="meta-label">🏟️ Estádio</span>
                    <span class="meta-value">MorumBIS</span>
                </div>
                <div class="meta-pill">
                    <span class="meta-label">📅 Data</span>
                    <span class="meta-value" id="matchDate">15/09/2026</span>
                </div>
                <div class="meta-pill">
                    <span class="meta-label">⏰ Horário</span>
                    <span class="meta-value" id="matchTime">21:30 BRT</span>
                </div>
            </div>
        </div>

        <!-- CONTAINER DINÂMICO DE STATUS / DETALHES -->
        <div id="dynamicContainer">
            <div class="glass-card search-card">
                <h3 style="font-size:15px; font-weight:800; color:#fff;">Consulte o Andamento do seu Pedido</h3>
                <p style="font-size:12px; color:var(--spfc-muted); margin-top:4px;">
                    Digite seu CPF cadastrado para verificar os detalhes da sua solicitação:
                </p>
                <input type="text" id="cpfSearchInput" class="input-cpf" placeholder="000.000.000-00" maxlength="14" oninput="mascararInputCPF(this)">
                <button class="btn-search" onclick="buscarPorInput()">Acompanhar Pedido</button>
            </div>
        </div>

        <!-- AVISO LEGAL E DE INDEPENDÊNCIA -->
        <div class="disclaimer-card">
            <div class="disclaimer-title">
                <span>🛡️ AVISO LEGAL & NOTA DE INDEPENDÊNCIA</span>
            </div>
            <p class="disclaimer-text">
                Esta página e este serviço de assessoria <strong>não possuem qualquer vínculo, filiação, homologação ou parceria oficial com a plataforma SPFC Ticket ou com o São Paulo Futebol Clube</strong>. Somos uma assessoria independente cujo propósito é auxiliar e apoiar o torcedor são-paulino em todas as etapas para garantir suas entradas com tranquilidade e apoiar o Tricolor no MorumBIS.
            </p>
        </div>
    </div>

    <script>
        function mascararInputCPF(input) {
            let v = input.value.replace(/\D/g, '');
            if (v.length > 11) v = v.substring(0, 11);
            if (v.length > 9) v = v.replace(/^(\d{3})(\d{3})(\d{3})(\d{1,2})$/, '$1.$2.$3-$4');
            else if (v.length > 6) v = v.replace(/^(\d{3})(\d{3})(\d{1,3})$/, '$1.$2.$3');
            else if (v.length > 3) v = v.replace(/^(\d{3})(\d{1,3})$/, '$1.$2');
            input.value = v;
        }

        function mascararCPF(cpfStr) {
            const clean = (cpfStr || '').replace(/\D/g, '');
            if (clean.length === 11) {
                return `${clean.substring(0,3)}.***.***-${clean.substring(9,11)}`;
            }
            return cpfStr;
        }

        function extrairCPFRota() {
            // Suporta ?cpf=..., /pedido/..., /acompanhar/..., /rastreio/...
            const params = new URLSearchParams(window.location.search);
            if (params.get('cpf')) return params.get('cpf').replace(/\D/g, '');

            const pathParts = window.location.pathname.split('/').filter(p => p.trim());
            for (let part of pathParts) {
                const limpo = part.replace(/\D/g, '');
                if (limpo.length === 11) return limpo;
            }
            return '';
        }

        async function carregarRastreio() {
            const cpf = extrairCPFRota();
            if (!cpf) return;

            const container = document.getElementById('dynamicContainer');

            try {
                const res = await fetch(`/api/rastreio?cpf=${cpf}`, {
                    headers: { 'Bypass-Tunnel-Reminder': 'true' }
                });
                const data = await res.json();

                if (!data.encontrado) {
                    container.innerHTML = `
                        <div class="glass-card search-card">
                            <div style="font-size:32px; margin-bottom:8px;">🔎</div>
                            <h3 style="font-size:16px; font-weight:800; color:#fff;">Solicitação não localizada</h3>
                            <p style="font-size:12px; color:var(--spfc-muted); margin:8px 0 16px;">
                                Não encontramos solicitação ativa para o CPF <strong>${mascararCPF(cpf)}</strong>.
                            </p>
                            <button class="btn-search" onclick="window.location.href='/pedido'">Consultar Outro CPF</button>
                        </div>
                    `;
                    return;
                }

                const ped = data.pedido;
                const isConcluido = ped.status === 'CONCLUIDO';
                const cpfMask = mascararCPF(ped.cpf);
                const agoraHora = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });

                // Ajusta o adversário dinamicamente se detectado no pedido
                const setorSolicitado = ped.setores_solicitados || ped.setor || 'Arquibancada';
                if (ped.id_pedido && ped.id_pedido.includes('8054')) {
                    document.getElementById('opponentName').innerText = 'ATLÉTICO-MG';
                    document.getElementById('matchComp').innerText = 'Brasileirão Betano';
                    document.getElementById('matchDate').innerText = '05/09/2026 - 18:30';
                }

                let heroHtml = '';
                if (isConcluido) {
                    heroHtml = `
                        <div class="glass-card hero-success">
                            <div class="hero-badge-gold">🏆 INGRESSO ADQUIRIDO COM SUCESSO</div>
                            <h2 class="hero-success-title">🎉 Parabéns! Seu Ingresso Está Garantido!</h2>
                            <p style="font-size:12px; color:#d1d8e0;">Sua compra foi aprovada e seu ingresso está vinculado ao seu reconhecimento facial.</p>
                            <div class="hero-details-grid">
                                <div class="detail-item">
                                    <span class="detail-label">Setor Confirmado</span>
                                    <span class="detail-val">🏟️ ${ped.setor_comprado || ped.setor}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Reconhecimento Facial</span>
                                    <span class="detail-val" style="color:var(--spfc-gold);">⭐ BePass Confirmada</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Beneficiário</span>
                                    <span class="detail-val">👤 ${cpfMask}</span>
                                </div>
                                <div class="detail-item">
                                    <span class="detail-label">Código do Pedido</span>
                                    <span class="detail-val" style="font-family:'JetBrains Mono';">📄 ${ped.id_pedido || 'SPFC-OK'}</span>
                                </div>
                            </div>
                            <div style="font-size:11px; color:#fff; background:rgba(0,0,0,0.4); border:1px solid rgba(255,255,255,0.1); padding:8px 12px; border-radius:6px; margin-top:4px;">
                                📸 <strong>Acesso ao MorumBIS:</strong> Basta comparecer ao estádio com seu documento oficial com foto e passar na catraca biométrica do setor!
                            </div>
                        </div>
                    `;
                } else {
                    heroHtml = `
                        <div class="glass-card hero-progress">
                            <div class="status-badge-active">
                                <span class="pulse-red-dot"></span>
                                ATENDIMENTO ATIVO • BUSCA CONTÍNUA
                            </div>
                            <h2 class="hero-progress-title">🔎 Busca Ativa de Ingressos</h2>
                            <p class="hero-progress-desc">
                                Nossa equipe permanece dedicada e atenta, buscando seu(s) ingresso(s) nos setores prioritários (<strong>${setorSolicitado}</strong>). Fique tranquilo, estamos acompanhando todo o processo para você!
                            </p>
                            <div class="order-info-grid">
                                <div><span style="color:var(--spfc-muted);">Beneficiário:</span> <strong>${cpfMask}</strong></div>
                                <div><span style="color:var(--spfc-gold);">Reconhecimento Facial:</span> <strong>⭐ BePass Aprovada</strong></div>
                                <div style="grid-column: span 2;"><span style="color:var(--spfc-muted);">Setor(es) Solicitado(s):</span> <strong>🏟️ ${setorSolicitado}</strong></div>
                            </div>
                        </div>
                    `;
                }

                // Renderiza Timeline
                container.innerHTML = `
                    <div style="display:flex; flex-direction:column; gap:16px;">
                        ${heroHtml}

                        <div class="glass-card timeline-card">
                            <div class="timeline-header">
                                <span class="timeline-title-text">Diário de Acompanhamento</span>
                                <div class="live-tag">
                                    <span class="pulse-red-dot" style="width:6px; height:6px;"></span>
                                    <span>ATUALIZADO ÀS ${agoraHora}</span>
                                </div>
                            </div>

                            <div class="timeline">
                                <!-- ETAPA 1 -->
                                <div class="step-item completed">
                                    <div class="step-icon">✓</div>
                                    <div class="step-content">
                                        <div class="step-heading">1. Solicitação Registrada & Cadastro Facial Verificado</div>
                                        <div class="step-desc">Seus dados foram validados com sucesso e seu reconhecimento facial BePass está vinculado ao MorumBIS.</div>
                                        <div class="step-time">Etapa Concluída</div>
                                    </div>
                                </div>

                                <!-- ETAPA 2 -->
                                <div class="step-item ${isConcluido ? 'completed' : 'active'}">
                                    <div class="step-icon">${isConcluido ? '✓' : '2'}</div>
                                    <div class="step-content">
                                        <div class="step-heading">2. Atendimento Ativo • Busca Contínua</div>
                                        <div class="step-desc">Nossa equipe permanece dedicada e atenta, buscando seu(s) ingresso(s) nos setores prioritários (${setorSolicitado}). Fique tranquilo, estamos acompanhando todo o processo para você.</div>
                                        <div class="step-time">${isConcluido ? 'Etapa Concluída' : 'Em Andamento'}</div>
                                    </div>
                                </div>

                                <!-- ETAPA 3 -->
                                <div class="step-item ${isConcluido ? 'completed' : 'active'}">
                                    <div class="step-icon">${isConcluido ? '✓' : '3'}</div>
                                    <div class="step-content">
                                        <div class="step-heading">3. Acompanhamento e Priorização Contínua</div>
                                        <div class="step-desc">Sua solicitação segue ativa e sob monitoramento constante da nossa equipe. Assim que a aquisição for realizada, você será avisado imediatamente e o comprovante estará aqui.</div>
                                        <div class="step-time">${isConcluido ? 'Etapa Concluída' : 'Atendimento Ativo'}</div>
                                    </div>
                                </div>

                                <!-- ETAPA 4 -->
                                <div class="step-item ${isConcluido ? 'success' : ''}">
                                    <div class="step-icon">${isConcluido ? '🏆' : '4'}</div>
                                    <div class="step-content">
                                        <div class="step-heading" style="${isConcluido ? 'color:var(--spfc-gold); font-weight:800;' : ''}">
                                            ${isConcluido ? '4. Ingresso Adquirido com Sucesso!' : '4. Emissão e Confirmação de Acesso'}
                                        </div>
                                        <div class="step-desc">
                                            ${isConcluido 
                                                ? 'Ingresso emitido com sucesso e vinculado à sua biometria facial BePass para entrada no MorumBIS!' 
                                                : 'Notificação imediata assim que a aquisição for concluída.'}
                                        </div>
                                        <div class="step-time">${isConcluido ? 'Finalizado com Sucesso' : 'Aguardando Aquisição'}</div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                `;

            } catch (err) {
                container.innerHTML = `<div style="text-align:center; padding:20px; color:#ff6b6b;">Erro ao carregar dados. Tentando novamente...</div>`;
            }
        }

        function buscarPorInput() {
            const input = document.getElementById('cpfSearchInput');
            const v = input.value.replace(/\D/g, '');
            if (v.length !== 11) {
                alert('Por favor, digite um CPF válido com 11 dígitos.');
                return;
            }
            window.location.href = `/pedido?cpf=${v}`;
        }

        window.onload = () => {
            carregarRastreio();
            setInterval(carregarRastreio, 3000);
        };
    </script>
</body>
</html>
"""


def limpar_cpf(cpf):
    return re.sub(r'\D', '', str(cpf or ''))

def carregar_pedidos():
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salvar_pedidos(dados):
    try:
        with open(DB_FILE, 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f'Erro ao salvar pedidos: {e}')

@app.route('/')
@app.route('/rastreio')
@app.route('/pedido')
@app.route('/pedido/<path:cpf>')
@app.route('/acompanhar')
def pagina_rastreio(cpf=None):
    return render_template_string(HTML_RASTREIO)

@app.route('/api/rastreio', methods=['GET'])
def api_rastreio():
    cpf_raw = request.args.get('cpf', '')
    cpf_limpo = limpar_cpf(cpf_raw)
    
    pedidos = carregar_pedidos()
    if cpf_limpo in pedidos:
        return jsonify({
            'encontrado': True,
            'pedido': pedidos[cpf_limpo]
        })
    return jsonify({'encontrado': False})

@app.route('/api/sincronizar', methods=['POST'])
def api_sincronizar():
    auth = request.headers.get('Authorization', '')
    token = request.args.get('token', '')
    if auth != f'Bearer {SECRET_SYNC_TOKEN}' and token != SECRET_SYNC_TOKEN:
        return jsonify({'sucesso': False, 'mensagem': 'Nao autorizado'}), 401
        
    data = request.get_json(force=True, silent=True) or {}
    cpf = limpar_cpf(data.get('cpf', ''))
    if not cpf or len(cpf) != 11:
        return jsonify({'sucesso': False, 'mensagem': 'CPF invalido'}), 400
        
    pedidos = carregar_pedidos()
    if data.get('remover'):
        if cpf in pedidos:
            del pedidos[cpf]
            salvar_pedidos(pedidos)
        return jsonify({'sucesso': True, 'mensagem': 'CPF removido com sucesso'})
        
    pedidos[cpf] = {
        'status': data.get('status', 'CONCLUIDO'),
        'cpf': cpf,
        'setor_comprado': data.get('setor_comprado', data.get('setor', 'Setor Garantido')),
        'id_pedido': str(data.get('id_pedido', 'SPFC-OK')),
        'data_hora': data.get('data_hora', ''),
        'setores_solicitados': data.get('setores_solicitados', ''),
        'status_biometria': data.get('status_biometria', 'APROVADO')
    }
    salvar_pedidos(pedidos)
    return jsonify({'sucesso': True, 'mensagem': 'Pedido sincronizado com sucesso!'})

@app.route('/health')
def health():
    return 'OK', 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
