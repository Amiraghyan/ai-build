"""
inference_optim_llm.build.builder
=================================

Construction d'engines TensorRT-LLM optimisés avec support de quantification.

Fonctionnalités :
-----------------
* Support FP16, INT8 avec calibration personnalisée.
* Logs détaillés pour debugging et CI.
* Cache intelligent des modèles HuggingFace.
* Gestion robuste des erreurs de compilation.
"""

from __future__ import annotations

import logging
import os
import shutil
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Configuration par défaut
REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_MAX_INPUT_LEN = 4096
DEFAULT_MAX_OUTPUT_LEN = 2048
DEFAULT_BATCH_SIZE = 1


class TensorRTEngineBuilder:
    """
    Builder pour engines TensorRT-LLM avec support avancé de quantification.
    
    Paramètres
    ----------
    model_id : str
        ID HuggingFace ou chemin local du modèle.
    precision : str
        Précision : 'fp16', 'fp32', 'int8'.
    quant_mode : str | None
        Mode de quantification pour INT8 : 'int8', 'int4_weightonly', etc.
    calibration_path : str | None
        Chemin vers les données de calibration pour INT8.
    output_dir : Path
        Répertoire de sortie des engines.
    cache_dir : Path | None
        Répertoire de cache pour les modèles HF (défaut : HF_HOME).
    """

    def __init__(
        self,
        model_id: str,
        *,
        precision: str = "fp16",
        quant_mode: Optional[str] = None,
        calibration_path: Optional[str] = None,
        output_dir: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
        max_input_len: int = DEFAULT_MAX_INPUT_LEN,
        max_output_len: int = DEFAULT_MAX_OUTPUT_LEN,
        batch_size: int = DEFAULT_BATCH_SIZE,
    ) -> None:
        self.model_id = model_id
        self.precision = precision
        self.quant_mode = quant_mode
        self.calibration_path = calibration_path
        self.max_input_len = max_input_len
        self.max_output_len = max_output_len
        self.batch_size = batch_size
        
        # Répertoires
        self.output_dir = output_dir or REPO_ROOT / "engines"
        self.cache_dir = cache_dir or Path(os.getenv("HF_HOME", Path.home() / ".cache" / "huggingface"))
        self.tmp_dir = REPO_ROOT / "tmp"
        
        # Validation des paramètres
        self._validate_params()
        
        logger.info(
            "Initialisation du builder TensorRT-LLM: %s (%s), sortie: %s",
            self.model_id, self.precision, self.output_dir
        )

    def _validate_params(self) -> None:
        """Validation des paramètres d'entrée."""
        valid_precisions = {"fp16", "fp32", "int8", "int4"}
        if self.precision not in valid_precisions:
            raise ValueError(f"Précision non supportée: {self.precision}. "
                           f"Valeurs valides: {valid_precisions}")
        
        if self.precision == "int8" and self.quant_mode is None:
            self.quant_mode = "int8"
            logger.warning("Mode de quantification automatiquement défini à 'int8'")

        if self.quant_mode and self.precision not in {"int8", "int4"}:
            raise ValueError(f"quant_mode spécifié avec precision={self.precision}. "
                           "quant_mode nécessite precision='int8' ou 'int4'")

    def build(self) -> Path:
        """
        Construction complète de l'engine TensorRT-LLM.
        
        Returns
        -------
        Path
            Chemin vers l'engine compilé.
        """
        logger.info("=== Début de compilation engine TensorRT-LLM ===")
        
        try:
            # Préparation des répertoires
            self._prepare_directories()
            
            # Étape 1: Conversion en checkpoint TensorRT-LLM
            ckpt_dir = self._convert_checkpoint()
            
            # Étape 2: Compilation de l'engine
            engine_path = self._build_engine(ckpt_dir)
            
            # Nettoyage
            self._cleanup(ckpt_dir)
            
            logger.info("✅ Engine compilé avec succès: %s", engine_path)
            return engine_path
            
        except Exception as e:
            logger.error("❌ Échec de compilation: %s", e)
            raise

    def _prepare_directories(self) -> None:
        """Préparation des répertoires de travail."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        
        logger.debug("Répertoires préparés: output=%s, tmp=%s", 
                    self.output_dir, self.tmp_dir)

    def _convert_checkpoint(self) -> Path:
        """
        Conversion du modèle HuggingFace en checkpoint TensorRT-LLM.
        
        Returns
        -------
        Path
            Répertoire contenant le checkpoint converti.
        """
        ckpt_dir = self.tmp_dir / "trt_ckpt" / f"{self.model_id.replace('/', '_')}"
        ckpt_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("🔄 Conversion en checkpoint TensorRT-LLM...")
        
        # Commande de base
        cmd = [
            "python", "/opt/tensorrt_llm/examples/llama/convert_checkpoint.py",
            "--model_dir", str(self.model_id),
            "--output_dir", str(ckpt_dir),
            "--dtype", self.precision,
        ]
        
        # Options spécifiques à la quantification
        if self.quant_mode:
            cmd.extend(["--quant_mode", self.quant_mode])
            
        if self.calibration_path:
            cmd.extend(["--calibration_dataset", self.calibration_path])
            
        # Exécution avec logs détaillés
        self._run_command(cmd, "Conversion checkpoint")
        
        logger.info("✅ Checkpoint converti: %s", ckpt_dir)
        return ckpt_dir

    def _build_engine(self, ckpt_dir: Path) -> Path:
        """
        Compilation du checkpoint en engine TensorRT-LLM.
        
        Parameters
        ----------
        ckpt_dir : Path
            Répertoire du checkpoint à compiler.
            
        Returns
        -------
        Path
            Chemin vers l'engine compilé.
        """
        model_name = self.model_id.split("/")[-1]
        suffix = f"{self.precision}"
        if self.quant_mode:
            suffix = f"{self.quant_mode}"
        
        engine_name = f"{model_name}.{suffix}.engine"
        engine_path = self.output_dir / engine_name
        
        logger.info("🔧 Compilation de l'engine TensorRT-LLM...")
        
        # Commande de compilation
        cmd = [
            "trtllm-build",
            "--checkpoint_dir", str(ckpt_dir),
            "--output_dir", str(self.output_dir),
            "--max_batch_size", str(self.batch_size),
            "--max_input_len", str(self.max_input_len),
            "--max_output_len", str(self.max_output_len),
        ]
        
        # Options spécifiques à la précision
        if self.precision in {"fp16", "fp32"}:
            cmd.extend(["--dtype", self.precision])
        
        # Options INT8/quantification
        if self.quant_mode:
            cmd.extend(["--quant_mode", self.quant_mode])
            
        # Exécution avec logs détaillés
        self._run_command(cmd, "Compilation engine")
        
        # Vérification de la création
        if not engine_path.exists():
            # Tentative de détection automatique du fichier créé
            created_engines = list(self.output_dir.glob("*.engine"))
            if created_engines:
                actual_engine = created_engines[-1]  # Plus récent
                logger.warning("Engine créé avec nom différent: %s", actual_engine)
                return actual_engine
            else:
                raise FileNotFoundError(f"Engine non créé: {engine_path}")
        
        return engine_path

    def _run_command(self, cmd: List[str], step_name: str) -> None:
        """
        Exécution sécurisée d'une commande avec logs détaillés.
        
        Parameters
        ----------
        cmd : List[str]
            Commande à exécuter.
        step_name : str
            Nom de l'étape pour les logs.
        """
        logger.debug("Exécution: %s", " ".join(cmd))
        
        try:
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=3600,  # 1h timeout
            )
            
            # Log de la sortie en mode debug
            if result.stdout:
                logger.debug("%s - stdout:\n%s", step_name, result.stdout)
            if result.stderr:
                logger.debug("%s - stderr:\n%s", step_name, result.stderr)
                
        except subprocess.CalledProcessError as e:
            logger.error("%s - Échec (code %d)", step_name, e.returncode)
            if e.stdout:
                logger.error("stdout:\n%s", e.stdout)
            if e.stderr:
                logger.error("stderr:\n%s", e.stderr)
            raise RuntimeError(f"Échec de {step_name}: {e}") from e
            
        except subprocess.TimeoutExpired as e:
            logger.error("%s - Timeout après 1h", step_name)
            raise RuntimeError(f"Timeout de {step_name}") from e

    def _cleanup(self, ckpt_dir: Path) -> None:
        """Nettoyage des fichiers temporaires."""
        try:
            shutil.rmtree(ckpt_dir, ignore_errors=True)
            logger.debug("Nettoyage effectué: %s", ckpt_dir)
        except Exception as e:
            logger.warning("Erreur lors du nettoyage: %s", e)

    def get_engine_info(self) -> Dict[str, Any]:
        """
        Informations sur la configuration de l'engine.
        
        Returns
        -------
        Dict[str, Any]
            Métadonnées de configuration.
        """
        return {
            "model_id": self.model_id,
            "precision": self.precision,
            "quant_mode": self.quant_mode,
            "max_input_len": self.max_input_len,
            "max_output_len": self.max_output_len,
            "batch_size": self.batch_size,
            "output_dir": str(self.output_dir),
        }


# --------------------------------------------------------------------------- #
# API de compatibilité
# --------------------------------------------------------------------------- #


def convert_and_build(
    model_id: str, 
    precision: str = "fp16",
    quant_mode: Optional[str] = None,
    calibration_path: Optional[str] = None,
) -> Path:
    """
    API de compatibilité pour la fonction originale.
    
    Parameters
    ----------
    model_id : str
        ID du modèle HuggingFace.
    precision : str
        Précision de l'engine.
    quant_mode : str | None
        Mode de quantification pour INT8.
    calibration_path : str | None
        Chemin vers les données de calibration.
        
    Returns
    -------
    Path
        Chemin vers l'engine compilé.
    """
    builder = TensorRTEngineBuilder(
        model_id=model_id,
        precision=precision,
        quant_mode=quant_mode,
        calibration_path=calibration_path,
    )
    return builder.build()
