from django.db import models
from django.contrib.auth.models import User
 
# Framework model (Keep only one definition)
class Framework(models.Model):
    FrameworkId = models.AutoField(primary_key=True)
    FrameworkName = models.CharField(max_length=255)
    Version = models.CharField(max_length=50)
    FrameworkDetails = models.TextField()
    Date = models.DateField()
    CreatedByName = models.CharField(max_length=255)
    CreatedByDate = models.DateField()
    AuthorisedByName = models.CharField(max_length=255)
    AuthorisedByDate = models.DateField()
    Category = models.CharField(max_length=50)
    DocURL = models.CharField(max_length=255)
    identifier = models.CharField(max_length=45)
    Authorized_Description = models.CharField(max_length=255)
    Authorized_Title = models.CharField(max_length=100)
 
    class Meta:
        db_table = 'frameworks'
       
 
# Policy model
class Policy(models.Model):
    PolicyId = models.AutoField(primary_key=True)
    FrameworkId = models.ForeignKey(
        'Framework',
        on_delete=models.CASCADE,
        db_column='FrameworkId'
    )
    PolicyName = models.CharField(max_length=255)
 
    class Meta:
        db_table = 'policies'
 
# Audit model
class Audit(models.Model):
    audit_id = models.AutoField(primary_key=True)
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignee', db_column='assignee')
    auditor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='auditor', db_column='auditor')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviewer', null=True, db_column='reviewer')
    FrameworkId = models.ForeignKey(
        'Framework',
        on_delete=models.CASCADE,
        db_column='FrameworkId'
    )
    PolicyId = models.ForeignKey(
        'Policy',
        on_delete=models.CASCADE,
        db_column='PolicyId'
    )
    duedate = models.DateField()
    frequency = models.IntegerField(null=True)
    audit_type = models.CharField(max_length=1)
 
    class Meta:
        db_table = 'audit'
 
 
# Compliance model
class Compliance(models.Model):
    SubPolicyId = models.IntegerField()
    ComplianceId = models.IntegerField(primary_key=True)
    ComplianceItemDescription = models.TextField()
    IsRisk = models.BooleanField()
    PossibleDamage = models.TextField()
    Criticality = models.CharField(max_length=50)
    MandatoryOptional = models.CharField(max_length=50)
    ManualAutomatic = models.CharField(max_length=50)
    Impact = models.CharField(max_length=50)
    Probability = models.CharField(max_length=50)
 
    class Meta:
        db_table = 'compliance'
 
 
# AuditFindings model
class AuditFindings(models.Model):
    audit_id = models.ForeignKey('Audit', on_delete=models.CASCADE, db_column='audit_id')
    ComplianceId = models.ForeignKey('Compliance', on_delete=models.CASCADE, db_column='ComplianceId')
    date = models.DateTimeField(primary_key=True)
    comment = models.TextField()
    UserId = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='UserId')
    check_status = models.CharField(
        max_length=1,
        choices=[('0', 'Unchecked'), ('1', 'Checked'), ('2', 'Reviewed')],
        db_column='check'
    )
 
    class Meta:
        db_table = 'audit_findings'
 
 
# Incident model
class Incident(models.Model):
    IncidentId = models.AutoField(primary_key=True)
    incidenttitle = models.CharField(max_length=255)
    description = models.TextField()
    audit_id = models.ForeignKey('Audit', on_delete=models.CASCADE, db_column='audit_id')
    ComplianceId = models.ForeignKey('Compliance', on_delete=models.CASCADE, db_column='ComplianceId')
    Date = models.DateField()
    Time = models.TimeField()
    UserId = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='UserId')
    Origin = models.CharField(max_length=50)
    Comments = models.TextField()
    risk_category = models.CharField(max_length=100)
    priority_level = models.CharField(max_length=20)
    attachments = models.TextField()
    mitigation = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
 
    class Meta:
        db_table = 'incidents'
 
 
# Last Checklist Item Verified model
class LastChecklistItemVerified(models.Model):
    FrameworkId = models.ForeignKey('Framework', on_delete=models.CASCADE)
    ComplianceId = models.ForeignKey('Compliance', on_delete=models.CASCADE)
    SubPolicyId = models.ForeignKey('SubPolicy', on_delete=models.CASCADE)
    PolicyId = models.ForeignKey('Policy', on_delete=models.CASCADE)
    Date = models.DateField()
    Time = models.TimeField()
    User = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='UserId')
    Complied = models.CharField(max_length=1)
    Comments = models.TextField()
 
    class Meta:
        db_table = 'lastchecklistitemverified'
 
 
# Risks model
class Risk(models.Model):
    RiskId = models.AutoField(primary_key=True)
    audit_id = models.ForeignKey('Audit', on_delete=models.CASCADE)
    ComplianceId = models.ForeignKey('Compliance', on_delete=models.CASCADE)
    Origin = models.CharField(max_length=50)
    Criticality = models.IntegerField()
    Date = models.DateField()
    Time = models.TimeField()
    UserId = models.ForeignKey('Users', on_delete=models.CASCADE, db_column='UserId')
    Category = models.TextField()
    IncidentId = models.ForeignKey('Incident', on_delete=models.CASCADE)
    appetite = models.TextField()
 
    class Meta:
        db_table = 'risks'
 
 
# SubPolicies model
class SubPolicy(models.Model):
    PolicyId = models.ForeignKey('Policy', on_delete=models.CASCADE)
    Version = models.CharField(max_length=50)
    SubPolicyId = models.IntegerField(primary_key=True)
    SubPolicyName = models.CharField(max_length=255)
    CreatedByName = models.CharField(max_length=255)
    CreatedByDate = models.DateField()
    AuthorisedByName = models.CharField(max_length=255)
    AuthorisedByDate = models.DateField()
    Applicability = models.CharField(max_length=45)
    identifier = models.CharField(max_length=45)
    description = models.TextField()
 
    class Meta:
        db_table = 'subpolicies'
 
 
# Users model (Django built-in User model is used)
class Users(models.Model):
    UserId = models.AutoField(primary_key=True)
    UserName = models.CharField(max_length=255)
    MobileNo = models.CharField(max_length=15)
    Email = models.CharField(max_length=255)
    Department = models.CharField(max_length=255)
    Designation = models.CharField(max_length=255)
    Password = models.CharField(max_length=255)
    CreatedAt = models.DateTimeField()
    UpdatedAt = models.DateTimeField()
    role = models.CharField(max_length=45)
    branch = models.CharField(max_length=45)
 
    class Meta:
        db_table = 'users'
 
# Workflow model
class Workflow(models.Model):
    finding_id = models.DateTimeField(null=True, blank=True)
    IncidentId = models.IntegerField(null=True, blank=True)
    assignee_id = models.IntegerField()
    reviewer_id = models.IntegerField()
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'workflow'
 