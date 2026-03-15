from locust import HttpUser, task, between, tag
import random
import string
import json

class URLShortenerUser(HttpUser):
    """Пользователь для нагрузочного тестирования"""
    
    wait_time = between(1, 3)
    token = None
    short_codes = []
    
    def on_start(self):
        self.email = f"loadtest_{random.randint(1, 1000000)}@example.com"
        self.password = "password123"
        
        self.client.post("/api/register", json={
            "email": self.email,
            "password": self.password
        })
        
        response = self.client.post("/api/login", json={
            "email": self.email,
            "password": self.password
        })
        
        if response.status_code == 200:
            self.token = response.json()["access_token"]
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @tag(1)
    @task(3)
    def create_short_link(self):
        """Создание короткой ссылки"""
        url = f"https://example.com/{random.randint(1, 1000000)}"
        
        if random.random() < 0.3:
            custom_alias = ''.join(random.choices(string.ascii_lowercase, k=6))
            response = self.client.post("/api/links/shorten", json={
                "original_url": url,
                "custom_alias": custom_alias
            }, headers=self.headers if random.random() < 0.7 else {})
        else:
            response = self.client.post("/api/links/shorten", json={
                "original_url": url
            }, headers=self.headers if random.random() < 0.7 else {})
        
        if response.status_code == 201:
            short_code = response.json()["short_code"]
            self.short_codes.append(short_code)
    
    @tag(2)
    @task(10)
    def redirect_to_link(self):
        """Переход по короткой ссылке"""
        if not self.short_codes:
            return
        
        short_code = random.choice(self.short_codes)
        self.client.get(f"/api/{short_code}")
    
    @tag(3)
    @task(2)
    def get_link_stats(self):
        """Получение статистики по ссылке"""
        if not self.short_codes or not self.token:
            return
        
        short_code = random.choice(self.short_codes)
        self.client.get(
            f"/api/links/{short_code}/stats",
            headers=self.headers
        )
    
    @tag(4)
    @task(1)
    def search_links(self):
        """Поиск ссылок"""
        search_term = "example"
        self.client.get(
            "/api/links/search",
            params={"original_url": search_term},
            headers=self.headers if random.random() < 0.5 else {}
        )
    
    @tag(5)
    @task(1)
    def update_link(self):
        """Обновление ссылки"""
        if not self.short_codes or not self.token:
            return
        
        short_code = random.choice(self.short_codes)
        new_url = f"https://updated-{random.randint(1, 1000)}.com"
        
        self.client.put(
            f"/api/links/{short_code}",
            json={"original_url": new_url},
            headers=self.headers
        )
    
    @tag(6)
    @task(1)
    def delete_link(self):
        """Удаление ссылки"""
        if not self.short_codes or not self.token:
            return
        
        if len(self.short_codes) > 5:
            short_code = self.short_codes.pop(random.randint(0, len(self.short_codes) - 1))
            self.client.delete(
                f"/api/links/{short_code}",
                headers=self.headers
            )
    
    @tag(7)
    @task(1)
    def health_check(self):
        """Проверка здоровья"""
        self.client.get("/health")