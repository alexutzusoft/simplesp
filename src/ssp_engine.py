import os
import re
import time
import json
from typing import List, Optional

DEFAULT_CONFIG = {
    "data_dir": "data",
    "supported_extensions": [".txt", ".py", ".json"],
    "reload_check_interval": 2,
    "ui": {
        "title": "SimpleSP / Sentence Prediction",
        "dark_mode": True
    }
}

class SSPEngine:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.config = self._load_config()
        self.data_dir = self.config.get("data_dir", "data")
        self.extensions = tuple(self.config.get("supported_extensions", [".txt", ".py", ".json"]))
        
        self.corpus: List[str] = []
        self.last_mtime = 0
        self.load_data()

    def _load_config(self) -> dict:
        if not os.path.exists(self.config_path):
            try:
                with open(self.config_path, "w", encoding="utf-8") as f:
                    json.dump(DEFAULT_CONFIG, f, indent=4)
                print(f"Created default configuration at {self.config_path}")
                return DEFAULT_CONFIG
            except Exception as e:
                print(f"Error creating default config: {e}")
                return DEFAULT_CONFIG

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading config: {e}. Using defaults.")
            return DEFAULT_CONFIG

    def _get_data_mtime(self) -> float:
        if not os.path.exists(self.data_dir):
            return 0
        
        mtimes = [os.path.getmtime(self.data_dir)]
        if os.path.exists(self.config_path):
            mtimes.append(os.path.getmtime(self.config_path))

        for filename in os.listdir(self.data_dir):
            if filename.endswith(self.extensions):
                file_path = os.path.join(self.data_dir, filename)
                mtimes.append(os.path.getmtime(file_path))
        return max(mtimes) if mtimes else 0

    def load_data(self):
        # Refresh config in case it changed
        self.config = self._load_config()
        self.data_dir = self.config.get("data_dir", "data")
        self.extensions = tuple(self.config.get("supported_extensions", [".txt", ".py", ".json"]))
        
        self.corpus = []
        if not os.path.exists(self.data_dir):
            return

        for filename in os.listdir(self.data_dir):
            if filename.endswith(self.extensions):
                file_path = os.path.join(self.data_dir, filename)
                try:
                    if filename.endswith(".json"):
                        self._load_json_file(file_path)
                    else:
                        self._load_text_file(file_path)
                except Exception as e:
                    print(f"Error loading {filename}: {e}")
        
        self.last_mtime = self._get_data_mtime()
        print(f"Loaded {len(self.corpus)} sentences into corpus.")

    def _load_text_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Clean up Wikipedia-style references [n]
            content = re.sub(r"\[\d+\]", "", content)
            # Refined sentence splitting: . ! ? followed by space or newline, but not mid-word
            sentences = re.split(r"(?<=[.!?])\s+", content)
            self.corpus.extend([s.strip() for s in sentences if len(s.strip()) > 2])

    def _load_json_file(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                self.corpus.extend([str(item).strip() for item in data if item])
            elif isinstance(data, dict):
                # If it's a dict, we take values that are likely sentences
                for key, value in data.items():
                    if isinstance(value, str):
                        self.corpus.append(value.strip())
                    elif isinstance(value, list):
                        self.corpus.extend([str(i).strip() for i in value if i])

    def refresh_if_needed(self):
        current_mtime = self._get_data_mtime()
        if current_mtime > self.last_mtime:
            print(f"Hot Reload: Changes detected. Refreshing corpus...")
            self.load_data()

    def predict(self, text: str, limit: int = 1) -> List[str]:
        self.refresh_if_needed()
        
        if not text:
            return []

        # Find multiple sentences in corpus that start with text or match template
        predictions = self._find_matches(text, limit)
        return predictions

    def _find_matches(self, fragment: str, limit: int = 1) -> List[str]:
        fragment_clean = fragment.strip()
        if not fragment_clean:
            return []

        matches = []
        seen = set()

        # 1. Template matching {P}
        if "{P}" in fragment_clean:
            # Escape except for {P}
            parts = fragment_clean.split("{P}")
            escaped_parts = [re.escape(p) for p in parts]
            regex_pattern = "(.*?)".join(escaped_parts)
            
            try:
                pattern = re.compile(f"^{regex_pattern}", re.IGNORECASE)
                for sentence in self.corpus:
                    if pattern.search(sentence):
                        if sentence not in seen:
                            matches.append(sentence)
                            seen.add(sentence)
                            if limit is not None and len(matches) >= limit:
                                return matches
            except Exception as e:
                print(f"Regex error: {e}")
        
        # 2. Prefix matching
        fragment_lower = fragment_clean.lower()
        for sentence in self.corpus:
            if sentence.lower().startswith(fragment_lower):
                if sentence not in seen:
                    matches.append(sentence)
                    seen.add(sentence)
                    if limit is not None and len(matches) >= limit:
                        return matches
                
        return matches
