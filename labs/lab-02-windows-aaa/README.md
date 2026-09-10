# Lab 2 – Windows AAA, Access Control and Encryption

## Overview

This lab focused on authentication, authorization and access control within a Windows domain environment.

The lab involved configuring and testing user accounts, groups, file shares, NTFS permissions and file encryption. Different user accounts were used to verify how Windows applies permissions and controls access to shared resources.

The exercises provided practical experience with managing access to resources in a Windows Server and Active Directory environment.

## Lab Environment

| System | Role |
|---|---|
| Windows Server | Active Directory, user/group and file resource administration |
| Windows 10 | Domain-joined client used for access testing |
| Active Directory | Centralised identity and access management |
| NTFS | File system permissions and access control |
| EFS | File encryption testing |

## Main Areas Covered

The lab included practical work involving:

- Active Directory users and groups.
- Authentication and authorization.
- Windows file sharing.
- Share permissions.
- NTFS permissions.
- User and group-based access control.
- Permission inheritance.
- Testing access using different domain accounts.
- Encrypting File System (EFS).
- Testing access to encrypted files.


## Implementation

### 1. Active Directory Users and Groups

Active Directory Users and Computers was used to manage identities within the `HP.local` domain.

A dedicated Organizational Unit (OU) named `TestAccounts` was used to organise accounts required for the lab exercises. The OU contained test user accounts and a security group that could be used when applying and testing access controls.

Using an OU provided a structured way to manage the accounts separately from the default Active Directory containers.

![Active Directory TestAccounts OU](screenshots/01-active-directory-testaccounts.png)

#### Security Group Configuration

A security group named `WindowsTest` was configured to group accounts that required access during the lab exercises.

The group contained domain user accounts as well as the Windows 10 computer account used in the lab environment.

Using a security group allows permissions to be assigned to the group rather than configuring access separately for every account. This makes access control easier to manage as users or computers can be added to or removed from the group when their access requirements change.

![WindowsTest security group members](screenshots/02-windowstest-group-members.png)

