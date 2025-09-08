function load_designation(action_url) {
    console.log('action_url', action_url)
    // Initialize DataTable
    $('#designationTable').DataTable({
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
        // console.log('id', id, 'name', name)
        $('#editDesignationId').val(id);
        $('#editDesignationName').val(name);
        $('#editDesignationErrors').empty();
    });

    // Populate delete modal
    $('.delete-btn').click(function() {
        var id = $(this).data('id');
        var name = $(this).data('name');
        $('#deleteDesignationId').val(id);
        $('#deleteDesignationName').text(name);
    });

    // Handle add form submission
    $('#adddesignationModal').submit(function(e) {
        e.preventDefault();
        
        // Serialize the form data
        const formData = $(this).serialize();
        
        // Log the serialized data to the console for debugging
        console.log("Serialized form data:", formData);
        alert("View Serialized form data")
        $.ajax({
            url: action_url,
            type: 'POST',
            data: formData, // Use the new variable
            
            success: function(response) {
                console.log("Success Response:", response, action_url);
                if (response.status === 'success') {
                    SuccessMSG(response.message);
                    // location.reload(); 
                } else {
                    $('#addDesignationErrors').text(response.errors.designation_name || 'An error occurred');
                    $('#addDesignationErrors').show();
                }
            },
            
            error: function(jqXHR, textStatus, errorThrown) {
                console.log("AJAX Error:", jqXHR, textStatus, errorThrown);
                $('#addDesignationErrors').text('An error occurred');
                $('#addDesignationErrors').show();
            }
        });
    });

    
    $('#editdesignationModal').submit(function(e) {
        e.preventDefault();
    
        const form = e.target;
        const formData = new FormData(form);
    
        fetch(action_url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': formData.get('csrfmiddlewaretoken'),
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            const responseDiv = document.getElementById('responseMessage');
            if (data.status === 'success') {
                responseDiv.innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            } else {
                responseDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
                console.log(data.errors);
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
    
}

