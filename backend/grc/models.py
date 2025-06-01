from django.db import models
 
class Framework(models.Model):
    FrameworkId = models.AutoField(primary_key=True)
    FrameworkName = models.CharField(max_length=255)
    CurrentVersion = models.FloatField(default=1.0)
    FrameworkDescription = models.TextField()
    EffectiveDate = models.DateField()
    CreatedByName = models.CharField(max_length=255)
    CreatedByDate = models.DateField()
    Category = models.CharField(max_length=100, null=True, blank=True)
    DocURL = models.CharField(max_length=255, null=True, blank=True)
    Identifier = models.CharField(max_length=45, null=True, blank=True)
    StartDate = models.DateField(null=True, blank=True)
    EndDate = models.DateField(null=True, blank=True)
    Status = models.CharField(max_length=45, null=True, blank=True)
    ActiveInactive = models.CharField(max_length=45, null=True, blank=True)
    Reviewer = models.CharField(max_length=255)
 
    class Meta:
        db_table = 'frameworks'
 
class FrameworkVersion(models.Model):
    VersionId = models.AutoField(primary_key=True)
    FrameworkId = models.ForeignKey('Framework', on_delete=models.CASCADE, db_column='FrameworkId')
    Version = models.FloatField()
    FrameworkName = models.CharField(max_length=255)
    CreatedBy = models.CharField(max_length=255)
    CreatedDate = models.DateField()
    PreviousVersionId = models.IntegerField(null=True, blank=True)
 
    class Meta:
        db_table = 'frameworkversions'
 
 
class Policy(models.Model):
    PolicyId = models.AutoField(primary_key=True)
    FrameworkId = models.ForeignKey('Framework', on_delete=models.CASCADE, db_column='FrameworkId')
    CurrentVersion = models.CharField(max_length=20, default='1.0')
    Status = models.CharField(max_length=50)
    PolicyDescription = models.TextField()
    PolicyName = models.CharField(max_length=255)
    StartDate = models.DateField()
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
    Reviewer=models.CharField(max_length=255, null=True, blank=True)
    CoverageRate = models.FloatField(null=True, blank=True)
    AcknowledgedUserIds = models.JSONField(default=list, blank=True, null=True)  # Allow null and use empty list as default
    AcknowledgementCount = models.IntegerField(default=0)
 
 
    class Meta:
        db_table = 'policies'
 
 
class PolicyVersion(models.Model):
    VersionId = models.AutoField(primary_key=True)
    PolicyId = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='PolicyId')
    Version = models.CharField(max_length=20)
    PolicyName = models.CharField(max_length=255)
    CreatedBy = models.CharField(max_length=255)
    CreatedDate = models.DateField()
    PreviousVersionId = models.IntegerField(null=True, blank=True)
 
    class Meta:
        db_table = 'policyversions'
 
 
class SubPolicy(models.Model):
    SubPolicyId = models.AutoField(primary_key=True)
    PolicyId = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='PolicyId')
    SubPolicyName = models.CharField(max_length=255)
    CreatedByName = models.CharField(max_length=255)
    CreatedByDate = models.DateField()
    Identifier = models.CharField(max_length=45)
    Description = models.TextField()
    Status = models.CharField(max_length=50, null=True, blank=True)
    PermanentTemporary = models.CharField(max_length=50, null=True, blank=True)
    Control = models.TextField(null=True, blank=True)
 
    class Meta:
        db_table = 'subpolicies'
 
 
class PolicyApproval(models.Model):
    ApprovalId = models.AutoField(primary_key=True)
    PolicyId = models.ForeignKey('Policy', on_delete=models.CASCADE, db_column='PolicyId', null=True)
    # Identifier = models.CharField(max_length=45)
    ExtractedData = models.JSONField(null=True, blank=True)
    UserId = models.IntegerField()
    ReviewerId = models.IntegerField()
    Version = models.CharField(max_length=50, null=True, blank=True)
    ApprovedNot = models.BooleanField(null=True)
    ApprovedDate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"PolicyApproval {self.Policy_id} (Version {self.Version})"
 
    class Meta:
        db_table = 'policyapproval'


class FrameworkApproval(models.Model):
    ApprovalId = models.AutoField(primary_key=True)
    FrameworkId = models.ForeignKey('Framework', on_delete=models.CASCADE, db_column='FrameworkId', null=True)
    # Identifier field is optional, uncomment if needed
    # Identifier = models.CharField(max_length=45, null=True, blank=True)
    ExtractedData = models.JSONField(null=True, blank=True)
    UserId = models.IntegerField()
    ReviewerId = models.IntegerField(null=True, blank=True)
    Version = models.CharField(max_length=50, null=True, blank=True)
    ApprovedNot = models.BooleanField(null=True)
    ApprovedDate = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"FrameworkApproval {self.FrameworkId_id} (Version {self.Version})"

    class Meta:
        db_table = 'frameworkapproval'

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

class Compliance(models.Model):
    ComplianceId = models.AutoField(primary_key=True)
    SubPolicyId = models.ForeignKey('SubPolicy', on_delete=models.CASCADE, db_column='SubPolicyId')
    Identifier = models.CharField(max_length=50, null=True, blank=True)
    ComplianceItemDescription = models.TextField()
    mitigation = models.TextField(null=True, blank=True)
    IsRisk = models.BooleanField()
    PossibleDamage = models.TextField()
    Criticality = models.CharField(max_length=50)
    MandatoryOptional = models.CharField(max_length=50)
    ManualAutomatic = models.CharField(max_length=50)
    Impact = models.CharField(max_length=50)
    Probability = models.CharField(max_length=50)
    ActiveInactive = models.CharField(max_length=45, null=True, blank=True)
    PermanentTemporary = models.CharField(max_length=45)
    CreatedByName = models.CharField(max_length=250)
    CreatedByDate = models.DateField()
    ComplianceVersion = models.CharField(max_length=50)
    Status = models.CharField(max_length=50, null=True, blank=True)
 
    class Meta:
        db_table = 'compliance'
        # Since Django does not support composite primary keys, you can add a unique constraint to enforce uniqueness:
        unique_together = (('SubPolicyId', 'ComplianceVersion'),)
 
    def __str__(self):
        return f"Compliance {self.ComplianceId} - Version {self.ComplianceVersion}"

class Incident(models.Model):
    IncidentId = models.AutoField(primary_key=True)
    IncidentTitle = models.CharField(max_length=255)
    Description = models.TextField()
    Mitigation = models.TextField(null=True, blank=True)
    AuditId = models.ForeignKey('Audit', on_delete=models.CASCADE, null=True, blank=True, db_column='AuditId')
    ComplianceId = models.ForeignKey('Compliance', on_delete=models.CASCADE, null=True, blank=True, db_column='ComplianceId')
    Date = models.DateField()
    Time = models.TimeField()
    UserId = models.ForeignKey(Users, on_delete=models.CASCADE, null=True, blank=True, db_column='UserId')
    Origin = models.CharField(max_length=50)
    Comments = models.TextField(null=True, blank=True)
    RiskCategory = models.CharField(max_length=100, null=True, blank=True)
    RiskPriority = models.CharField(max_length=20, null=True, blank=True)
    Attachments = models.TextField(null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    Status = models.CharField(max_length=45, null=True, blank=True)
    IdentifiedAt = models.DateTimeField(null=True, blank=True)
    RepeatedNot = models.BooleanField(null=True, blank=True)
    CostOfIncident= models.CharField(max_length=45, null=True, blank=True)
    ReopenedNot = models.BooleanField(null=True, blank=True)
    
 
    class Meta:
        db_table = 'incidents'

class Risk(models.Model):
    RiskId = models.AutoField(primary_key=True)  # Primary Key
    ComplianceId = models.IntegerField(null=True)
    Criticality = models.CharField(max_length=100, null=False)
    PossibleDamage = models.TextField(null=False)
    Category = models.CharField(max_length=100, null=False)
    RiskDescription = models.TextField(null=False)
    RiskLikelihood = models.IntegerField(null=False)
    RiskImpact = models.IntegerField(null=False)
    RiskExposureRating = models.DecimalField(max_digits=4, decimal_places=2, null=False)
    RiskPriority = models.CharField(max_length=50, null=False)
    RiskMitigation = models.TextField(null=True)

    class Meta:
        db_table = 'risk'  # Ensure Django uses the correct table in the database

    def __str__(self):
        return f"Risk {self.RiskId}"

class RiskInstance(models.Model):
    RiskInstanceId = models.AutoField(primary_key=True)
    RiskId = models.IntegerField(null=True)
    IncidentId = models.ForeignKey(
        Incident,
        on_delete=models.CASCADE,
        db_column='IncidentId'  # THIS tells Django the actual DB column name
    )
    Criticality = models.CharField(max_length=100, null=True)
    PossibleDamage = models.TextField(null=True)
    Category = models.CharField(max_length=100, null=True)
    Appetite = models.CharField(max_length=100, null=True)
    RiskDescription = models.TextField(null=True)
    RiskLikelihood = models.CharField(max_length=50, null=True)
    RiskImpact = models.CharField(max_length=50, null=True)
    RiskExposureRating = models.CharField(max_length=50, null=True)
    RiskPriority = models.CharField(max_length=50, null=True)
    RiskResponseType = models.CharField(max_length=100, null=True)
    RiskResponseDescription = models.TextField(null=True)
    RiskMitigation = models.JSONField(null=True, blank=True)
    RiskOwner = models.CharField(max_length=255, null=True)
    RiskStatus = models.CharField(max_length=50, null=True)
    UserId = models.IntegerField(null=True)
    Date = models.DateTimeField(null=True)
    MitigationDuedate = models.DateTimeField(null=True) 
    ModifiedMitigations = models.JSONField(null=True, blank=True)
    MitigationStatus = models.CharField(max_length=50, null=True)
    FirstResponseAt = models.DateTimeField(null=True)
    MitigationCompletedDate = models.DateTimeField(null=True)
    ReviewerCount = models.IntegerField(null=True)
    RiskFormDetails = models.JSONField(null=True, blank=True)
    RecurrenceCount = models.IntegerField(null=True)

    class Meta:
        db_table = 'risk_instance'  # Ensure Django uses the correct table name in the database

    def __str__(self):
        return f"Risk Instance {self.RiskInstanceId}"

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
    ReviewerComments = models.CharField(max_length=255, null=True)
    AuditType = models.CharField(max_length=1)
 
    class Meta:
        db_table = 'audit'
   
class AuditFinding(models.Model):
    AuditFindingsId = models.AutoField(primary_key=True)
    AuditId = models.ForeignKey(Audit, on_delete=models.CASCADE, db_column='AuditId')
    ComplianceId = models.ForeignKey('Compliance', on_delete=models.CASCADE, db_column='ComplianceId')
    UserId = models.ForeignKey(Users, on_delete=models.CASCADE, db_column='UserId')
    Evidence = models.TextField()
    Check = models.CharField(max_length=1, choices=[('0', 'Not Compliance'), ('1', 'Compliance'), ('2', 'Partially Compliance'), ('3', 'Not Applicable')], default='0')
    HowToVerify = models.TextField(null=True, blank=True)
    Impact = models.TextField(null=True, blank=True)
    Recommendation = models.TextField(null=True, blank=True)
    DetailsOfFinding = models.TextField(null=True, blank=True)
    Comments = models.TextField(null=True, blank=True)
    CheckedDate = models.DateTimeField(null=True, blank=True)
    AssignedDate = models.DateTimeField()
 
    class Meta:
        db_table = 'audit_findings'
 