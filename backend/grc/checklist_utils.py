from django.db import connection
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def update_lastchecklistitem_verified(audit_id):
    """
    Update lastchecklistitemverified table when an audit is approved and completed.
    This function:
    1. Gets all compliance items from audit_findings for the given audit
    2. For each compliance, gets the associated policy hierarchy
    3. Updates or inserts records in lastchecklistitemverified table
    4. Prints records where check value is "0" or "1"
    """
    try:
        current_datetime = timezone.now()
        current_date = current_datetime.date()
        current_time = current_datetime.time()

        with connection.cursor() as cursor:
            # First get all the audit findings for this audit
            cursor.execute("""
                SELECT 
                    af.ComplianceId,
                    af.UserId,
                    af.`Check`,
                    af.Comments,
                    c.SubPolicyId,
                    sp.PolicyId,
                    p.FrameworkId
                FROM 
                    audit_findings af
                JOIN 
                    compliance c ON af.ComplianceId = c.ComplianceId
                JOIN 
                    subpolicies sp ON c.SubPolicyId = sp.SubPolicyId
                JOIN 
                    policies p ON sp.PolicyId = p.PolicyId
                WHERE 
                    af.AuditId = %s
            """, [audit_id])
            
            findings = cursor.fetchall()
            
            for finding in findings:
                compliance_id, user_id, check_value, comments, subpolicy_id, policy_id, framework_id = finding
                
                # Check if a record already exists for this compliance
                cursor.execute("""
                    SELECT COUNT(*), Count 
                    FROM lastchecklistitemverified 
                    WHERE ComplianceId = %s
                """, [compliance_id])
                
                result = cursor.fetchone()
                exists = result[0] > 0
                current_count = result[1] if exists else 0
                
                # Increment count if check value is "0" or "1"
                new_count = current_count
                if check_value in ["0", "1"]:
                    new_count = current_count + 1
                
                if exists:
                    # Update existing record
                    cursor.execute("""
                        UPDATE lastchecklistitemverified
                        SET 
                            SubPolicyId = %s,
                            PolicyId = %s,
                            FrameworkId = %s,
                            Date = %s,
                            Time = %s,
                            User = %s,
                            Complied = %s,
                            Comments = %s,
                            Count = %s
                        WHERE ComplianceId = %s
                    """, [
                        subpolicy_id,
                        policy_id,
                        framework_id,
                        current_date,
                        current_time,
                        user_id,
                        check_value,
                        comments,
                        new_count,
                        compliance_id
                    ])
                else:
                    # Insert new record
                    cursor.execute("""
                        INSERT INTO lastchecklistitemverified (
                            ComplianceId,
                            SubPolicyId,
                            PolicyId,
                            FrameworkId,
                            Date,
                            Time,
                            User,
                            Complied,
                            Comments,
                            Count
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, [
                        compliance_id,
                        subpolicy_id,
                        policy_id,
                        framework_id,
                        current_date,
                        current_time,
                        user_id,
                        check_value,
                        comments,
                        new_count
                    ])
                
                # Print record if check value is "0" or "1"
                if check_value in ["0", "1"]:
                    cursor.execute("""
                        SELECT * FROM lastchecklistitemverified
                        WHERE ComplianceId = %s
                    """, [compliance_id])
                    record = cursor.fetchone()
                    print(f"Updated/Inserted record for ComplianceId {compliance_id}: {record}")
        
        return True
    except Exception as e:
        logger.error(f"Error in update_lastchecklistitem_verified: {str(e)}")
        print(f"ERROR: Failed to update lastchecklistitemverified table: {str(e)}")
        return False 