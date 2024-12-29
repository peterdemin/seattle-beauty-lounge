#!/usr/bin/env bash

set -e -o pipefail

gcloud compute instances create staging \
    --project=seattle-beauty-lounge \
    --zone=us-west1-a \
    --machine-type=e2-micro \
    --network-interface=network-tier=STANDARD,stack-type=IPV4_ONLY,subnet=default \
    --tags=http-server,https-server \
    --public-ptr \
    --public-ptr-domain=staging.seattle-beauty-lounge.com. \
    --metadata=ssh-keys=peterdemin:ssh-rsa\ \
AAAAB3NzaC1yc2EAAAADAQABAAABgQDYxOnUHnt2KZ8kdjYjO/xWflaFKxXXJLv6V8/TiXgow8L\+QdFmcEJ/NRdR6/LVLEwiJ5h9l26mY8XxlpVAIY43NqbhPUdBp6SoeX2tpHFQa4R1i7coO3bO1sjAVqeTmTby4iROtWZ89OEsqYnWyYco4py\+sn6X\+h8TDRIbrl2zYQI9IwK8O2UJTV9qT2Vy4s4fitLTeO6AI7935OsrLzXV\+iaGGmhoUfpZcHZ5I9puaaTOyxuJ3q4nA0PNiZ9Lw7\+TYOo73eXPA\+qRrsvEy6b6x3\+izyj4WX31YSklksw5CX\+jjc23d7muV8cHFaoO1GkueVYyve8ncqy0dGn9CiDQudVqUyhqkF49MvWO1Hjg9SeidaKGqalh0Pv8RJquTJ8aUXcVS9GwCmYu\+/JfBVcCGYKEpcwrLOt/iYa9iHCsImb/wlO08n3R\+HBIF4At0Jxgd4wWM8ZhSXoA2UjCBojZwcWLPuS\+S/zplFgi3stv\+mkfEf9WDQo1g5bueFJ\+gK8=\ peterdemin@Kates-MacBook-Air.local \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --service-account=698831896740-compute@developer.gserviceaccount.com \
    --scopes=https://www.googleapis.com/auth/devstorage.read_only,https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write,https://www.googleapis.com/auth/service.management.readonly,https://www.googleapis.com/auth/servicecontrol,https://www.googleapis.com/auth/trace.append \
    --create-disk=auto-delete=yes,boot=yes,device-name=staging,image=projects/ubuntu-os-cloud/global/images/ubuntu-2004-focal-v20241219,mode=rw,size=10,type=pd-balanced \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=goog-ec-src=vm_add-gcloud \
    --reservation-affinity=any
