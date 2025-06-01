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