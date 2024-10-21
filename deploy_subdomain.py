import os
import json
import requests

# Cloudflare API 정보를 담은 URL
CF_API_URL = "https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records"

# Cloudflare 환경변수에서 API 키와 이메일을 가져옴
CLOUDFLARE_EMAIL = os.getenv('CLOUDFLARE_EMAIL')  # Your Cloudflare account email
CLOUDFLARE_API_KEY = os.getenv('CLOUDFLARE_API_KEY')  # Your Global API Key

HEADERS = {
    'X-Auth-Email': CLOUDFLARE_EMAIL,
    'X-Auth-Key': CLOUDFLARE_API_KEY,
    'Content-Type': 'application/json'
}

def get_zone_id(domain_name):
    """ Cloudflare에서 도메인 zone ID를 가져오는 함수 """
    print(f"Fetching Zone ID for {domain_name}")
    print(f"Using email: {CLOUDFLARE_EMAIL[:4]}...")  # To verify it's being picked up
    
    response = requests.get(
        f'https://api.cloudflare.com/client/v4/zones?name={domain_name}',
        headers=HEADERS
    )
    print(f"Response Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    
    data = response.json()
    return data['result'][0]['id'] if data['success'] else None

def create_cname_record(zone_id, subdomain_name, cname_value, ttl, proxied):
    """ CNAME 레코드를 생성하는 함수 """
    data = {
        'type': 'CNAME',
        'name': subdomain_name,
        'content': cname_value,
        'ttl': ttl,
        'proxied': proxied
    }
    response = requests.post(CF_API_URL.format(zone_id=zone_id), headers=HEADERS, json=data)
    print(f"Creating CNAME for {subdomain_name}: {response.status_code}")
    print(f"Response Body: {response.text}")
    return response.json()

def apply_subdomains_from_folder(domain, folder_path):
    """ 폴더 내 모든 JSON 파일을 읽어 서브도메인 적용 """
    zone_id = get_zone_id(domain)
    if not zone_id:
        print(f"Zone ID for {domain} not found!")
        return
    
    # 폴더 내의 모든 json 파일에 대해 처리
    for json_file in os.listdir(folder_path):
        if json_file.endswith('.json'):
            json_file_path = os.path.join(folder_path, json_file)
            print(f"Processing file: {json_file_path}")
            with open(json_file_path, 'r') as file:
                subdomains = json.load(file)
                for subdomain in subdomains:
                    subdomain_name = subdomain['subdomain']
                    cname_value = subdomain['cname']
                    ttl = subdomain.get('ttl', 120)
                    proxied = subdomain.get('proxied', False)

                    response = create_cname_record(zone_id, subdomain_name, cname_value, ttl, proxied)
                    print(f"Created subdomain {subdomain_name}.{domain}: {response}")

if __name__ == "__main__":
    # moontree.me에 대한 설정을 포함한 폴더에서 서브도메인 적용
    apply_subdomains_from_folder("moontree.me", "me_subdomains_folder")
    
    # moonsparkle.tech에 대한 설정을 포함한 폴더에서 서브도메인 적용
    apply_subdomains_from_folder("moonsparkle.tech", "tech_subdomains_folder")
