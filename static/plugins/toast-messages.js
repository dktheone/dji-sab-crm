// toast-messages.js

/**
 * Creates and displays a Bootstrap toast message.
 * @param {string} message - The message to be displayed.
 * @param {string} type - The type of toast (e.g., 'success', 'error', 'info').
 */
function showToast(message, type) {
    let toastClass = '';
    let headerText = '';
  
    // Determine the toast style and header text based on the type
    switch (type) {
      case 'success':
        toastClass = 'bg-success text-white';
        headerText = 'Success';
        break;
        case 'error':
          toastClass = 'bg-danger text-white';
          headerText = 'Error';
          break;
          case 'info':
            toastClass = 'bg-info text-white';
            headerText = 'Info';
            break;
            case 'warning':
                toastClass = 'bg-warning text-dark';
                headerText = 'Info';
                break;
                case 'primary':
                    toastClass = 'bg-primary text-white';
                    headerText = 'Message';
                    break;
                    case 'dark':
                        toastClass = 'bg-dark text-white';
                        headerText = 'Message';
                        break;
      default:
        toastClass = 'bg-secondary text-white';
        headerText = 'Notification';
    }
  
    // Create the toast HTML
    const toastHtml = `
      <div class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-delay="20000" style="width:300px;height:100%;">
        <div class="toast-header h5 ${toastClass}">
          <strong class="mr-auto">${headerText}</strong>
          
          <button type="button" class="ml-2 mb-1 close" data-dismiss="toast" aria-label="Close">
            <span aria-hidden="true">&times;</span>
          </button>
        </div>
        <div class="toast-body ${toastClass} p-10">
        
          ${message}

        </div>
      </div>
    `;
  
    // Append the toast to a container and show it
    // Ensure you have a container with id="toast-container" in your HTML
    $('#toast-container').append(toastHtml);
    $('#toast-container .toast:last-child').toast('show');
  }
  
  /**
   * Displays a success message toast.
   * @param {string} message - The success message.
   */
  function SuccessMSG(message) {    
    showToast(message, 'success');
  }
  
  /**
   * Displays an error message toast.
   * @param {string} message - The error message.
   */
  function ErrorMSG(message) {
    showToast(message, 'error');
  }
  
  /**
   * Displays an info message toast.
   * @param {string} message - The info message.
   */
  function InfoMSG(message) {
    showToast(message, 'info');
  }
  /**
   * Displays an info message toast.
   * @param {string} message - The info message.
   */
  function WarningMSG(message) {
    showToast(message, 'warning');
  }
  /**
   * Displays an info message toast.
   * @param {string} message - The info message.
   */
  function PrimaryMSG(message) {
    showToast(message, 'primary');
  }
  /**
   * Displays an info message toast.
   * @param {string} message - The info message.
   */
  function DarkMSG(message) {
    showToast(message, 'dark');
  }