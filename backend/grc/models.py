from django.db import models

class Risk(models.Model):
    RiskId = models.AutoField(primary_key=True)  # Primary Key
    ComplianceId = models.IntegerField(null=True)
    Criticality = models.CharField(max_length=100, null=True)
    PossibleDamage = models.TextField(null=True)
    Category = models.CharField(max_length=100, null=True)
    RiskDescription = models.TextField(null=True)
    RiskLikelihood = models.CharField(max_length=50, null=True)
    RiskImpact = models.CharField(max_length=50, null=True)
    RiskExposureRating = models.CharField(max_length=50, null=True)
    RiskPriority = models.CharField(max_length=50, null=True)
    RiskMitigation = models.CharField(max_length=100, null=True)

    class Meta:
        db_table = 'risk'  # Ensure Django uses the correct table in the database

    def __str__(self):
        return f"Risk {self.RiskId}"


class Incident(models.Model):
    IncidentId = models.AutoField(primary_key=True)
    IncidentTitle = models.CharField(max_length=255, null=True)
    Description = models.TextField(null=True)
    Mitigation = models.TextField(null=True)
    AuditId = models.IntegerField(null=True)
    ComplianceId = models.IntegerField(null=True)
    Date = models.DateField(null=True)
    Time = models.TimeField(null=True)
    UserId = models.IntegerField(null=True)
    Origin = models.CharField(max_length=50, null=True)
    Comments = models.TextField(null=True)
    RiskCategory = models.CharField(max_length=100, null=True)
    RiskPriority = models.CharField(max_length=20, null=True)
    Attachments = models.TextField(null=True)
    CreatedAt = models.DateTimeField(null=True)
    Status = models.CharField(max_length=45, null=True)
    IdentifiedAt = models.DateTimeField(null=True)

    class Meta:
        db_table = 'incidents'  # match the MySQL table name


class Compliance(models.Model):
    SubPolicyId = models.IntegerField()  # Not primary
    ComplianceId = models.AutoField(primary_key=True)  # Only ONE primary key allowed
    ComplianceItemDescription = models.TextField(null=True)
    IsRisk = models.BooleanField(null=True)
    PossibleDamage = models.TextField(null=True)
    Criticality = models.CharField(max_length=50, null=True)
    MandatoryOptional = models.CharField(max_length=50, null=True)
    ManualAutomatic = models.CharField(max_length=50, null=True)
    Impact = models.CharField(max_length=50, null=True)
    Probability = models.CharField(max_length=50, null=True)

    class Meta:
        db_table = 'compliance'
        managed = False  # since you're using an existing table
        unique_together = (('SubPolicyId', 'ComplianceId'),)  # Composite uniqueness


class RiskInstance(models.Model):
    RiskInstanceId = models.AutoField(primary_key=True)
    RiskId = models.IntegerField(null=True)
    IncidentId = models.IntegerField(null=True)
    Criticality = models.CharField(max_length=100, null=True)
    PossibleDamage = models.TextField(null=True)
    Category = models.CharField(max_length=100, null=True)
    Appetite = models.CharField(max_length=100, null=True)
    RiskDescription = models.TextField(null=True)
    RiskLikelihood = models.FloatField(null=True)
    RiskImpact = models.FloatField(null=True)
    RiskExposureRating = models.FloatField(null=True)
    RiskPriority = models.CharField(max_length=50, null=True)
    RiskResponseType = models.CharField(max_length=100, null=True)
    RiskResponseDescription = models.TextField(null=True)
    RiskMitigation = models.TextField(null=True)
    RiskOwner = models.CharField(max_length=255, null=True)
    RiskStatus = models.CharField(max_length=50, null=True)
    UserId = models.IntegerField(null=True)
    Date = models.DateField(null=True)

    class Meta:
        db_table = 'risk_instance'  # Ensure Django uses the correct table name in the database

    def __str__(self):
        return f"Risk Instance {self.RiskInstanceId}"
