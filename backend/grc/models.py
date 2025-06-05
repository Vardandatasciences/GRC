from django.db import models

# Use Django's built-in User model instead of creating a custom one
# from django.contrib.auth.models import User

# Any additional models can be defined here
class GRCProfile(models.Model):
    # You can extend User with a OneToOneField if needed later
    pass

class User(models.Model):
    UserId = models.AutoField(primary_key=True)
    UserName = models.CharField(max_length=255, null=False)
    Password = models.CharField(max_length=255, null=False)
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
    Framework = models.ForeignKey(Framework, on_delete=models.CASCADE, db_column='FrameworkId', related_name='policies')
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

# class LastChecklistItemVerified(models.Model):
#     Comments = models.TextField(null=True, blank=True)
#     Count = models.IntegerField()
    
#     class Meta:
#         db_table = 'lastchecklistitemverified'
#         managed = False  # This tells Django not to manage this table's schema

class LastChecklistItemVerified(models.Model):
    id = models.BigAutoField(primary_key=True)
    FrameworkId = models.IntegerField()
    ComplianceId = models.IntegerField()
    SubPolicyId = models.IntegerField()
    PolicyId = models.IntegerField()
    Date = models.DateField()
    Time = models.TimeField()
    User = models.IntegerField()
    Complied = models.CharField(max_length=1, choices=[('0', 'No'), ('1', 'Yes'), ('2', 'N/A')])
    Comments = models.TextField(blank=True, null=True)
    Count = models.IntegerField(default=0)
    AuditFindingsId = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'lastchecklistitemverified'
        verbose_name = 'Checklist Verification Record'
        verbose_name_plural = 'Checklist Verification Records'

    def __str__(self):
        return f"Checklist for Framework {self.FrameworkId}, Compliance {self.ComplianceId} by User {self.User}"
    
class AuditVersion(models.Model):
    # Define the fields
    AuditId = models.IntegerField()
    Version = models.CharField(max_length=45)  # Version as a string (e.g., '1.0', '1.1')
    ExtractedInfo = models.JSONField()  # JSON field to store audit-related details
    UserId = models.IntegerField()  # User ID of the person who initiated the audit
    ApproverId = models.IntegerField()  # User ID of the person who approved the audit
    ApprovedRejected = models.CharField(max_length=45)  # Status (Approved/Rejected)
    Date = models.DateTimeField()  # Date and time when the audit version was created
    ActiveInactive = models.CharField(max_length=1)  # Status (A = Active, I = Inactive)

    # Meta information for the model
    class Meta:
        db_table = 'audit_versions'  # The table name in the database

    def __str__(self):
        return f"Audit Version {self.Version} for Audit ID {self.AuditId}"
    
class AuditFindings(models.Model):
    # Define the fields
    AuditFindingsId = models.AutoField(primary_key=True)  # Auto-incremented primary key
    AuditId = models.IntegerField()
    ComplianceId = models.IntegerField()
    Evidence = models.TextField()  # Text field for evidence details
    UserId = models.IntegerField()  # User ID who reported or initiated the finding
    Check = models.CharField(max_length=45)  # Check status (e.g., 0, 1, 2)
    HowToVerify = models.TextField()  # Instructions on how to verify the finding
    Impact = models.TextField()  # Impact of the finding
    Recommendation = models.TextField()  # Recommendation for resolving the issue
    DetailsOfFinding = models.TextField()  # Detailed description of the finding
    Comments = models.TextField()  # Additional comments
    CheckedDate = models.DateTimeField()  # Date when the finding was checked
    AssignedDate = models.DateTimeField()  # Date when the finding was assigned
    MajorMinor = models.CharField(max_length=45)  # Severity (Major or Minor)
    ReviewRejected = models.BooleanField()  # Whether the finding was rejected during review
    ReviewComments = models.TextField()  # Reviewer's comments
    ReviewStatus = models.CharField(max_length=50)  # Status of the review (Approved, Rejected, etc.)
    ReviewDate = models.DateTimeField()  # Date when the finding was reviewed

    # Meta information for the model
    class Meta:
        db_table = 'audit_findings'  # The table name in the database

    def __str__(self):
        return f"Audit Finding {self.AuditId} - {self.ComplianceId}"

class RiskInstance(models.Model):
    RiskInstanceId = models.AutoField(primary_key=True)
    RiskId = models.IntegerField(null=True)
    IncidentId = models.IntegerField(null=True)
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
   
    # Define choices for RiskStatus
    STATUS_NOT_ASSIGNED = 'Not Assigned'
    STATUS_ASSIGNED = 'Assigned'
    STATUS_APPROVED = 'Approved'
    STATUS_REJECTED = 'Rejected'
   
    RISK_STATUS_CHOICES = [
        (STATUS_NOT_ASSIGNED, 'Not Assigned'),
        (STATUS_ASSIGNED, 'Assigned'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]
   
    # Define choices for MitigationStatus
    MITIGATION_YET_TO_START = 'Yet to Start'
    MITIGATION_IN_PROGRESS = 'Work In Progress'
    MITIGATION_REVISION_REVIEWER = 'Revision Required by Reviewer'
    MITIGATION_REVISION_USER = 'Revision Required by User'
    MITIGATION_COMPLETED = 'Completed'
   
    MITIGATION_STATUS_CHOICES = [
        (MITIGATION_YET_TO_START, 'Yet to Start'),
        (MITIGATION_IN_PROGRESS, 'Work In Progress'),
        (MITIGATION_REVISION_REVIEWER, 'Revision Required by Reviewer'),
        (MITIGATION_REVISION_USER, 'Revision Required by User'),
        (MITIGATION_COMPLETED, 'Completed'),
    ]
   
    # Update the field definitions to use choices
    RiskStatus = models.CharField(max_length=50, choices=RISK_STATUS_CHOICES, default=STATUS_NOT_ASSIGNED, null=True)
    MitigationStatus = models.CharField(max_length=50, choices=MITIGATION_STATUS_CHOICES, default=MITIGATION_YET_TO_START, null=True)
   
    UserId = models.IntegerField(null=True)
    Date = models.DateTimeField(null=True)
    MitigationDueDate = models.DateField(null=True)
    MitigationCompletedDate = models.DateTimeField(null=True)
    ModifiedMitigations = models.JSONField(null=True)
    ReviewerCount = models.IntegerField(null=True)
    RiskFormDetails = models.JSONField(null=True, blank=True)
 
    class Meta:
        db_table = 'risk_instance'  # Ensure Django uses the correct table name in the database
 
    def __str__(self):
        return f"Risk Instance {self.RiskInstanceId}"

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