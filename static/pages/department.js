function load_dept(action_url) {
    // Initialize DataTable
    $('#departmentTable').DataTable({
        "paging": false,
        "lengthChange": true,
        "searching": true,
        "ordering": true,
        "info": true,
        "autoWidth": false,
        "responsive": true,
    });

    // Populate edit modal
    $('.edit-btn').click(function() {
        var id = $(this).data('id');
        var name = $(this).data('name');           
        $('#editDepartmentId').val(id);
        $('#editDepartmentName').val(name);
        $('#editDepartmentErrors').empty();
    });

    // Populate delete modal
    $('.delete-btn').click(function() {
        var id = $(this).data('id');
        var name = $(this).data('name');
        $('#deleteDepartmentId').val(id);
        $('#deleteDepartmentName').text(name);
    });

    // Handle add form submission
    $('#addDepartmentForm').submit(function(e) {
        e.preventDefault();
        
        // Serialize the form data
        const formData = $(this).serialize();
        
        // Log the serialized data to the console for debugging
        console.log("Serialized form data:", formData);

        $.ajax({
            url: action_url,
            type: 'POST',
            data: formData, // Use the new variable
            
            success: function(response) {
                console.log("Success Response:", response);
                if (response.status === 'success') {
                    SuccessMSG(response.message);
                    location.reload(); 
                } else {
                    $('#addDepartmentErrors').text(response.errors.department_name || 'An error occurred');
                    $('#addDepartmentErrors').show();
                }
            },
            
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("AJAX Error:", jqXHR, textStatus, errorThrown);
                $('#addDepartmentErrors').text('An error occurred');
                $('#addDepartmentErrors').show();
            }
        });
    });

    // Handle edit form submission
    $('#editDepartmentForm').submit(function(e) {
        e.preventDefault();
        $.ajax({
            url: action_url,
            type: 'POST',
            data: $(this).serialize(),
            success: function(response) {
                console.log(response)
                if (response.status === 'success') {
                    console.log(response)
                    SuccessMSG(response.message);
                    location.reload();
                } else {
                    $('#editDepartmentErrors').text(response.errors.department_name || 'An error occurred');
                    $('#editDepartmentErrors').show();
                }
            },
            error: function() {
                $('#editDepartmentErrors').text('An error occurred');
                $('#editDepartmentErrors').show();
            }
        });
    });

    
}

