"""
База данных семьи
"""

import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class FamilyDB:
    """Класс базы данных семьи"""
    
    def __init__(self, data_dir: str = "data/discord_family_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Файлы базы данных
        self.files = {
            'applications': self.data_dir / 'applications.json',
            'members': self.data_dir / 'members.json',
            'warnings': self.data_dir / 'warnings.json',
            'events': self.data_dir / 'events.json',
            'ranks': self.data_dir / 'ranks.json'
        }
        
        # Загружаем данные
        self.data = {}
        for key, filepath in self.files.items():
            self.data[key] = self._load_file(filepath)
    
    def _load_file(self, filepath: Path) -> Dict:
        """Загрузка файла JSON"""
        if not filepath.exists():
            return {}
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_file(self, key: str) -> bool:
        """Сохранение файла JSON"""
        try:
            with open(self.files[key], 'w', encoding='utf-8') as f:
                json.dump(self.data[key], f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    # Методы для членов
    def get_member(self, user_id: str) -> Optional[Dict]:
        """Получение члена семьи"""
        return self.data['members'].get(str(user_id))
    
    def add_member(self, user_id: str, data: Dict) -> bool:
        """Добавление члена семьи"""
        user_id = str(user_id)
        
        member_data = {
            'user_id': user_id,
            'username': data.get('username', ''),
            'game_name': data.get('game_name', ''),
            'rank': data.get('rank', 'Новичок'),
            'join_date': datetime.now().isoformat(),
            'level': data.get('level', 0),
            'age': data.get('age', 0)
        }
        
        self.data['members'][user_id] = member_data
        return self._save_file('members')
    
    def get_all_members(self) -> Dict:
        """Получение всех членов"""
        return self.data['members']
    
    # Методы для заявок
    def add_application(self, user_id: str, data: Dict) -> bool:
        """Добавление заявки"""
        user_id = str(user_id)
        
        application_data = {
            'user_id': user_id,
            'username': data.get('username', ''),
            'full_name': data.get('full_name', ''),
            'age': data.get('age', 0),
            'level': data.get('level', 0),
            'game_name': data.get('game_name', ''),
            'experience': data.get('experience', ''),
            'reason': data.get('reason', ''),
            'status': 'pending',
            'date': datetime.now().isoformat()
        }
        
        self.data['applications'][user_id] = application_data
        return self._save_file('applications')
    
    def get_pending_applications(self) -> List[Dict]:
        """Получение ожидающих заявок"""
        return [
            app for app in self.data['applications'].values()
            if app.get('status') == 'pending'
        ]
    
    # Методы для предупреждений
    def add_warning(self, user_id: str, admin_id: str, reason: str) -> bool:
        """Добавление предупреждения"""
        user_id = str(user_id)
        
        if user_id not in self.data['warnings']:
            self.data['warnings'][user_id] = []
        
        warning_data = {
            'reason': reason,
            'admin_id': admin_id,
            'date': datetime.now().isoformat()
        }
        
        self.data['warnings'][user_id].append(warning_data)
        return self._save_file('warnings')
    
    # Статистика
    def get_stats(self) -> Dict:
        """Получение статистики"""
        pending_apps = len(self.get_pending_applications())
        total_warnings = sum(len(w) for w in self.data['warnings'].values())
        
        return {
            'total_members': len(self.data['members']),
            'pending_applications': pending_apps,
            'total_ranks': len(self.data['ranks']),
            'total_warnings': total_warnings,
            'total_events': len(self.data['events'])
        }