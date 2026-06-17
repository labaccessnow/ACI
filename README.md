# Cisco ACI & Data-Center Fabric

Spine-leaf fabric design and automation — describing application intent (who talks to whom, on
what ports) instead of hand-plumbing VLANs and ACLs across a stack of switches.

## What it looks like in practice

Build the fabric from code, not the GUI. Tenant → application profile → EPG with `cisco.aci`,
using a YAML anchor so the APIC connection isn't repeated on every task:

```yaml
- name: Build a tenant, app profile, and EPG on APIC
  hosts: apic
  gather_facts: false
  vars:
    aci: &aci
      host: "{{ apic_host }}"
      username: "{{ apic_user }}"
      password: "{{ apic_password }}"
      validate_certs: false
  tasks:
    - cisco.aci.aci_tenant:   { <<: *aci, tenant: PROD, description: "Production", state: present }
    - cisco.aci.aci_ap:       { <<: *aci, tenant: PROD, ap: web-app, state: present }
    - cisco.aci.aci_epg:
        <<: *aci
        tenant: PROD
        ap: web-app
        epg: web
        bd: web-bd
        preferred_group: false     # keep it OUT of the permit-any group
        state: present
```

## Best practices I follow
- **Start network-centric, migrate to app-centric.** Don't try to model every contract on
  day one. Get traffic flowing in a network-centric design, then tighten into EPG/ESG
  segmentation as you actually learn the flows.
- **Automate via the API.** The APIC GUI is for reading and troubleshooting. Anything you'd
  do more than twice goes through `cisco.aci` / the REST API, in version control.
- **Naming discipline up front.** Tenants, BDs, EPGs, contracts, filters — a convention on
  day zero, or you drown in `EPG_new_FINAL_v2`.

## Lessons learned
- **Preferred groups quietly become permit-any.** They're convenient and then they're a flat
  network with extra steps. I keep new EPGs out of the preferred group and write explicit
  contracts, even when it's more typing.
- **Contract sprawl is the real maintenance cost**, not the initial build. Reusable filters and
  scoped contracts pay off the first time you have to audit "what can reach the database EPG."
- **Operate from Nexus Dashboard, not box-by-box CLI** — assurance and change impact before you
  click apply on a fabric.

## Where it's going (dated)
- **Dec 2023 → 2024:** Cisco acquires **Isovalent** (eBPF/Cilium), extending intent into
  cloud-native/container networking.
- **2024–2025:** consolidation under **Nexus Dashboard** and the **"Nexus One"** model — one
  policy/management plane across **both ACI and NX-OS VXLAN EVPN** (Group Policy Objects +
  Border Gateways) as the industry standardizes on open VXLAN/EVPN.
- **Late 2025 → 2026:** ACI 6.1.x / 6.2 and Nexus Dashboard 4.x carry that convergence forward.

I stay fluent in both the ACI policy model and the VXLAN-EVPN direction it's converging toward,
so a fabric I design today doesn't get stranded on the wrong side of that shift.
