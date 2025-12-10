// employee_additional.js
// Handles add, edit, and delete logic for Education, Experience, and Family forms

$(document).ready(function() {
    // Initialize Select2 for all select elements with custom_select class
    $('.custom_select').select2({
        placeholder: "Select an option",
        allowClear: true,
        width: '100%'
    });

    // Function to populate modal form fields
    function populateModal(formId, data) {
        $(formId + ' input, ' + formId + ' select, ' + formId + ' textarea').each(function() {
            var name = $(this).attr('name');
            if (name && data[name]) {
                if ($(this).is('select')) {
                    $(this).val(data[name]).trigger('change');
                } else {
                    $(this).val(data[name]);
                }
            }
        });
    }

    // Function to reset modal form
    function resetModal(formId) {
        $(formId)[0].reset();
        $(formId + ' select').val('').trigger('change');
        $(formId + ' .invalid-feedback').remove();
        $(formId + ' .form-control').removeClass('is-invalid');
    }

    // Function to display form errors
    function displayErrors(formId, errors) {
        $(formId + ' .invalid-feedback').remove();
        $(formId + ' .form-control').removeClass('is-invalid');
        for (var field in errors) {
            var fieldElement = $(formId + ' [name="' + field + '"]');
            fieldElement.addClass('is-invalid');
            fieldElement.after('<div class="invalid-feedback">' + errors[field] + '</div>');
        }
    }

    // Education Modal Handling
    $('#educationModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var action = button.data('action');
        $('#educationAction').val(action === 'add' ? 'add_education' : 'edit_education');
        
        if (action === 'edit') {
            var row = button.closest('tr');
            var id = row.data('id');
            $('#educationId').val(id);
            var data = {
                degree: row.find('td:eq(0)').text(),
                institution: row.find('td:eq(1)').text(),
                passing_year: row.find('td:eq(2)').text(),
                percentage: row.find('td:eq(3)').text()
            };
            populateModal('#educationForm', data);
        } else {
            resetModal('#educationForm');
            $('#educationId').val('');
        }
    });

    $('#educationForm').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: '',
            type: 'POST',
            data: new FormData(this),
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: response.message,
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    displayErrors('#educationForm', response.errors);
                }
            },
            error: function(response) {
                displayErrors('#educationForm', response.responseJSON.errors);
            }
        });
    });

    $('#educationTable').on('click', '.delete-btn', function() {
        var row = $(this).closest('tr');
        var id = row.data('id');
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.post('', {
                    action: 'delete_education',
                    id: id,
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                }, function(response) {
                    if (response.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Deleted',
                            text: response.message,
                            timer: 1500,
                            showConfirmButton: false
                        }).then(() => {
                            row.remove();
                        });
                    }
                }).fail(function(response) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to delete education record.'
                    });
                });
            }
        });
    });

    // Experience Modal Handling
    $('#experienceModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var action = button.data('action');
        $('#experienceAction').val(action === 'add' ? 'add_experience' : 'edit_experience');
        
        if (action === 'edit') {
            var row = button.closest('tr');
            console.log(row);
            var id = row.data('id');
            $('#experienceId').val(id);
            var data = {
                company_name: row.find('td:eq(0)').text(),
                job_title: row.find('td:eq(1)').text(),
                start_date: row.find('td:eq(2)').data('start-date') || '',
                end_date: row.find('td:eq(3)').data('end-date') || '',
                gross_salary: row.find('td:eq(4)').text() !== '-' ? row.find('td:eq(4)').text() : '',
                responsibilities: row.find('td:eq(5)').text() !== '-' ? row.find('td:eq(5)').text() : '',
                reason_for_leaving: row.find('td:eq(6)').text() !== '-' ? row.find('td:eq(6)').text() : ''
                // Note: responsibilities and reason_for_leaving are not in table for simplicity
            };
            populateModal('#experienceForm', data);
        } else {
            resetModal('#experienceForm');
            $('#experienceId').val('');
        }
    });

    $('#experienceForm').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: '',
            type: 'POST',
            data: new FormData(this),
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: response.message,
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    displayErrors('#experienceForm', response.errors);
                }
            },
            error: function(response) {
                displayErrors('#experienceForm', response.responseJSON.errors);
            }
        });
    });

    $('#experienceTable').on('click', '.delete-btn', function() {
        var row = $(this).closest('tr');
        var id = row.data('id');
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.post('', {
                    action: 'delete_experience',
                    id: id,
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                }, function(response) {
                    if (response.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Deleted',
                            text: response.message,
                            timer: 1500,
                            showConfirmButton: false
                        }).then(() => {
                            row.remove();
                        });
                    }
                }).fail(function(response) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to delete experience record.'
                    });
                });
            }
        });
    });

    // Family Modal Handling
    $('#familyModal').on('show.bs.modal', function(event) {
        var button = $(event.relatedTarget);
        var action = button.data('action');
        $('#familyAction').val(action === 'add' ? 'add_family' : 'edit_family');
        
        if (action === 'edit') {
            var row = button.closest('tr');
            var id = row.data('id');
            $('#familyId').val(id);
            var data = {
                name: row.find('td:eq(0)').text(),
                relationship: row.find('td:eq(1)').text(),
                dob: row.find('td:eq(2)').text() !== '-' ? row.find('td:eq(2)').text() : '',
                occupation: row.find('td:eq(3)').text() !== '-' ? row.find('td:eq(3)').text() : '',
                contact_no: row.find('td:eq(4)').text() !== '-' ? row.find('td:eq(4)').text() : '',
                aadhaar_no: row.find('td:eq(5)').text() !== '-' ? row.find('td:eq(5)').text() : '',
                address: row.find('td:eq(6)').text() !== '-' ? row.find('td:eq(6)').text() : ''
                // Note: address and aadhaar_no are not in table for simplicity
            };
            populateModal('#familyForm', data);
        } else {
            resetModal('#familyForm');
            $('#familyId').val('');
        }
    });

    $('#familyForm').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: '',
            type: 'POST',
            data: new FormData(this),
            processData: false,
            contentType: false,
            success: function(response) {
                if (response.status === 'success') {
                    Swal.fire({
                        icon: 'success',
                        title: 'Success',
                        text: response.message,
                        timer: 1500,
                        showConfirmButton: false
                    }).then(() => {
                        location.reload();
                    });
                } else {
                    displayErrors('#familyForm', response.errors);
                }
            },
            error: function(response) {
                displayErrors('#familyForm', response.responseJSON.errors);
            }
        });
    });

    $('#familyTable').on('click', '.delete-btn', function() {
        var row = $(this).closest('tr');
        var id = row.data('id');
        Swal.fire({
            title: 'Are you sure?',
            text: "You won't be able to revert this!",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Yes, delete it!'
        }).then((result) => {
            if (result.isConfirmed) {
                $.post('', {
                    action: 'delete_family',
                    id: id,
                    csrfmiddlewaretoken: $('[name=csrfmiddlewaretoken]').val()
                }, function(response) {
                    if (response.status === 'success') {
                        Swal.fire({
                            icon: 'success',
                            title: 'Deleted',
                            text: response.message,
                            timer: 1500,
                            showConfirmButton: false
                        }).then(() => {
                            row.remove();
                        });
                    }
                }).fail(function(response) {
                    Swal.fire({
                        icon: 'error',
                        title: 'Error',
                        text: 'Failed to delete family record.'
                    });
                });
            }
        });
    });
});