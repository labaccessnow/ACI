# Infrastructure-as-Code for ACI with the CiscoDevNet/aci provider:
# tenant -> VRF -> bridge domain -> application profile -> EPG, with the relations wired up.
# APIC credentials come from the APIC_USERNAME / APIC_PASSWORD / APIC_URL env vars.
terraform {
  required_providers {
    aci = {
      source  = "CiscoDevNet/aci"
      version = "~> 2.0"
    }
  }
}

variable "apic_url" {
  type = string
}

provider "aci" {
  url      = var.apic_url
  insecure = true # lab self-signed cert; user/pass from APIC_USERNAME / APIC_PASSWORD
}

resource "aci_tenant" "prod" {
  name        = "PROD"
  description = "Production tenant, managed by Terraform"
}

resource "aci_vrf" "vrf" {
  tenant_dn = aci_tenant.prod.id
  name      = "prod-vrf"
}

resource "aci_bridge_domain" "web_bd" {
  tenant_dn          = aci_tenant.prod.id
  name               = "web-bd"
  relation_fv_rs_ctx = aci_vrf.vrf.id # BD -> VRF
}

resource "aci_application_profile" "ap" {
  tenant_dn = aci_tenant.prod.id
  name      = "web-app"
}

resource "aci_application_epg" "web" {
  application_profile_dn = aci_application_profile.ap.id
  name                   = "web"
  relation_fv_rs_bd      = aci_bridge_domain.web_bd.id # EPG -> BD
}
