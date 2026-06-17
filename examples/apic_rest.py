#!/usr/bin/env python3
"""Talk to the APIC REST API directly — login, push a tenant, log out.

The cisco.aci modules wrap exactly this. Going raw is useful when you want to see the object
model as it really is, or do something a module doesn't cover yet.

    export APIC_URL=https://apic.lab APIC_USER=admin APIC_PASS=...
    python3 apic_rest.py
"""
import os
import requests

requests.packages.urllib3.disable_warnings()  # lab APIC ships a self-signed cert


def main() -> None:
    base = os.environ["APIC_URL"].rstrip("/")
    s = requests.Session()
    s.verify = False

    # 1) login — the token comes back as the APIC-cookie session cookie
    s.post(
        f"{base}/api/aaaLogin.json",
        json={"aaaUser": {"attributes": {
            "name": os.environ["APIC_USER"],
            "pwd": os.environ["APIC_PASS"],
        }}},
        timeout=30,
    ).raise_for_status()

    # 2) create/update a tenant — the same fvTenant managed object the GUI creates
    s.post(
        f"{base}/api/mo/uni/tn-PROD.json",
        json={"fvTenant": {"attributes": {"name": "PROD", "status": "created,modified"}}},
        timeout=30,
    ).raise_for_status()
    print("tenant PROD created/updated")

    # 3) be a good citizen and drop the session
    s.post(
        f"{base}/api/aaaLogout.json",
        json={"aaaUser": {"attributes": {"name": os.environ["APIC_USER"]}}},
        timeout=30,
    )


if __name__ == "__main__":
    main()
