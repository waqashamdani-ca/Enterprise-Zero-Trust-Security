# Enterprise Zero Trust Security Architecture

## Overview

This enterprise-style cybersecurity lab is designed to show how an organization can give people access to the systems and data they need while protecting sensitive resources. It uses synthetic data in an isolated environment to demonstrate zero trust through identity and permission checks, and defense in depth through separate network, host and application controls.

## Objectives

- Separate lab networks and allow only required traffic between them.
- Give users and administrators only the permissions their roles require.
- Review security events and investigate denied access.
- Verify controls, automate a routine check and practice application recovery.

## Lab Environment

The design places three workload virtual machines on a Dell Precision 5820 running Proxmox VE. The OPNsense firewall runs on a separate physical HP desktop. A TP-Link TL-SG108E managed switch separates the lab networks, and a GL.iNet Beryl AX serves as the upstream router.

- **DC1** provides Active Directory on Windows Server.
- **WIN1** is a Windows workstation.
- **APP1** serves the application over HTTPS using Apache on Linux.

The three logical zones are **Management** for administration, **Corporate** for DC1 and WIN1, and **Restricted** for APP1.

## Security Capabilities

- Network segmentation, with OPNsense policy between zones and separate host firewalls.
- Active Directory access management and endpoint security for Windows and Linux.
- Trusted HTTPS certificates and separate application permissions based on user roles.
- Tailscale remote access limited to the HTTPS application.
- Security event monitoring, local automation and encrypted application backup and recovery.

## Documentation

- [Project Assignment](docs/assignments/PROJECT-ASSIGNMENT.md), [Architecture](docs/architecture/ARCHITECTURE.md) and [Lab Implementation Guide](docs/lab-guides/LAB-IMPLEMENTATION-GUIDE.md)
- [Security Requirements](docs/security/SECURITY-REQUIREMENTS.md), [Test Plan](docs/testing/TEST-PLAN.md) and [Acceptance Criteria](docs/testing/ACCEPTANCE-CRITERIA.md)

## Technologies

Proxmox VE, OPNsense, Windows Server, Active Directory, Windows, Linux, Apache HTTP Server, Microsoft Defender, Tailscale, PowerShell and Python.
