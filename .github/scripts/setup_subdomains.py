import os
import json
import requests
import glob

CF_API_TOKEN = os.environ['CF_API_TOKEN']
GH_TOKEN = os.environ['GH_TOKEN']
CF_HEADERS = {
    "Authorization": f"Bearer {CF_API_TOKEN}",
    "Content-Type": "application/json"
}
GH_HEADERS = {
    "Authorization": f"token {GH_TOKEN}",
    "Accept": "application/vnd.github.v3+json"
}

def get_zone_id(domain):
    response = requests.get(
        f"https://api.cloudflare.com/client/v4/zones?name={domain}",
        headers=CF_HEADERS
    )
    zones = response.json()['result']
    return zones[0]['id'] if zones else None

def setup_dns_record(zone_id, record_type, name, content):
    data = {
        "type": record_type,
        "name": name,
        "content": content,
        "proxied": True
    }
    response = requests.post(
        f"https://api.cloudflare.com/client/v4/zones/{zone_id}/dns_records",
        headers=CF_HEADERS,
        json=data
    )
    return response.json()

def setup_github_pages(repo, cname):
    response = requests.post(
        f"https://api.github.com/repos/{repo}/pages",
        headers=GH_HEADERS,
        json={"cname": cname}
    )
    return response.status_code == 201

def process_domain_config(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)

    domain = config['domain']
    zone_id = get_zone_id(domain)
    if not zone_id:
        print(f"Zone not found for domain: {domain}")
        return

    for subdomain in config['subdomains']:
        full_domain = f"{subdomain['name']}.{domain}"
        result = setup_dns_record(
            zone_id,
            "CNAME",
            full_domain,
            subdomain['github_pages_url']
        )
        print(f"Setting up CNAME for {full_domain}: {'Success' if result['success'] else 'Failed'}")

        if setup_github_pages(subdomain['repo'], full_domain):
            print(f"GitHub Pages configured for {subdomain['repo']} with CNAME {full_domain}")
        else:
            print(f"Failed to configure GitHub Pages for {subdomain['repo']}")

def main():
    config_files = glob.glob('domains/*.json')
    for config_file in config_files:
        print(f"Processing configuration: {config_file}")
        process_domain_config(config_file)

if __name__ == "__main__":
    main()
