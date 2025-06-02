from django.db import models
from django.contrib.auth.models import User

# Users model (Django built-in User model is used)
class Users(models.Model):
    UserId = models.AutoField(primary_key=True)
    UserName = models.CharField(max_length=255)
    # MobileNo = models.CharField(max_length=15)
    # Email = models.CharField(max_length=255)
    # Department = models.CharField(max_length=255)
    # Designation = models.CharField(max_length=255)
    Password = models.CharField(max_length=255)
    CreatedAt = models.DateTimeField()
    UpdatedAt = models.DateTimeField()
    # role = models.CharField(max_length=45)
    # branch = models.CharField(max_length=45)

    class Meta:
        db_table = 'users'

# Framework model
class Framework(models.Model):
    FrameworkId = models.AutoField(primary_key=True)
    FrameworkName = models.CharField(max_length=255)
    CurrentVersion = models.FloatField()
    FrameworkDescription = models.TextField()
    EffectiveDate = models.DateField()
    CreatedByName = models.CharField(max_length=255)
    CreatedByDate = models.DateField()
    AuthorisedByName = models.CharField(max_length=255)
    AuthorisedByDate = models.DateField()
    Category = models.CharField(max_length=50)
    DocURL = models.CharField(max_length=255)
    Identifier = models.CharField(max_length=45)
    ActiveInactive = models.CharField(max_length=45)

    class Meta:
        db_table = 'frameworks'

class Policy(models.Model):
    PolicyId = models.AutoField(primary_key=True)
    FrameworkId = models.ForeignKey(
        'Framework',
        on_delete=models.CASCADE,
        db_column='FrameworkId'
    )
    CurrentVersion = models.CharField(max_length=50, null=True, blank=True)
    Status = models.CharField(max_length=50, null=True, blank=True)
    PolicyDescription = models.TextField(null=True, blank=True)
    PolicyName = models.CharField(max_length=255)
    StartDate = models.DateField(null=True, blank=True)
    EndDate = models.DateField(null=True, blank=True)
    Department = models.CharField(max_length=255, null=True, blank=True)
    CreatedByName = models.CharField(max_length=255, null=True, blank=True)
    CreatedByDate = models.DateField(null=True, blank=True)
    Applicability = models.CharField(max_length=255, null=True, blank=True)
    DocURL = models.CharField(max_length=255, null=True, blank=True)
    Scope = models.TextField(null=True, blank=True)
    Objective = models.TextField(null=True, blank=True)
    Identifier = models.CharField(max_length=45, null=True, blank=True)
    PermanentTemporary = models.CharField(max_length=45, null=True, blank=True)
    ActiveInactive = models.CharField(max_length=45, null=True, blank=True)

    class Meta:
        db_table = 'policies'


# SubPolicy model
class SubPolicy(models.Model):
    SubPolicyId = models.AutoField(primary_key=True)
    PolicyId = models.ForeignKey(Policy, on_delete=models.CASCADE, db_column='PolicyId')
    Version = models.CharField(max_length=50)
    SubPolicyName = models.CharField(max_length=255)
    CreatedByName = models.CharField(max_length=255)
    CreatedByDate = models.DateField()
    AuthorisedByName = models.CharField(max_length=255)
    AuthorisedByDate = models.DateField()
    Applicability = models.CharField(max_length=45)
    Identifier = models.CharField(max_length=45)
    Description = models.TextField()

    class Meta:
        db_table = 'subpolicies'

    def __str__(self):
        return f"SubPolicy(id={self.SubPolicyId}, name={self.SubPolicyName}, version={self.Version})"

# Compliance model
class Compliance(models.Model):
    ComplianceId = models.AutoField(primary_key=True)
    SubPolicyId = models.ForeignKey('SubPolicy', on_delete=models.CASCADE, db_column='SubPolicyId')
    ComplianceItemDescription = models.TextField()
    IsRisk = models.BooleanField()
    PossibleDamage = models.TextField()
    Criticality = models.CharField(max_length=50)
    MandatoryOptional = models.CharField(max_length=50)
    ManualAutomatic = models.CharField(max_length=50)
    Impact = models.CharField(max_length=50)
    Probability = models.CharField(max_length=50)
    ActiveInactive = models.CharField(max_length=45)
    PermanentTemporary = models.CharField(max_length=45)
    CreatedByName = models.CharField(max_length=250)
    CreatedByDate = models.DateField()
    AuthorizedByName = models.CharField(max_length=250)
    AuthorizedByDate = models.DateField()
    ComplianceVersion = models.CharField(max_length=50)

    class Meta:
        db_table = 'compliance'

# Audit model
class Audit(models.Model):
    AuditId = models.AutoField(primary_key=True)
    Assignee = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='assignee', db_column='assignee')
    Auditor = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='auditor', db_column='auditor')
    Reviewer = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='reviewer', null=True, db_column='reviewer')
    FrameworkId = models.ForeignKey('Framework', on_delete=models.CASCADE, db_column='FrameworkId')
    PolicyId = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='PolicyId', null=True)
    SubPolicyId = models.ForeignKey('SubPolicy', on_delete=models.CASCADE, db_column='SubPolicyId', null=True)
    DueDate = models.DateField()
    Frequency = models.IntegerField(null=True)
    Status = models.CharField(max_length=45)
    CompletionDate = models.DateTimeField(null=True)
    ReviewStatus = models.CharField(max_length=45, null=True)
    ReviewComments = models.CharField(max_length=255, null=True)
    ReviewStartDate = models.DateTimeField(null=True)
    ReviewDate = models.DateTimeField(null=True)
    AuditType = models.CharField(max_length=1)
    Evidence = models.TextField(null=True, blank=True)
    Comments = models.TextField(null=True, blank=True)
    AssignedDate = models.DateTimeField(null=True, db_column='AssignedDate')
    Reports = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'audit'

# AuditFinding model
class AuditFinding(models.Model):
    AuditFindingsId = models.AutoField(primary_key=True)
    AuditId = models.ForeignKey(Audit, on_delete=models.CASCADE, db_column='AuditId', related_name='findings')
    ComplianceId = models.ForeignKey(Compliance, on_delete=models.CASCADE, db_column='ComplianceId')
    UserId = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='UserId')
    Evidence = models.TextField()
    Check = models.CharField(max_length=1, choices=[
        ('0', 'Not Started'), 
        ('1', 'In Progress'), 
        ('2', 'Completed'),
        ('3', 'Not Applicable')
    ], default='0')
    MajorMinor = models.CharField(max_length=1, choices=[
        ('0', 'Minor'),
        ('1', 'Major'),
        ('2', 'Not Applicable')
    ], null=True, blank=True)
    HowToVerify = models.TextField(null=True, blank=True)
    Impact = models.TextField(null=True, blank=True)
    Recommendation = models.TextField(null=True, blank=True)
    DetailsOfFinding = models.TextField(null=True, blank=True)
    Comments = models.TextField(null=True, blank=True)
    CheckedDate = models.DateTimeField(null=True, blank=True)
    AssignedDate = models.DateTimeField()
    
    class Meta:
        db_table = 'audit_findings'
        
    def save(self, *args, **kwargs):
        """Override save to ensure AuditId consistency"""
        print(f"DEBUG: Saving AuditFinding {self.AuditFindingsId} with AuditId {self.AuditId.AuditId}")
        super().save(*args, **kwargs)

# Incident model
class Incident(models.Model):
    IncidentId = models.AutoField(primary_key=True)
    AuditId = models.ForeignKey(Audit, on_delete=models.CASCADE)
    ComplianceId = models.ForeignKey(Compliance, on_delete=models.CASCADE)
    Date = models.DateField()
    Time = models.TimeField()
    UserId = models.ForeignKey(Users, on_delete=models.CASCADE)
    Origin = models.CharField(max_length=50)
    Comments = models.TextField()

    class Meta:
        db_table = 'incidents'

class Risk(models.Model):
    RiskId = models.AutoField(primary_key=True)
    ComplianceId = models.ForeignKey(Compliance, on_delete=models.CASCADE)
    RiskCategory = models.CharField(max_length=100)
    RiskDescription = models.TextField()
    RiskLikelihood = models.FloatField()
    RiskImpact = models.FloatField()
    RiskExposureRating = models.FloatField()
    RiskPriority = models.CharField(max_length=100)
    RiskMitigation = models.TextField()
 
    class Meta:
        db_table = 'risk'
 
# RiskInstance model
class RiskInstance(models.Model):
    RiskInstanceId = models.AutoField(primary_key=True)
    RiskId = models.ForeignKey(Risk, on_delete=models.CASCADE)
    Criticality = models.IntegerField()
    PossibleDamage = models.TextField()
    Category = models.CharField(max_length=45)
    Appetite = models.TextField()
    RiskDescription = models.TextField()
    RiskLikelihood = models.FloatField()
    RiskImpact = models.FloatField()
    RiskExposureRating = models.FloatField()
    RiskPriority = models.CharField(max_length=100)
    RiskResponseType = models.CharField(max_length=100)
    RiskResponseDescription = models.TextField()
    RiskOwner = models.CharField(max_length=45)
    RiskStatus = models.CharField(max_length=45)
    UserId = models.ForeignKey(Users, on_delete=models.CASCADE)
    Date = models.DateTimeField()
 
    class Meta:
        db_table = 'risk_instance'

# Workflow model
class Workflow(models.Model):
    Id = models.AutoField(primary_key=True)
    FindingId = models.ForeignKey(AuditFinding, on_delete=models.CASCADE, db_column='finding_id')
    IncidentId = models.ForeignKey(Incident, on_delete=models.CASCADE, db_column='IncidentId')
    AssigneeId = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='assignee_id', related_name='workflow_assignee')
    ReviewerId = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='reviewer_id', related_name='workflow_reviewer')
    AssignedAt = models.DateTimeField()

    class Meta:
        db_table = 'workflow'

class AuditReport(models.Model):
    ReportId = models.AutoField(primary_key=True)
    AuditId = models.ForeignKey(Audit, on_delete=models.CASCADE, db_column='AuditId')
    Report = models.TextField()
    PolicyId = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='PolicyId', null=True)
    SubPolicyId = models.ForeignKey('SubPolicy', on_delete=models.CASCADE, db_column='SubPolicyId', null=True)
    FrameworkId = models.ForeignKey('Framework', on_delete=models.CASCADE, db_column='FrameworkId')

    class Meta:
        db_table = 'audit_report'
