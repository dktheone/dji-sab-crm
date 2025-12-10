"""
Data Migration Script:  Convert EmployeeAdjustment to Master-Transaction Architecture

Run this after creating the new models and running migrations.
This script migrates existing adjustment data to the new structure.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crm_sab.settings')
django.setup()

from apps.emp.models import (
    Employee, EmployeeAdjustment,
    EmployeeAdjustmentMaster, EmployeeAdjustmentTransaction
)
from decimal import Decimal
from django.utils import timezone

def migrate_adjustments():
    """Migrate existing adjustments to new Master-Transaction architecture"""
    
    print("Starting adjustment migration...")
    print("=" * 60)
    
    old_adjustments = EmployeeAdjustment.objects.all()
    total = old_adjustments.count()
    
    print(f"Found {total} adjustments to migrate")
    
    migrated = 0
    errors = []
    
    for adj in old_adjustments:
        try:
            # Create Master record
            master = EmployeeAdjustmentMaster.objects.create(
                employee=adj.employee,
                adjustment_type=adj.adjustment_type,
                total_amount=adj.amount,
                date_issued=adj.date,
                description=adj.remarks or f"Migrated from old adjustment #{adj.id}",
                created_by=adj.created_by,
                created_at=adj.created_at
            )
            
            # Handle different statuses
            if adj.status == 'Pending':
                # No transactions yet, just master
                master.status = 'Active'
                master.save()
                print(f"✓ Migrated Pending #{adj.id} → Master #{master.id}")
            
            elif adj.status == 'Partial':
                # Create transaction for settled amount
                settled = adj.amount - adj.remaining_amount
                
                # Create transaction (estimate month as current if not available)
                EmployeeAdjustmentTransaction.objects.create(
                    adjustment_master=master,
                    employee=adj.employee,
                    settlement_amount=settled,
                    salary_month=timezone.now().month,
                    salary_year=timezone.now().year,
                    transaction_type='Partial',
                    remarks=f"Migrated partial settlement from old adjustment #{adj.id}",
                    created_by=adj.created_by
                )
                
                master.status = 'Active'  # Still has outstanding
                master.save()
                print(f"✓ Migrated Partial #{adj.id} → Master #{master.id} + Transaction (₹{settled})")
            
            elif adj.status == 'Cleared':
                # Create full settlement transaction
                EmployeeAdjustmentTransaction.objects.create(
                    adjustment_master=master,
                    employee=adj.employee,
                    settlement_amount=adj.amount,
                    salary_month=timezone.now().month,
                    salary_year=timezone.now().year,
                    transaction_type='Full',
                    remarks=f"Migrated full settlement from old adjustment #{adj.id}",
                    created_by=adj.created_by
                )
                
                master.status = 'Closed'
                master.save()
                print(f"✓ Migrated Cleared #{adj.id} → Master #{master.id} + Full Transaction")
            
            migrated += 1
            
        except Exception as e:
            errors.append(f"Error migrating #{adj.id}: {str(e)}")
            print(f"✗ Error migrating #{adj.id}: {str(e)}")
    
    print("=" * 60)
    print(f"\nMigration Summary:")
    print(f"Total: {total}")
    print(f"Migrated: {migrated}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print("\nErrors:")
        for error in errors:
            print(f"  - {error}")
    
    # Verification
    print("\n" + "=" * 60)
    print("Verification:")
    print(f"EmployeeAdjustmentMaster count: {EmployeeAdjustmentMaster.objects.count()}")
    print(f"EmployeeAdjustmentTransaction count: {EmployeeAdjustmentTransaction.objects.count()}")
    
    # Show sample
    print("\nSample migrated data:")
    for master in EmployeeAdjustmentMaster.objects.all()[:5]:
        print(f"\nMaster #{master.id}: {master.adjustment_type} ₹{master.total_amount}")
        print(f"  Status: {master.status}")
        print(f"  Settled: ₹{master.settled_amount}")
        print(f"  Outstanding: ₹{master.outstanding_amount}")
        for trans in master.adjustment_transactions.all():
            print(f"  → Transaction: ₹{trans.settlement_amount} ({trans.salary_month}/{trans.salary_year})")

if __name__ == '__main__':
    confirm = input("This will migrate all EmployeeAdjustment data. Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        migrate_adjustments()
        print("\n✓ Migration complete!")
    else:
        print("Migration cancelled.")
