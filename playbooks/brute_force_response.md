# Playbook: Brute Force Attack Response
## Automated Response to Brute Force Attempts

### Trigger Conditions
- Threat Type: Brute Force Attack
- Severity: High (3)
- Detection: Multiple failed login attempts (>5 in 5 minutes)

### Automated Actions (Executed in Sequence)

#### 1. Account Protection (Immediate)
- **Disable Account**: Lock compromised account
- **Reset Password**: Force password change
- **Revoke Sessions**: Terminate active sessions

```yaml
Action: disable_account
Target: Compromised User Account
Timeline: Immediate (0-1 second)
Result: Account locked, all sessions terminated
```

#### 2. Source Blocking (Immediate)
- **Block IP Address**: Add to firewall blacklist
- **Geo-block**: If anomalous location
- **Rate Limiting**: Increase for source IP

```yaml
Action: block_ip
Target: Attack Source IP
Timeline: 1-2 seconds
Result: IP blocked at firewall
```

#### 3. Investigation (Within 10 seconds)
- **Audit Log Review**: Check for successful logins
- **Session Analysis**: Review active sessions
- **Credential Check**: Verify account security

```yaml
Action: collect_logs
Target: Authentication logs
Timeline: 5-10 seconds
Result: Complete audit trail collected
```

#### 4. Notification & Documentation (Within 1 minute)
- **Alert Security Team**: Immediate notification
- **Create Case**: Brute force incident case
- **Document**: All actions and findings

```yaml
Action: alert_security_team
Channels: Slack, Email
Timeline: <1 minute
Recipients: SOC Team, Account Owner Manager
```

#### 5. Monitoring (Ongoing)
- **Enhanced Monitoring**: Watch for related attempts
- **Credential Exposure**: Check if passwords compromised
- **Lateral Movement**: Check for privilege escalation

### Response Timeline
```
T+0s   : Brute force attack detected
T+0-1s : Account disabled
T+1-2s : IP blocked
T+5-10s: Logs collected
T+10-60s: Security team alerted
T+1m   : Case created
```

### Success Criteria
✓ Account locked within 1 second
✓ Attack source blocked
✓ No successful compromise
✓ SOC team alerted
✓ Account owner notified
✓ Root cause identified

### Additional Verification
- [ ] Check if password was compromised
- [ ] Review other accounts from same IP
- [ ] Check for data access during attacks
- [ ] Verify MFA implementation

### Escalation
- Escalate if:
  - Successful login detected
  - Multiple accounts targeted
  - Privileged account targeted
  - Attack continues after blocking

### Post-Incident Actions
1. User password reset assistance
2. MFA enablement verification
3. Training reminder sent
4. Pattern analysis for trend identification
