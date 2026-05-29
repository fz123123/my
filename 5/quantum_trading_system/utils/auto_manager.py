import os
import shutil
import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
import zipfile

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import config, save_config, BASE_DIR, BACKUP_DIR


class AutoManager:
    def __init__(self):
        self.last_backup = None
        self._load_state()

    def _load_state(self):
        state_file = BASE_DIR / 'auto_state.json'
        if state_file.exists():
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    if 'last_backup' in state:
                        self.last_backup = datetime.fromisoformat(state['last_backup'])
            except:
                pass

    def _save_state(self):
        state_file = BASE_DIR / 'auto_state.json'
        state = {
            'last_backup': self.last_backup.isoformat() if self.last_backup else None
        }
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def auto_save(self, data, filename):
        if not config['auto_save']:
            return None

        save_dir = BACKUP_DIR / 'saves'
        save_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        save_path = save_dir / f"{filename}_{timestamp}.json"

        try:
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            return save_path
        except Exception as e:
            print(f"Auto save failed: {e}")
            return None

    def auto_backup(self, force=False):
        if not config['auto_backup'] and not force:
            return None

        now = datetime.now()

        if not force and self.last_backup:
            interval = timedelta(hours=config['backup_interval_hours'])
            if now - self.last_backup < interval:
                return None

        backup_name = f"backup_{now.strftime('%Y%m%d_%H%M%S')}"
        backup_path = BACKUP_DIR / backup_name

        try:
            backup_path.mkdir(exist_ok=True)

            data_dir = BASE_DIR / 'data'
            if data_dir.exists():
                shutil.copytree(data_dir, backup_path / 'data', dirs_exist_ok=True)

            config_file = BASE_DIR / 'system_config.json'
            if config_file.exists():
                shutil.copy2(config_file, backup_path)

            zip_path = BACKUP_DIR / f"{backup_name}.zip"
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                for root, dirs, files in os.walk(backup_path):
                    for file in files:
                        file_path = Path(root) / file
                        arcname = file_path.relative_to(backup_path)
                        zf.write(file_path, arcname)

            shutil.rmtree(backup_path)

            self.last_backup = now
            self._save_state()

            print(f"Auto backup completed: {zip_path}")
            return zip_path

        except Exception as e:
            print(f"Auto backup failed: {e}")
            return None

    def list_backups(self):
        backups = []
        for f in BACKUP_DIR.glob('backup_*.zip'):
            stat = f.stat()
            backups.append({
                'name': f.name,
                'path': f,
                'size': stat.st_size,
                'time': datetime.fromtimestamp(stat.st_mtime)
            })
        return sorted(backups, key=lambda x: x['time'], reverse=True)

    def restore_backup(self, backup_name):
        backup_path = BACKUP_DIR / backup_name
        if not backup_path.exists():
            return False

        try:
            restore_dir = BACKUP_DIR / 'restore_temp'
            if restore_dir.exists():
                shutil.rmtree(restore_dir)

            with zipfile.ZipFile(backup_path, 'r') as zf:
                zf.extractall(restore_dir)

            data_dir = restore_dir / 'data'
            target_data_dir = BASE_DIR / 'data'
            if data_dir.exists():
                if target_data_dir.exists():
                    shutil.rmtree(target_data_dir)
                shutil.copytree(data_dir, target_data_dir)

            config_file = restore_dir / 'system_config.json'
            if config_file.exists():
                shutil.copy2(config_file, BASE_DIR)

            shutil.rmtree(restore_dir)
            print(f"Restored from {backup_name} successfully")
            return True

        except Exception as e:
            print(f"Restore failed: {e}")
            return False

    def cleanup_old_backups(self, keep_count=10):
        backups = self.list_backups()
        if len(backups) > keep_count:
            for backup in backups[keep_count:]:
                try:
                    backup['path'].unlink()
                    print(f"Removed old backup: {backup['name']}")
                except:
                    pass

    def auto_cleanup(self):
        self.cleanup_old_backups()
