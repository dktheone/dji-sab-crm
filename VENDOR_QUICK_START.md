# Vendor Module - Quick Start Guide

## ⚡ Run These Commands Now

Your vendor module is fully coded and ready! You just need to create the database tables.

### Step 1: Stop the Server
In your terminal where `runserver` is running:
- Press `Ctrl+C` to stop the server

### Step 2: Run Migrations

```powershell
# Make sure you're in the project directory
cd d:\Projects\SAB_CRM\crm_sab

# Activate virtual environment (if not already active)
.\env_sab\Scripts\Activate.ps1

# Create migration files for vendors app
python manage.py makemigrations vendors

# Apply the migrations to create database tables
python manage.py migrate

# Restart the server
python manage.py runserver 0.0.0.0:8000
```

### Step 3: Access the Module
1. Open your browser and go to: `http://localhost:8000`
2. Login with your credentials
3. Look for **VENDORS** in the left sidebar menu
4. Click **"Add New Vendor"** to create your first vendor!

---

## 🎯 Quick Test Checklist

After running migrations, test these features:

- [ ] **Create Vendor**: Add a new vendor with basic information
- [ ] **Add Registration ID**: Add a PAN Card or GST number
- [ ] **Add Payment Info**: Configure payment mode and bank details
- [ ] **Upload Document**: Upload a quotation or contract (PDF/Image)
- [ ] **View Vendor List**: See all vendors in the list with filters
- [ ] **Edit Vendor**: Modify vendor information
- [ ] **Search**: Search for vendors by name or code
- [ ] **Delete Vendor**: Delete a test vendor (with confirmation)

---

## 📋 What You Get

### Menu Items (in sidebar)
```
VENDORS
├── Vendors List
└── Add New Vendor
```

### URLs Available
```
/vendors/                          → List all vendors
/vendors/create/                   → Create new vendor
/vendors/<id>/                     → View vendor details
/vendors/<id>/update/              → Edit vendor
/vendors/<id>/delete/              → Delete vendor
/vendors/<id>/payment/             → Payment information
/vendors/<id>/registration-ids/    → API: Get registration IDs
/vendors/<id>/documents/           → API: Get documents
```

### Database Tables Created
```
- vendors                    → Main vendor table
- vendor_registration_ids    → Registration IDs (PAN, GST, etc.)
- vendor_payment_info        → Payment and bank details
- vendor_documents           → Uploaded documents
```

---

## 🐛 If Something Goes Wrong

### Migration Errors
```powershell
# View current migration status
python manage.py showmigrations vendors

# If vendors app not found, check:
# - Is 'apps.vendors' in INSTALLED_APPS? (it should be!)
# - Does apps/vendors/__init__.py exist?

# Force create migrations
python manage.py makemigrations vendors --name initial_vendor_models
```

### Menu Not Showing
- Clear browser cache (Ctrl+Shift+Delete)
- Check if you're logged in as admin or HR user
- Refresh the page (F5)

### Database Already Exists Error
```powershell
# If tables already exist, skip vendor migration:
python manage.py migrate --fake vendors

# Or drop and recreate (WARNING: loses data):
# Delete db.sqlite3 and run: python manage.py migrate
```

### File Upload Not Working
- Check `MEDIA_URL` and `MEDIA_ROOT` in settings.py (already configured)
- Ensure `media` folder exists in project root
- Check file size is under 5MB

---

## 💡 Usage Tips

1. **Always set a Primary Registration ID** - This is used for official documentation
2. **Payment Schedule Examples**:
   - 7 Days = Payment in 7 days
   - 2 Weeks = Payment in 2 weeks  
   - 1 Month = Payment in 1 month
3. **Bank Details** - Only required for Cheque/Net Banking/Bank Transfer modes
4. **Documento Upload** - Supports PDF, Images (JPG/PNG), and Word docs
5. **Status Management**:
   - Active = Currently working vendor
   - Inactive = Temporarily not working
   - Suspended = Performance issues
   - Blacklisted = Do not use

---

## 📞 Need Help?

All code is complete and follows your existing CRM patterns. If you encounter any issues:

1. Check the walkthrough.md for detailed documentation
2. Review error messages carefully
3. Ensure migrations ran successfully
4. Verify server restarted after migrations

---

## ✅ Success Indicators

You'll know everything works when:
- ✅ Migrations complete without errors
- ✅ VENDORS menu appears in sidebar
- ✅ You can create a vendor successfully
- ✅ Registration IDs can be added via modal
- ✅ Documents can be uploaded
- ✅ Vendor list shows all vendors with filters working

**Happy vendor management! 🚀**
