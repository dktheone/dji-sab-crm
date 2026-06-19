from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    Employee, EmploymentHistory, EmployeeStatusLog,
    EmployeeEducation, EmployeeFamily, EmployeeUpload,
    EmployeeActivityLog, EmployeeSalaryMaster,
    EmployeeAdjustmentMaster, EmployeeAdjustmentTransaction,
    EmployeeSalaryTransaction, Leave, DisciplinaryAction,
    TrainingRecord, EmployeePerformanceReview
)
from .utils import log_employee_activity
from django.contrib.auth.models import User

@receiver(post_save, sender=Employee)
def log_employee_save(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance,
            category=EmployeeActivityLog.ActivityCategory.PROFILE,
            action="Profile Created",
            remark="Employee profile created."
        )
    else:
        log_employee_activity(
            employee=instance,
            category=EmployeeActivityLog.ActivityCategory.PROFILE,
            action="Profile Updated",
            remark="Employee profile updated."
        )

@receiver(post_save, sender=EmploymentHistory)
def log_employment_history(sender, instance, created, **kwargs):
    if created:
        if instance.exit_date:
            reason = instance.reason_for_exit or "N/A"
            log_employee_activity(
                employee=instance.employee,
                category=EmployeeActivityLog.ActivityCategory.STATUS,
                action="Offboarding",
                remark=f"Employee offboarded (Legacy record). Exit date: {instance.exit_date}. Reason: {reason}"
            )
        else:
            log_employee_activity(
                employee=instance.employee,
                category=EmployeeActivityLog.ActivityCategory.STATUS,
                action="Onboarding",
                remark=f"Employee onboarded. Joining date: {instance.joining_date}"
            )
    elif instance.exit_date:
        reason = instance.reason_for_exit or "N/A"
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.STATUS,
            action="Offboarding",
            remark=f"Employee offboarded. Exit date: {instance.exit_date}. Reason: {reason}"
        )

@receiver(post_save, sender=EmployeeStatusLog)
def log_employee_status_change(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.STATUS,
            action="Status Change",
            remark=f"Employee status changed from {instance.old_status or 'None'} to {instance.new_status}."
        )

@receiver(post_save, sender=EmployeeEducation)
def log_employee_education(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.ACADEMICS,
            action="Education Added",
            remark=f"Education profile added: {instance.degree} from {instance.institution}"
        )

@receiver(post_save, sender=EmployeeFamily)
def log_employee_family(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.ACADEMICS,
            action="Family Member Added",
            remark=f"Family member added: {instance.name} ({instance.relationship})"
        )

@receiver(post_save, sender=EmployeeUpload)
def log_employee_upload(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.DOCUMENTS,
            action="Document Uploaded",
            remark=f"Document uploaded: {instance.document_type}"
        )
    else:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.DOCUMENTS,
            action="Document Status Updated",
            remark=f"Document {instance.document_type} status updated to: {instance.status}"
        )

@receiver(post_save, sender=EmployeeSalaryMaster)
def log_salary_master(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.SALARY_MASTER,
            action="Salary Master Created",
            remark=f"Salary master created for ₹{instance.salary_amount} effective from {instance.effective_from}"
        )
    else:
        if instance.status == 'Inactive':
            log_employee_activity(
                employee=instance.employee,
                category=EmployeeActivityLog.ActivityCategory.SALARY_MASTER,
                action="Salary Master Deactivated",
                remark="Salary master deactivated."
            )
        else:
            log_employee_activity(
                employee=instance.employee,
                category=EmployeeActivityLog.ActivityCategory.SALARY_MASTER,
                action="Salary Master Modified",
                remark=f"Salary master modified to ₹{instance.salary_amount} effective from {instance.effective_from}"
            )

@receiver(post_save, sender=EmployeeAdjustmentMaster)
def log_adjustment_master(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.ADJUSTMENTS,
            action="Adjustment Added",
            remark=f"Adjustment - {instance.adjustment_type} added: ₹{instance.total_amount}."
        )
    else:
        if instance.status == 'Closed':
            log_employee_activity(
                employee=instance.employee,
                category=EmployeeActivityLog.ActivityCategory.ADJUSTMENTS,
                action="Adjustment Cleared",
                remark=f"Adjustment - {instance.adjustment_type} fully cleared."
            )

@receiver(post_save, sender=EmployeeAdjustmentTransaction)
def log_adjustment_transaction(sender, instance, created, **kwargs):
    if created:
        adj = instance.adjustment_master
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.ADJUSTMENTS,
            action="Adjustment Settled",
            remark=f"Adjustment - {adj.adjustment_type} partially settled. ₹{adj.cleared_amount} cleared, ₹{adj.outstanding_amount} remaining."
        )

@receiver(post_save, sender=EmployeeSalaryTransaction)
def log_salary_transaction(sender, instance, created, **kwargs):
    if created or instance.status == 'Prepared':
        if created:
            log_employee_activity(
                employee=instance.employee,
                category=EmployeeActivityLog.ActivityCategory.PAYROLL,
                action="Salary Prepared",
                remark=f"Salary created for Month/Year {instance.month:02d}-{instance.year}. Net amount: ₹{instance.net_salary}"
            )
    else:
        if instance.status == 'Paid':
            log_employee_activity(
                employee=instance.employee,
                category=EmployeeActivityLog.ActivityCategory.PAYROLL,
                action="Salary Disbursed",
                remark=f"Salary disbursed for Month/Year {instance.month:02d}-{instance.year}."
            )

@receiver(post_save, sender=Leave)
def log_leave(sender, instance, created, **kwargs):
    if not created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.HR,
            action=f"Leave {instance.status}",
            remark=f"Leave {instance.status}: {instance.leave_type} from {instance.from_date} to {instance.to_date}"
        )
    else:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.HR,
            action="Leave Applied",
            remark=f"Leave Applied: {instance.leave_type} from {instance.from_date} to {instance.to_date}"
        )

@receiver(post_save, sender=DisciplinaryAction)
def log_disciplinary(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.HR,
            action="Disciplinary Action Issued",
            remark=f"Disciplinary action - {instance.action_type} issued. Reason: {instance.reason}"
        )

@receiver(post_save, sender=TrainingRecord)
def log_training(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.HR,
            action="Training Recorded",
            remark=f"Training recorded: {instance.training_topic}"
        )

@receiver(post_save, sender=EmployeePerformanceReview)
def log_performance(sender, instance, created, **kwargs):
    if created:
        log_employee_activity(
            employee=instance.employee,
            category=EmployeeActivityLog.ActivityCategory.HR,
            action="Performance Review Added",
            remark=f"Performance review added for {instance.review_month:02d}-{instance.review_year}. Score: {instance.performance_rating}"
        )

@receiver(post_save, sender=User)
def log_user_auth(sender, instance, created, **kwargs):
    # Try to find the associated employee
    try:
        employee = instance.employee_profile
    except Exception:
        employee = None

    if employee:
        if created:
            log_employee_activity(
                employee=employee,
                category=EmployeeActivityLog.ActivityCategory.AUTH,
                action="Login Created",
                remark=f"Login credentials created. Username: {instance.username}"
            )
        else:
            # We can't perfectly know if password changed via just post_save without tracking old value,
            # but usually User is only saved on password reset or profile edit.
            # We'll log it conditionally if we can't tell, or just rely on explicitly logging it in the view.
            pass
