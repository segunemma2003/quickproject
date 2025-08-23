
#!/usr/bin/env python3
from __future__ import annotations
import argparse, datetime as dt, html, re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
import pandas as pd
import numpy as np

try:
    from asammdf import MDF  # type: ignore
    _ASAMMDF_AVAILABLE = True
except Exception:
    MDF = None  # type: ignore
    _ASAMMDF_AVAILABLE = False

try:
    # from eva_graphics import generate_all_plots
    _GRAPHICS_AVAILABLE = False  # Désactivé temporairement
except Exception:
    _GRAPHICS_AVAILABLE = False
    
def generate_all_plots(*args, **kwargs):
    return {"signals": [], "summary": []}

# Catalogue des exigences avec leurs règles logiques
EXIGENCES_CATALOG = {
    "REQ_SYS_Comm_480": {
        "label": "Communication système stable au réveil",
        "signals": ["HevcWakeUpSleepcommand", "Powerrelaystate"],
        "logic": "all_present",
        "description": "Tous les signaux doivent être présents"
    },
    "REQ_6.519": {
        "label": "Ecart SOC BMS vs affiché dans la bande",
        "signals": ["SOC_BMS", "SOC_Affiche"],
        "logic": "custom",
        "rule": "abs(SOC_BMS - SOC_Affiche) <= 5",
        "description": "L'écart entre SOC_BMS et SOC_Affiche doit être <= 5%"
    },
    "REQ_TEMP_001": {
        "label": "Température batterie dans les limites",
        "signals": ["Temperature_Battery"],
        "logic": "custom",
        "rule": "(Temperature_Battery >= -20) and (Temperature_Battery <= 60)",
        "description": "Température batterie entre -20°C et 60°C"
    },
    "REQ_VOLTAGE_001": {
        "label": "Tension batterie stable",
        "signals": ["Battery_Voltage"],
        "logic": "custom", 
        "rule": "(Battery_Voltage >= 300) and (Battery_Voltage <= 420)",
        "description": "Tension batterie entre 300V et 420V"
    }
}

def read_signal_data(mdf_path: Path, signal_names: List[str]) -> Dict[str, np.ndarray]:
    """Lit les données des signaux depuis un fichier MDF."""
    signal_data = {}
    
    if not mdf_path.exists():
        return signal_data
        
    try:
        if _ASAMMDF_AVAILABLE and mdf_path.suffix.lower() in {".mf4", ".mf3", ".mdf"}:
            mdf = MDF(str(mdf_path))
            channels = set(mdf.channels_db.keys())
            
            for signal in signal_names:
                # Essayer différentes variantes du nom
                variants = [signal, signal.lower(), signal.upper(), 
                           signal.replace("_", ""), signal.replace(" ", "_")]
                
                found_signal = None
                for variant in variants:
                    if variant in channels:
                        found_signal = variant
                        break
                
                if found_signal:
                    try:
                        sig_data = mdf.get(found_signal)
                        signal_data[signal] = sig_data.samples
                    except Exception:
                        signal_data[signal] = np.array([])
                else:
                    signal_data[signal] = np.array([])
                    
        elif mdf_path.suffix.lower() in {".csv", ".txt"}:
            df = pd.read_csv(mdf_path)
            for signal in signal_names:
                if signal in df.columns:
                    signal_data[signal] = df[signal].values
                else:
                    signal_data[signal] = np.array([])
                    
    except Exception as e:
        print(f"Erreur lors de la lecture des signaux: {e}")
        
    return signal_data

def verify_requirement(req_id: str, signal_data: Dict[str, np.ndarray]) -> Dict[str, Any]:
    """Vérifie une exigence donnée avec les données des signaux."""
    if req_id not in EXIGENCES_CATALOG:
        return {"status": "UNKNOWN", "message": "Exigence non définie"}
    
    req = EXIGENCES_CATALOG[req_id]
    required_signals = req["signals"]
    
    # Vérifier la présence des signaux
    missing_signals = []
    available_signals = {}
    
    for signal in required_signals:
        if signal in signal_data and len(signal_data[signal]) > 0:
            available_signals[signal] = signal_data[signal]
        else:
            missing_signals.append(signal)
    
    if missing_signals:
        return {
            "status": "NOK",
            "message": f"Signaux manquants: {', '.join(missing_signals)}",
            "details": req["description"]
        }
    
    # Appliquer la logique de vérification
    if req["logic"] == "all_present":
        return {
            "status": "OK", 
            "message": "Tous les signaux requis sont présents",
            "details": req["description"]
        }
    
    elif req["logic"] == "custom":
        try:
            rule = req["rule"]
            
            # Créer un environnement d'évaluation avec les signaux
            eval_env = {}
            for signal, data in available_signals.items():
                # Utiliser la moyenne pour l'évaluation (ou autre logique selon besoin)
                eval_env[signal] = np.mean(data) if len(data) > 0 else 0
            
            # Évaluer la règle
            eval_env.update({"abs": abs, "np": np})
            
            if eval(rule, {"__builtins__": {}}, eval_env):
                return {
                    "status": "OK",
                    "message": f"Condition respectée: {rule}",
                    "details": req["description"]
                }
            else:
                return {
                    "status": "NOK", 
                    "message": f"Condition non respectée: {rule}",
                    "details": req["description"]
                }
                
        except Exception as e:
            return {
                "status": "ERROR",
                "message": f"Erreur d'évaluation: {str(e)}",
                "details": req["description"]
            }
    
    return {"status": "UNKNOWN", "message": "Logique non implémentée"}

def verify_all_requirements(mdf_path: Path) -> pd.DataFrame:
    """Vérifie toutes les exigences du catalogue."""
    all_signals = []
    for req in EXIGENCES_CATALOG.values():
        all_signals.extend(req["signals"])
    
    # Supprimer les doublons
    unique_signals = list(set(all_signals))
    
    # Lire les données des signaux
    signal_data = read_signal_data(mdf_path, unique_signals)
    
    # Vérifier chaque exigence
    results = []
    for req_id, req_info in EXIGENCES_CATALOG.items():
        verification = verify_requirement(req_id, signal_data)
        results.append({
            "Exigence": req_id,
            "Label": req_info["label"],
            "Signaux": ", ".join(req_info["signals"]),
            "Status": verification["status"],
            "Message": verification["message"],
            "Description": verification["details"]
        })
    
    return pd.DataFrame(results)

def list_mdf_channels(mdf_path: Optional[Path]) -> Set[str]:
    if not mdf_path: return set()
    if mdf_path.exists():
        if _ASAMMDF_AVAILABLE and mdf_path.suffix.lower() in {".mf4",".mf3",".mdf"}:
            try:
                mdf = MDF(str(mdf_path))
                return set(mdf.channels_db.keys())
            except Exception:
                pass
        if mdf_path.suffix.lower() in {".csv",".txt"}:
            try:
                head = pd.read_csv(mdf_path, nrows=0)
                return set(map(str, head.columns))
            except Exception:
                pass
    return set()

def read_feuil3(labels_xlsx: Path) -> pd.DataFrame:
    """Lit l'onglet Feuil3 ou cherche des alternatives."""
    # Essayer d'abord Feuil3
    try:
        df = pd.read_excel(labels_xlsx, sheet_name="Feuil3")
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception:
        pass
    
    # Si Feuil3 n'est pas bon, essayer les autres onglets
    try:
        xl = pd.ExcelFile(labels_xlsx)
        for sheet in xl.sheet_names:
            if "sweet" in sheet.lower():
                df = pd.read_excel(labels_xlsx, sheet_name=sheet)
                df.columns = [str(c).strip() for c in df.columns]
                return df
    except Exception:
        pass
    
    # Retourner un DataFrame vide si rien ne fonctionne
    return pd.DataFrame()

def uc_signals_from_feuil3(f3: pd.DataFrame) -> Dict[str, List[Tuple[str, Optional[str]]]]:
    """Build UC -> list of (internal_name, b_pres_var) based on Feuil3.
       Adapté pour fonctionner avec différentes structures de fichier.
    """
    if f3.empty:
        return {}
    
    # Chercher une colonne qui ressemble à "internal name"
    internal_col = None
    for col in f3.columns:
        if any(term in col.lower() for term in ["internal", "name", "signal"]):
            internal_col = col
            break
    
    # Si pas trouvé, utiliser la première colonne
    if internal_col is None and len(f3.columns) > 0:
        internal_col = f3.columns[0]
    
    if internal_col is None:
        return {}
    
    # Chercher les colonnes UC (format X.Y)
    uc_cols = [c for c in f3.columns if re.fullmatch(r"\d+\.\d+", str(c))]
    
    # Si pas de colonnes UC trouvées, créer des Use Cases factices basés sur les données
    if not uc_cols:
        # Créer des Use Cases basés sur les signaux disponibles
        signals = f3[internal_col].dropna().astype(str).str.strip().tolist()
        if signals:
            # Grouper les signaux par groupes de 5-10
            uc_map = {}
            for i, group_start in enumerate(range(0, len(signals), 8)):
                group_signals = signals[group_start:group_start + 8]
                uc_name = f"UC 1.{i+1} — Groupe {i+1}"
                uc_map[uc_name] = [(sig, None) for sig in group_signals]
            return uc_map
    
    # Traitement normal avec colonnes UC
    bpres_uc_col = next((c for c in f3.columns if c.lower().startswith("b_pres_sig_uc")), None)
    uc_map: Dict[str, List[Tuple[str, Optional[str]]]] = {}
    
    for uc in uc_cols:
        mask = f3[uc].astype(str).str.strip().isin(["1","1.0","True","true"])
        rows = f3.loc[mask & f3[internal_col].notna(), [internal_col] + ([bpres_uc_col] if bpres_uc_col in f3.columns else [])]
        pairs: List[Tuple[str, Optional[str]]] = []
        for _, r in rows.iterrows():
            name = str(r[internal_col]).strip()
            bpres = str(r[bpres_uc_col]).strip() if bpres_uc_col in rows.columns and pd.notna(r[bpres_uc_col]) else None
            pairs.append((name, bpres))
        
        key = f"UC {uc}"
        uc_map[key] = pairs
    
    return uc_map

def detect_from_presence(uc_map: Dict[str, List[Tuple[str, Optional[str]]]], channels: Set[str]) -> pd.DataFrame:
    """Return a table with UC, Required, Present, Missing, Status and details per line."""
    records = []
    ch_norm = {c.lower(): c for c in channels}
    def present(sig: str) -> bool:
        s_norms = {sig, sig.lower(), sig.replace(" ","").lower(), sig.replace("_","").lower()}
        return any((x in ch_norm) for x in s_norms)
    for uc, pairs in uc_map.items():
        req = len(pairs); pres = 0; missing_list = []
        for name, _ in pairs:
            if present(name): pres += 1
            else: missing_list.append(name)
        status = "DETECTABLE" if req>0 and pres==req else ("PARTIEL" if pres>0 else "INDISPONIBLE")
        records.append({"UC": uc, "Required": req, "Present": pres, "Missing": ", ".join(missing_list), "Status": status})
    return pd.DataFrame.from_records(records)

def read_flux_mapping(flux_xlsx: Path, mode: str) -> pd.DataFrame:
    """Lit les mappings SWEET depuis le fichier Excel."""
    # Correspondance des modes vers les noms d'onglets réels
    sheet_mapping = {
        "sweet400": ["SYNTH_EVA Sweet 400", "Sweet 400 HEVC", "eva-mapping-sweet400"],
        "sweet500": ["SYNTH_EVA Sweet 500", "Sweet 500 HEVC", "eva-mapping-sweet500"]
    }
    
    possible_sheets = sheet_mapping.get(mode.lower(), [])
    
    # Essayer chaque nom d'onglet possible
    xl = pd.ExcelFile(flux_xlsx)
    for sheet_name in possible_sheets:
        if sheet_name in xl.sheet_names:
            try:
                df = pd.read_excel(flux_xlsx, sheet_name=sheet_name)
                df.columns = [str(c).strip() for c in df.columns]
                
                # Adapter les colonnes selon le format trouvé
                if "Signal SWEET" not in df.columns:
                    # Essayer de créer une structure compatible
                    if len(df.columns) >= 2:
                        # Renommer les premières colonnes
                        new_columns = ["Signal SWEET", "Signal MDF trouvé"]
                        for i, col in enumerate(df.columns[:2]):
                            if i < len(new_columns):
                                df = df.rename(columns={col: new_columns[i]})
                        
                        # Ajouter les colonnes manquantes
                        missing_cols = ["CAN Fallback", "Tx/Rx", "MyF2", "MyF3", "MyF4", "MyF5", "Exigence", "Domaine", "HEVC"]
                        for col in missing_cols:
                            if col not in df.columns:
                                df[col] = "N/A"
                
                return df.drop_duplicates().reset_index(drop=True)
            except Exception:
                continue
    
    # Si aucun onglet ne fonctionne, retourner un DataFrame vide avec la structure attendue
    return pd.DataFrame(columns=["Signal SWEET", "Signal MDF trouvé", "CAN Fallback", "Tx/Rx", "MyF2", "MyF3", "MyF4", "MyF5", "Exigence", "Domaine", "HEVC"])

def read_pval_requirements(pval_xlsm: Path) -> Set[str]:
    df = pd.read_excel(pval_xlsm, sheet_name="REQ")
    col = "DOORS Id" if "DOORS Id" in df.columns else next((c for c in df.columns if str(c).lower().startswith("doors")), None)
    if col is None: return set()
    return set(df[col].dropna().astype(str).str.strip().tolist())

def filter_mapping_by_pval(df_map: pd.DataFrame, doors_ids: Set[str]) -> pd.DataFrame:
    if not doors_ids:
        df_map["_pval_present"] = False
        return df_map
    df = df_map.copy()
    df["_pval_present"] = df["Exigence"].isin(doors_ids)
    return df[df["_pval_present"]].copy().reset_index(drop=True)

def compute_sweet_status(df_map: pd.DataFrame, channels: Set[str]) -> pd.DataFrame:
    def row_status(row) -> str:
        sig = str(row.get("Signal MDF trouvé","")).strip(); fb = str(row.get("CAN Fallback","")).strip()
        if sig and sig in channels: return "OK"
        if fb and fb in channels: return "Fallback"
        return "NOK"
    df = df_map.copy(); df["Statut"] = df.apply(row_status, axis=1); return df

def _html_escape(s: str) -> str: return html.escape(str(s))

def render(out_path: Path, meta: Dict[str,str], uc_table: pd.DataFrame, df_sweet: pd.DataFrame, uc_map: Dict[str, List[Tuple[str, Optional[str]]]], requirements_table: Optional[pd.DataFrame] = None, plots: Optional[Dict] = None):
    css = """body{font-family:system-ui,-apple-system,Segoe UI,Roboto,Arial;margin:24px}
    h1{font-size:28px;margin:0 0 8px}h2{font-size:22px;margin-top:24px;border-bottom:1px solid #eee;padding-bottom:4px}
    table{border-collapse:collapse;width:100%;margin:16px 0}th,td{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}
    th{background:#f7f7f7}.tag{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px}
    .OK{background:#e5f7ea;color:#0c6a2a;border:1px solid #bfe7c9}.NOK{background:#fdecea;color:#8a1c13;border:1px solid #f5c6c2}
    .ERROR{background:#fdecea;color:#8a1c13;border:1px solid #f5c6c2}
    .Fallback{background:#fff7e6;color:#ad6800;border:1px solid #ffe58f}.muted{color:#666}.small{font-size:12px}
    .DETECTABLE{background:#e5f7ea;color:#0c6a2a}.PARTIEL{background:#fff7e6;color:#ad6800}.INDISPONIBLE{background:#fdecea;color:#8a1c13}
    .plot-gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:20px;margin:20px 0}
    .plot-item{text-align:center;border:1px solid #ddd;padding:10px;border-radius:8px}
    .plot-item img{max-width:100%;height:auto;border-radius:4px}"""
    
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M")
    meta_rows = "".join(f"<tr><th>{_html_escape(k)}</th><td>{_html_escape(v)}</td></tr>" for k,v in meta.items())
    sec1 = f"<h2>1) Données véhicule</h2><table><tbody>{meta_rows}<tr><th>Généré le</th><td>{_html_escape(now)}</td></tr></tbody></table>"
    
    # UC summary
    if uc_table is not None and not uc_table.empty:
        rows = "".join(f"<tr><td>{_html_escape(r.UC)}</td><td>{int(r.Required)}</td><td>{int(r.Present)}</td><td>{_html_escape(r.Missing)}</td><td><span class='tag {r.Status}'>{_html_escape(r.Status)}</span></td></tr>" for r in uc_table.itertuples())
        sec2 = f"<h2>2) Use Cases (méthode Feuil3)</h2><table><thead><tr><th>UC</th><th># requis</th><th># présents</th><th>Manquants</th><th>Statut</th></tr></thead><tbody>{rows}</tbody></table>"
    else:
        sec2 = "<h2>2) Use Cases (méthode Feuil3)</h2><p class='muted'>Aucun UC listé dans Feuil3 (ou colonnes 1.x absentes).</p>"
    
    # UC details
    details_html = []
    for uc, pairs in uc_map.items():
        lines = "".join(f"<tr><td>{_html_escape(name)}</td><td>{_html_escape(bpres or '')}</td></tr>" for name, bpres in pairs)
        details_html.append(f"<h3>{_html_escape(uc)}</h3><table><thead><tr><th>internal name</th><th>B_Pres_Sig_UC</th></tr></thead><tbody>{lines}</tbody></table>")
    sec3 = "<h2>3) Détails par UC</h2>" + ("".join(details_html) if details_html else "<p>(aucun détail)</p>")
    
    # Requirements verification
    sec4 = ""
    if requirements_table is not None and not requirements_table.empty:
        req_rows = "".join(
            f"<tr><td>{_html_escape(r.Exigence)}</td><td>{_html_escape(r.Label)}</td><td>{_html_escape(r.Signaux)}</td><td><span class='tag {r.Status}'>{_html_escape(r.Status)}</span></td><td>{_html_escape(r.Message)}</td></tr>" 
            for r in requirements_table.itertuples()
        )
        sec4 = f"<h2>4) Vérification des exigences</h2><table><thead><tr><th>Exigence</th><th>Label</th><th>Signaux</th><th>Status</th><th>Message</th></tr></thead><tbody>{req_rows}</tbody></table>"
    
    # Graphiques
    sec_plots = ""
    if plots and (plots.get("summary") or plots.get("signals")):
        plot_html = "<div class='plot-gallery'>"
        
        # Graphiques de synthèse
        for plot_path in plots.get("summary", []):
            if plot_path.exists():
                plot_html += f"<div class='plot-item'><img src='{plot_path.name}' alt='Graphique de synthèse'><p>{plot_path.stem}</p></div>"
        
        # Premiers graphiques de signaux (limiter à 6)
        for plot_path in plots.get("signals", [])[:6]:
            if plot_path.exists():
                plot_html += f"<div class='plot-item'><img src='{plot_path.name}' alt='Signal {plot_path.stem}'><p>{plot_path.stem}</p></div>"
        
        plot_html += "</div>"
        sec_plots = f"<h2>5) Graphiques</h2>{plot_html}"
    
    # SWEET table
    cols = ["Signal SWEET","Signal MDF trouvé","CAN Fallback","HEVC","Tx/Rx","Domaine","Exigence","MyF2","MyF3","MyF4","MyF5","Statut"]
    present_cols = [c for c in cols if c in df_sweet.columns]
    rows = []
    for r in df_sweet[present_cols].itertuples(index=False):
        tds = []
        for i,c in enumerate(present_cols):
            val = getattr(r, c.replace(" ","_")) if hasattr(r, c.replace(" ","_")) else getattr(r, f"_{i}")
            tds.append(f"<td><span class='tag {html.escape(str(val))}'>{html.escape(str(val))}</span></td>" if c=="Statut" else f"<td>{_html_escape(val)}</td>")
        rows.append("<tr>" + "".join(tds) + "</tr>")
    sec6 = f"<h2>6) SWEET (filtré PVAL) — Statuts</h2><table><thead><tr>{''.join(f'<th>{_html_escape(c)}</th>' for c in present_cols)}</tr></thead><tbody>{''.join(rows)}</tbody></table><p class='small muted'>OK si « Signal MDF trouvé » présent ; Fallback si « CAN Fallback » présent ; sinon NOK.</p>"
    
    html_doc = f"<!doctype html><html lang=fr><head><meta charset='utf-8'/><title>Rapport EVA</title><style>{css}</style></head><body><h1>Rapport de Dépouillement Automatique EVA</h1>{sec1}{sec2}{sec3}{sec4}{sec_plots}{sec6}</body></html>"
    out_path.write_text(html_doc, encoding="utf-8")

# Configuration globale pour l'interface
CONFIG = {
    "myf": None,
    "labels_xlsx": Path("Labels Exemple (3).xlsx"),
    "flux_xlsx": Path("EVA_flux_equivalence_sweet400_500 (1).xlsx"),
    "pval_xlsm": Path("PVAL_SYS_ROBUSTNESS.005_copie_outil.xlsm")
}

def analyser_et_generer_rapport(mdf_path: str, lang: str = "fr", myf: Optional[str] = None) -> Dict[str, Dict]:
    """Analyse un fichier MDF et retourne les résultats de détection des Use Cases."""
    try:
        mdf_file = Path(mdf_path)
        channels = list_mdf_channels(mdf_file)
        
        # Lire Feuil3
        f3 = read_feuil3(CONFIG["labels_xlsx"])
        uc_map = uc_signals_from_feuil3(f3)
        uc_table = detect_from_presence(uc_map, channels) if uc_map else pd.DataFrame()
        
        # Vérifier les exigences
        requirements_table = verify_all_requirements(mdf_file)
        
        # Lire quelques signaux pour les graphiques
        signal_names = []
        for req in EXIGENCES_CATALOG.values():
            signal_names.extend(req["signals"])
        signal_names = list(set(signal_names))[:10]  # Limiter à 10 signaux
        
        signal_data = read_signal_data(mdf_file, signal_names)
        
        # Générer les graphiques
        plots = generate_all_plots(signal_data, requirements_table, uc_table)
        
        # Générer rapport HTML
        output_path = Path("rapport_eva.html")
        meta = {
            "VIN": "N/A",
            "SWID": "N/A", 
            "Mode": "sweet400",
            "Méthode UC": "Feuil3 (Labels Exemple)",
            "Fichier MDF": mdf_file.name,
            "Labels": CONFIG["labels_xlsx"].name,
            "Flux SWEET": CONFIG["flux_xlsx"].name,
            "PVAL": CONFIG["pval_xlsm"].name
        }
        
        df_map = read_flux_mapping(CONFIG["flux_xlsx"], "sweet400")
        doors = read_pval_requirements(CONFIG["pval_xlsm"])
        df_map_pval = filter_mapping_by_pval(df_map, doors) if doors else df_map.assign(_pval_present=False)
        df_sweet = compute_sweet_status(df_map_pval, channels)
        
        render(output_path, meta, uc_table, df_sweet, uc_map, requirements_table, plots)
        
        # Retourner les résultats pour l'interface
        results = {}
        if not uc_table.empty:
            for _, row in uc_table.iterrows():
                status = "detected" if row["Status"] == "DETECTABLE" else "not_detected"
                results[row["UC"]] = {
                    "status": status,
                    "required": row["Required"],
                    "present": row["Present"],
                    "missing": row["Missing"]
                }
        
        # Ajouter les résultats des exigences
        if not requirements_table.empty:
            results["_requirements"] = {
                "total": len(requirements_table),
                "ok": len(requirements_table[requirements_table["Status"] == "OK"]),
                "nok": len(requirements_table[requirements_table["Status"] == "NOK"]),
                "error": len(requirements_table[requirements_table["Status"] == "ERROR"])
            }
        
        # Ajouter les graphiques
        results["_plots"] = plots
        
        return results
        
    except Exception as e:
        return {"Erreur": {"status": "error", "message": str(e)}}

def verifier_presence_mapping_0p01s(mdf_path: str, mode: str = "sweet400", uc_id: Optional[str] = None, myf: Optional[str] = None) -> pd.DataFrame:
    """Vérifie la présence des signaux SWEET dans le fichier MDF."""
    try:
        mdf_file = Path(mdf_path)
        channels = list_mdf_channels(mdf_file)
        
        df_map = read_flux_mapping(CONFIG["flux_xlsx"], mode)
        doors = read_pval_requirements(CONFIG["pval_xlsm"])
        df_map_pval = filter_mapping_by_pval(df_map, doors) if doors else df_map.assign(_pval_present=False)
        df_sweet = compute_sweet_status(df_map_pval, channels)
        
        return df_sweet
        
    except Exception as e:
        return pd.DataFrame({"Erreur": [str(e)]})

def main():
    ap = argparse.ArgumentParser(description="EVA Detector — méthode Feuil3 + SWEET/PVAL")
    ap.add_argument("--mdf", type=Path, required=False)
    ap.add_argument("--labels_xlsx", type=Path, required=True)  # Feuil3
    ap.add_argument("--flux_xlsx", type=Path, required=True)    # SWEET
    ap.add_argument("--pval_xlsm", type=Path, required=True)    # PVAL REQ
    ap.add_argument("--mode", choices=["sweet400","sweet500"], default="sweet400")
    ap.add_argument("--vin", type=str, default="N/A")
    ap.add_argument("--swid", type=str, default="N/A")
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    channels = list_mdf_channels(args.mdf) if args.mdf else set()

    f3 = read_feuil3(args.labels_xlsx)
    uc_map = uc_signals_from_feuil3(f3)
    uc_table = detect_from_presence(uc_map, channels) if uc_map else pd.DataFrame()

    df_map = read_flux_mapping(args.flux_xlsx, args.mode)
    doors = read_pval_requirements(args.pval_xlsm)
    df_map_pval = filter_mapping_by_pval(df_map, doors) if doors else df_map.assign(_pval_present=False)
    df_sweet = compute_sweet_status(df_map_pval, channels)

    meta = {"VIN": args.vin, "SWID": args.swid, "Mode": args.mode, "Méthode UC": "Feuil3 (Labels Exemple)",
            "Fichier MDF": str(args.mdf) if args.mdf else "(non fourni)", "Labels": args.labels_xlsx.name,
            "Flux SWEET": args.flux_xlsx.name, "PVAL": args.pval_xlsm.name}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    render(args.out, meta, uc_table, df_sweet, uc_map)
    print(f"Rapport généré: {args.out}")

if __name__ == "__main__":
    main()
