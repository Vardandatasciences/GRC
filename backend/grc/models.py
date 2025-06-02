from django.db import models

# Use Django's built-in User model instead of creating a custom one
# from django.contrib.auth.models import User

# Any additional models can be defined here
class GRCProfile(models.Model):
    # You can extend User with a OneToOneField if needed later
    pass

class Users(models.Model):
    UserId = models.AutoField(primary_key=True)
    UserName = models.CharField(max_length=255)
    Password = models.CharField(max_length=255)
    # Optional fields that were commented out
    # MobileNo = models.CharField(max_length=15, null=True, blank=True)
    # Email = models.CharField(max_length=255, null=True, blank=True)
    # Department = models.CharField(max_length=255, null=True, blank=True)
    # Designation = models.CharField(max_length=255, null=True, blank=True)
    # role = models.CharField(max_length=45, null=True, blank=True)
    # branch = models.CharField(max_length=45, null=True, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    UpdatedAt = models.DateTimeField(auto_now=True, null=True, blank=True)
 
    class Meta:
        db_table = 'users'
        
    def __str__(self):
        return self.UserName

class Framework(models.Model):
    FrameworkId = models.AutoField(primary_key=True)
    FrameworkName = models.CharField(max_length=255, null=False)
    CurrentVersion = models.FloatField(null=True, blank=True)
    FrameworkDescription = models.TextField(null=True, blank=True)
    EffectiveDate = models.DateField(null=False)
    CreatedByName = models.CharField(max_length=255, null=True, blank=True)
    CreatedByDate = models.DateField(null=True, blank=True)
    Category = models.CharField(max_length=100, null=True, blank=True)
    DocURL = models.CharField(max_length=255, null=True, blank=True)
    Identifier = models.CharField(max_length=45, null=True, blank=True)
    StartDate = models.DateField(null=True, blank=True)
    EndDate = models.DateField(null=True, blank=True)
    Status = models.CharField(max_length=45, null=True, blank=True)
    ActiveInactive = models.CharField(max_length=45, null=True, blank=True)
    Reviewer = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'frameworks'

    def __str__(self):
        return self.FrameworkName

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
    FrameworkId = models.ForeignKey(Framework, on_delete=models.CASCADE, db_column='FrameworkId', related_name='policies')
    CurrentVersion = models.FloatField(null=False)
    Status = models.CharField(max_length=50, null=True, blank=True)
    PolicyDescription = models.TextField(null=True, blank=True)
    PolicyName = models.CharField(max_length=255, null=False)
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
    Reviewer = models.CharField(max_length=255, null=True, blank=True)
    CoverageRate = models.FloatField(null=True, blank=True)
    AcknowledgementCount = models.IntegerField(default=0, null=True, blank=True)
    AcknowledgedUserIds = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = 'policies'

    def __str__(self):
        return self.PolicyName
    
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
 
    def __str__(self):
        return f"Policy Version {self.Version} - {self.PolicyName}"
    
class SubPolicy(models.Model):
    SubPolicyId = models.AutoField(primary_key=True)
    Policy = models.ForeignKey(Policy, on_delete=models.CASCADE, db_column='PolicyId', related_name='subpolicies')
    SubPolicyName = models.CharField(max_length=255, null=False)
    CreatedByName = models.CharField(max_length=255, null=True, blank=True)
    CreatedByDate = models.DateField(null=True, blank=True)
    Identifier = models.CharField(max_length=45, null=True, blank=True)
    Description = models.TextField(null=True, blank=True)
    Status = models.CharField(max_length=50, null=True, blank=True)
    PermanentTemporary = models.CharField(max_length=50, null=True, blank=True)
    Control = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'subpolicies'

    def __str__(self):
        return self.SubPolicyName
    
class Compliance(models.Model):
    ComplianceId = models.AutoField(primary_key=True)
    SubPolicy = models.ForeignKey(SubPolicy, on_delete=models.CASCADE, db_column='SubPolicyId', related_name='compliances')
    ComplianceItemDescription = models.TextField(null=True, blank=True)
    IsRisk = models.BooleanField(null=True, blank=True)
    PossibleDamage = models.TextField(null=True, blank=True)
    mitigation = models.TextField(null=True, blank=True)
    Criticality = models.CharField(max_length=50, null=True, blank=True)
    MandatoryOptional = models.CharField(max_length=50, null=True, blank=True)
    ManualAutomatic = models.CharField(max_length=50, null=True, blank=True)
    Impact = models.CharField(max_length=50, null=True, blank=True)
    Probability = models.CharField(max_length=50, null=True, blank=True)
    MaturityLevel = models.CharField(max_length=50, choices=[
        ('Initial', 'Initial'),
        ('Developing', 'Developing'),
        ('Defined', 'Defined'),
        ('Managed', 'Managed'),
        ('Optimizing', 'Optimizing')
    ], default='Initial', null=True, blank=True)
    ActiveInactive = models.CharField(max_length=45, default='Inactive', null=True, blank=True)
    PermanentTemporary = models.CharField(max_length=45, null=True, blank=True)
    CreatedByName = models.CharField(max_length=250, null=True, blank=True)
    CreatedByDate = models.DateField(null=True, blank=True)
    ComplianceVersion = models.CharField(max_length=50, null=False)
    Status = models.CharField(max_length=50, default='Under Review', null=True, blank=True)
    Identifier = models.CharField(max_length=45, null=True, blank=True)
    PreviousComplianceVersionId = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_versions',
        db_column='PreviousComplianceVersionId'
    )
    
    class Meta:
        db_table = 'compliance'

    def __str__(self):
        return f"Compliance {self.ComplianceId} - Version {self.ComplianceVersion}"
    



class PolicyApproval(models.Model):
    ApprovalId = models.AutoField(primary_key=True)
    Identifier = models.CharField(max_length=45, db_column='Identifier')
    ExtractedData = models.JSONField(null=True, blank=True)
    UserId = models.IntegerField()
    ReviewerId = models.IntegerField()
    Version = models.CharField(max_length=50, null=True, blank=True)
    ApprovedNot = models.BooleanField(null=True)
    ApprovedDate = models.DateTimeField(null=True, blank=True)
 
    def __str__(self):
        return f"PolicyApproval {self.Identifier} (Version {self.Version})"
 
    class Meta:
        db_table = 'policyapproval'

class LastChecklistItemVerified(models.Model):
    Comments = models.TextField(null=True, blank=True)
    Count = models.IntegerField()
    
    class Meta:
        db_table = 'lastchecklistitemverified'
        managed = False  # This tells Django not to manage this table's schema

class RiskInstance(models.Model):
    MITIGATION_PENDING = 'Pending'
    MITIGATION_IN_PROGRESS = 'In Progress'
    MITIGATION_COMPLETED = 'Completed'
    
    MITIGATION_STATUS_CHOICES = [
        (MITIGATION_PENDING, 'Pending'),
        (MITIGATION_IN_PROGRESS, 'In Progress'),
        (MITIGATION_COMPLETED, 'Completed'),
    ]
    
    RiskInstanceId = models.AutoField(primary_key=True)
    ComplianceId = models.ForeignKey('Compliance', on_delete=models.CASCADE, related_name='risk_instances', null=True)
    MitigationStatus = models.CharField(max_length=20, choices=MITIGATION_STATUS_CHOICES, default=MITIGATION_PENDING)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    LastUpdated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'risk_instance'

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

class ExportTask(models.Model):
    id = models.AutoField(primary_key=True)
    export_data = models.JSONField(null=True, blank=True)
    file_type = models.CharField(max_length=10)
    user_id = models.CharField(max_length=100)
    s3_url = models.CharField(max_length=255, null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    error = models.TextField(null=True, blank=True)
    metadata = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'exported_files'
